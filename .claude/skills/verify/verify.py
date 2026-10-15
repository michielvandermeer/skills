"""Drive this checkout's skills the way a user does: as a plugin in a headless Claude Code session, in a scratch repo.

  python .claude/skills/verify/verify.py doctor                       # is this checkout worth driving?
  python .claude/skills/verify/verify.py new setup-local              # scratch repo + evidence folder; prints the run dir
  python .claude/skills/verify/verify.py turn <run> "/skills:setup local"
  python .claude/skills/verify/verify.py turn <run> "yes"             # later turns resume the same session
  python .claude/skills/verify/verify.py cleanup <run>                # deletes the scratch repo, keeps the evidence

Every turn runs `claude -p` with --plugin-dir set to this checkout (or --plugin-dir at `new`), so the working tree,
uncommitted edits included, is the plugin under test and replaces the installed skills@mvdmio for that session. No MCP
server loads, pushes and GitHub writes are denied, and the scratch repo has no remote. Evidence goes to
.claude/skills/verify/runs/<run>/ and survives cleanup. Python 3 standard library only."""
import argparse
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import uuid
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]  # the skills checkout
RUNS = HERE / "runs"
SCRATCH_PREFIX = "skills-verify-"
CONFIG = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")
DENIED = ["Bash(git push *)", "Bash(gh issue create *)", "Bash(gh issue edit *)", "Bash(gh issue close *)",
          "Bash(gh issue comment *)", "Bash(gh pr *)", "Bash(gh label *)", "Bash(gh release *)", "Bash(gh repo *)"]


def sh(argv, cwd=None, check=True):
    r = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       stdin=subprocess.DEVNULL)
    if check and r.returncode:
        raise SystemExit(f"{' '.join(map(str, argv))} failed ({r.returncode}):\n{r.stderr or r.stdout}")
    return r.stdout.strip()


def norm(p):
    return os.path.normcase(os.path.realpath(p))


def claude_argv(prompt, plugin_dir, mcp_file, session_id, resume, model, effort, budget):
    argv = [shutil.which("claude") or "claude", "-p", prompt, "--plugin-dir", str(plugin_dir),
            "--permission-mode", "bypassPermissions", "--strict-mcp-config", "--mcp-config", str(mcp_file),
            "--output-format", "stream-json", "--verbose", "--max-budget-usd", str(budget)]
    argv += ["--resume", session_id] if resume else ["--session-id", session_id]
    if model:
        argv += ["--model", model]
    if effort:
        argv += ["--effort", effort]
    return argv + ["--disallowedTools", *DENIED]  # variadic, so it goes last


def read_stream(path):
    events = []
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            events.append(json.loads(line))
        except ValueError:
            pass
    return events


def plugin_check(init, plugin_dir):
    """'ok' when the plugin named skills that loaded is plugin_dir and nothing else; otherwise what went wrong."""
    plugins = [p for p in (init or {}).get("plugins") or [] if isinstance(p, dict)]
    named = [p for p in plugins if p.get("name") == "skills"]
    if not init:
        return "FAIL: no init event"
    if len(named) != 1:
        return f"FAIL: {len(named)} plugins named skills loaded: {named}"
    if norm(named[0].get("path", "")) != norm(plugin_dir):
        return f"FAIL: skills loaded from {named[0].get('path')}, not {plugin_dir}"
    return "ok"


def session_loads(transcript):
    """Slash commands the user typed and the folders skill bodies loaded from, over the whole session so far.
    Neither shows in the stream: a slash command expands before the stream starts."""
    commands, bases = [], []
    if not transcript or not Path(transcript).exists():
        return commands, bases
    for e in read_stream(transcript):
        content = (e.get("message") or {}).get("content") if e.get("type") == "user" else None
        texts = [content] if isinstance(content, str) else [c.get("text", "") for c in content or [] if isinstance(c, dict)]
        for text in texts:
            if "<command-name>" in text:
                name = text.split("<command-name>", 1)[1].split("</command-name>", 1)[0]
                args = text.split("<command-args>", 1)[1].split("</command-args>", 1)[0] if "<command-args>" in text else ""
                commands.append(f"{name} {args}".strip())
            if text.startswith("Base directory for this skill: "):
                bases.append(text.split("\n", 1)[0].removeprefix("Base directory for this skill: "))
    return commands, bases


def summarize(events, plugin_dir, transcript=None):
    init = next((e for e in events if e.get("type") == "system" and e.get("subtype") == "init"), None)
    result = next((e for e in reversed(events) if e.get("type") == "result"), None)
    skills, agents, plugin_reads, denied = [], [], [], []
    for e in events:
        if e.get("type") != "assistant":
            continue
        for c in (e.get("message") or {}).get("content") or []:
            if c.get("type") != "tool_use":
                continue
            i = c.get("input") or {}
            if c.get("name") == "Skill":
                skills.append(f"{i.get('skill')} {i.get('args') or ''}".strip())
            elif c.get("name") in ("Agent", "Task"):
                agents.append(f"{i.get('subagent_type') or 'general-purpose'} model={i.get('model') or 'pinned/inherited'}"
                              f" — {i.get('description', '')}")
            elif c.get("name") == "Read" and norm(i.get("file_path", "")).startswith(norm(plugin_dir)):
                plugin_reads.append(os.path.relpath(i["file_path"], plugin_dir))
    for d in (result or {}).get("permission_denials") or []:
        denied.append(f"{d.get('tool_name')}: {json.dumps(d.get('tool_input'))[:200]}")
    commands, bases = session_loads(transcript)
    foreign = [b for b in bases if not norm(b).startswith(norm(plugin_dir))]
    lines = [f"plugin: {plugin_check(init, plugin_dir)}",
             f"mcp servers: {[m.get('name') for m in (init or {}).get('mcp_servers') or []]}",
             f"model: {(init or {}).get('model')}",
             f"slash commands this session: {commands or 'none'}",
             f"skill bodies loaded from: {sorted(set(bases)) or 'none'}" + (f"  FAIL: outside the plugin: {foreign}" if foreign else ""),
             f"skills invoked by the model this turn: {skills or 'none'}",
             f"plugin files read this turn: {plugin_reads or 'none'}",
             f"agents dispatched this turn: {len(agents)}", *[f"  - {a}" for a in agents],
             f"denied tool calls: {denied or 'none'}"]
    if result:
        lines += [f"result: {result.get('subtype')} is_error={result.get('is_error')} turns={result.get('num_turns')} "
                  f"cost=${result.get('total_cost_usd', 0):.2f} wall={result.get('duration_ms', 0) // 1000}s",
                  "", "--- final message ---", result.get("result") or ""]
    else:
        lines.append("result: NONE (crashed, killed, or timed out)")
    return "\n".join(lines)


def scratch_state(scratch):
    return "\n".join(["$ git log --stat -10", sh(["git", "log", "--stat", "-10"], scratch, check=False),
                      "", "$ git status --short --untracked-files=all", sh(["git", "status", "--short", "--untracked-files=all"], scratch, check=False),
                      "", "$ git branch -a", sh(["git", "branch", "-a"], scratch, check=False),
                      "", "$ git worktree list", sh(["git", "worktree", "list"], scratch, check=False)])


def copy_transcripts(session_id, dest):
    found = list((CONFIG / "projects").glob(f"*/{session_id}.jsonl"))
    if not found:
        return None
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(found[0], dest / found[0].name)
    if (found[0].parent / session_id).is_dir():
        shutil.copytree(found[0].parent / session_id, dest / session_id, dirs_exist_ok=True)
    return found[0].parent


def kill_tree(proc):
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True)
    else:
        os.killpg(proc.pid, 9)


def _unlock(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def load(run):
    run_dir = Path(run) if Path(run).is_dir() else RUNS / run
    meta_file = run_dir / "meta.json"
    if not meta_file.exists():
        raise SystemExit(f"no run at {run_dir}")
    return run_dir, json.loads(meta_file.read_text(encoding="utf-8"))


def save(run_dir, meta):
    (run_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")


def cmd_doctor(a):
    ok = True

    def check(name, passed, detail=""):
        nonlocal ok
        ok &= bool(passed)
        print(f"[{'ok' if passed else 'FAIL'}] {name}{': ' + detail if detail else ''}")

    plugin_dir = Path(a.plugin_dir or ROOT).resolve()
    claude = shutil.which("claude")
    check("claude on PATH", claude, sh([claude, "--version"]) if claude else "install Claude Code")
    if claude:
        auth = json.loads(sh([claude, "auth", "status"], check=False) or "{}")
        check("claude logged in", auth.get("loggedIn"), auth.get("authMethod", ""))
    for f in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json"):
        try:
            json.loads((plugin_dir / f).read_text(encoding="utf-8"))
            check(f"{f} parses", True)
        except (OSError, ValueError) as e:
            check(f"{f} parses", False, str(e))
    hook = ROOT / ".claude/hooks/check-frontmatter.mjs"
    skill_files = sorted(plugin_dir.glob("skills/*/SKILL.md"))
    agent_files = sorted(plugin_dir.glob("agents/*.md"))
    bad = []
    for f in skill_files + agent_files:
        r = subprocess.run(["node", str(hook)], input=json.dumps({"tool_input": {"file_path": str(f)}}),
                           capture_output=True, text=True, encoding="utf-8")
        if r.returncode:
            bad.append(r.stderr.strip())
    check(f"frontmatter of {len(skill_files)} skills and {len(agent_files)} agents", not bad, "\n".join(bad))
    stale = sorted(Path(tempfile.gettempdir()).glob(SCRATCH_PREFIX + "*"))
    check("no scratch repo left by an earlier run", not stale,
          ", ".join(map(str, stale)) + " — run cleanup on its run, or delete it if no run names it" if stale else "")
    if not a.offline and claude:
        with tempfile.TemporaryDirectory(prefix=SCRATCH_PREFIX + "doctor-") as tmp:
            Path(tmp, "mcp.json").write_text('{"mcpServers": {}}', encoding="utf-8")
            argv = [claude, "-p", "Reply with the single word READY.", "--model", "haiku", "--plugin-dir", str(plugin_dir),
                    "--strict-mcp-config", "--mcp-config", str(Path(tmp, "mcp.json")), "--no-session-persistence",
                    "--output-format", "stream-json", "--verbose", "--max-budget-usd", "0.5"]
            r = subprocess.run(argv, cwd=tmp, capture_output=True, text=True, encoding="utf-8", errors="replace",
                               stdin=subprocess.DEVNULL, timeout=300)
            events = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
        for leftover in (CONFIG / "projects").glob(f"*{Path(tmp).name}"):  # an empty memory folder, even without persistence
            if not any(f.is_file() for f in leftover.rglob("*")):
                shutil.rmtree(leftover, onerror=_unlock)
        init = next((e for e in events if e.get("subtype") == "init"), None)
        result = next((e for e in events if e.get("type") == "result"), {})
        check("live session loads this checkout as the skills plugin", plugin_check(init, plugin_dir) == "ok",
              plugin_check(init, plugin_dir))
        loaded = [s for s in (init or {}).get("skills") or [] if s.startswith("skills:")]
        check("every skill registered", len(loaded) == len(skill_files), f"{len(loaded)} of {len(skill_files)}")
        loaded_agents = [s for s in (init or {}).get("agents") or [] if s.startswith("skills:")]
        check("every agent registered", len(loaded_agents) == len(agent_files), f"{len(loaded_agents)} of {len(agent_files)}")
        check("no MCP server loaded", init and not init.get("mcp_servers"), str((init or {}).get("mcp_servers")))
        check("model answered", "READY" in (result.get("result") or ""), (result.get("result") or r.stderr)[:200])
    print("doctor: " + ("ok" if ok else "FAIL"))
    return 0 if ok else 1


def cmd_new(a):
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    run_id = f"{stamp}-{a.name}"
    run_dir = RUNS / run_id
    run_dir.mkdir(parents=True)
    scratch = Path(tempfile.gettempdir()) / f"{SCRATCH_PREFIX}{run_id}"
    if a.from_repo:
        sh(["git", "clone", "--quiet", "--no-hardlinks", str(Path(a.from_repo).resolve()), str(scratch)])
        sh(["git", "remote", "remove", "origin"], scratch)
    else:
        scratch.mkdir()
        sh(["git", "init", "--quiet", "--initial-branch=main"], scratch)
        (scratch / "README.md").write_text(f"# Scratch\n\nA throwaway repo for the {a.name} verification run.\n", encoding="utf-8")
        sh(["git", "add", "README.md"], scratch)
    sh(["git", "config", "user.name", "Skills Verify"], scratch)
    sh(["git", "config", "user.email", "verify@localhost"], scratch)
    sh(["git", "config", "core.longpaths", "true"], scratch)
    if not a.from_repo:
        sh(["git", "commit", "--quiet", "-m", "Scratch repo"], scratch)
    (run_dir / "mcp-empty.json").write_text('{"mcpServers": {}}', encoding="utf-8")
    meta = {"run": run_id, "scratch": str(scratch), "plugin_dir": str(Path(a.plugin_dir or ROOT).resolve()),
            "plugin_commit": sh(["git", "rev-parse", "HEAD"], a.plugin_dir or ROOT),
            "plugin_dirty": bool(sh(["git", "status", "--porcelain"], a.plugin_dir or ROOT)),
            "session_id": str(uuid.uuid4()), "turns": 0, "created": stamp}
    save(run_dir, meta)
    (run_dir / "scratch-00-start.txt").write_text(scratch_state(scratch), encoding="utf-8")
    print(f"run: {run_dir}\nscratch: {scratch}")
    return 0


def cmd_turn(a):
    run_dir, meta = load(a.run)
    scratch = Path(meta["scratch"])
    if not scratch.is_dir():
        raise SystemExit(f"scratch repo {scratch} is gone; start a new run")
    n = meta["turns"] + 1
    tag = f"{n:02d}"
    (run_dir / f"turn-{tag}.prompt.txt").write_text(a.prompt, encoding="utf-8")
    argv = claude_argv(a.prompt, meta["plugin_dir"], run_dir / "mcp-empty.json", meta["session_id"], n > 1,
                       a.model, a.effort, a.budget)
    # print mode stops a session 10 minutes after its last turn while a background agent still runs; 0 waits for it
    env = {**os.environ, "CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS": "0"}
    started = time.time()
    timed_out = False
    with open(run_dir / f"turn-{tag}.jsonl", "w", encoding="utf-8") as out, \
            open(run_dir / f"turn-{tag}.stderr.log", "w", encoding="utf-8") as err:
        proc = subprocess.Popen(argv, cwd=scratch, env=env, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                start_new_session=os.name != "nt")
        try:
            proc.wait(timeout=a.timeout)
        except subprocess.TimeoutExpired:
            kill_tree(proc)
            timed_out = True
    meta["turns"] = n
    project_dir = copy_transcripts(meta["session_id"], run_dir / "transcripts")
    if project_dir:
        meta["project_dir"] = str(project_dir)
    save(run_dir, meta)
    transcript = run_dir / "transcripts" / f"{meta['session_id']}.jsonl"
    summary = summarize(read_stream(run_dir / f"turn-{tag}.jsonl"), meta["plugin_dir"], transcript)
    if timed_out:
        summary = f"TIMED OUT after {a.timeout}s; process tree killed\n" + summary
    state = scratch_state(scratch)
    (run_dir / f"turn-{tag}.summary.md").write_text(summary + "\n", encoding="utf-8")
    (run_dir / f"scratch-{tag}.txt").write_text(state + "\n", encoding="utf-8")
    print(f"turn {n} ({int(time.time() - started)}s) — evidence in {run_dir}\n\n{summary}\n\n--- scratch repo ---\n{state}")
    checks = summary.split("--- final message ---", 1)[0]  # the model's own words may say FAIL
    return 1 if timed_out or "plugin: ok" not in checks or "FAIL" in checks else 0


def cmd_cleanup(a):
    run_dir, meta = load(a.run)
    scratch = Path(meta["scratch"])
    temp = Path(tempfile.gettempdir())
    if scratch.is_dir():
        if norm(scratch.parent) != norm(temp) or not scratch.name.startswith(SCRATCH_PREFIX):
            raise SystemExit(f"refusing to delete {scratch}: not a scratch repo this skill made")
        (run_dir / "scratch-final.txt").write_text(scratch_state(scratch) + "\n", encoding="utf-8")
        shutil.copytree(scratch, run_dir / "scratch-final", ignore=shutil.ignore_patterns("node_modules"),
                        dirs_exist_ok=True)
        shutil.rmtree(scratch, onerror=_unlock)
        print(f"deleted {scratch}; its final tree is in {run_dir / 'scratch-final'}")
    project = meta.get("project_dir")
    if project and Path(project).is_dir():
        ours = {f"{meta['session_id']}.jsonl", meta["session_id"]}
        if {p.name for p in Path(project).iterdir()} <= ours | {"memory"}:
            shutil.rmtree(project, onerror=_unlock)
            print(f"deleted the session folder {project}; its transcripts are in {run_dir / 'transcripts'}")
        else:
            print(f"kept {project}: it holds sessions this run did not make")
    print(f"evidence kept: {run_dir}")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("doctor", help="read-only checks, plus one cheap live session unless --offline")
    d.add_argument("--plugin-dir", help="plugin under test (default: this checkout)")
    d.add_argument("--offline", action="store_true", help="skip the live Haiku session")
    n = sub.add_parser("new", help="make a scratch repo and an evidence folder")
    n.add_argument("name", help="short kebab-case name for the run, such as setup-local")
    n.add_argument("--plugin-dir", help="plugin under test, such as a worktree of another commit (default: this checkout)")
    n.add_argument("--from-repo", help="clone this local repo as the scratch repo instead of an empty one; its remote is removed")
    t = sub.add_parser("turn", help="send one user message; the first starts the session, later ones resume it")
    t.add_argument("run", help="run folder or its name under runs/")
    t.add_argument("prompt")
    t.add_argument("--model", help="main session model (default: the user's default)")
    t.add_argument("--effort")
    t.add_argument("--budget", type=float, default=10.0, help="USD cap for this turn (default 10)")
    t.add_argument("--timeout", type=int, default=1800, help="seconds (default 1800)")
    c = sub.add_parser("cleanup", help="delete the scratch repo and session folder; keep the evidence")
    c.add_argument("run")
    a = p.parse_args(argv)
    return {"doctor": cmd_doctor, "new": cmd_new, "turn": cmd_turn, "cleanup": cmd_cleanup}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
