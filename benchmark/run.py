"""Run `claude -p '/implement #N'` headless on each frozen Spec, once per run on each side, alternating A,B,A,B.

  python benchmark/run.py --baseline <ref> --candidate <ref> --model sonnet --effort high \
      --claim "<what you expect to show>" --runs 5 --yes

Without --yes it prints the plan and the cost and runs nothing. Every run gets a throwaway worktree of the
target repo at the Spec's base, on its own branch, so the run lands there and nowhere else. Model, effort and
every other setting come from one set of arguments and apply to both sides. Guards: see guards.py and ADR-0066.

  python benchmark/run.py --record <spec-id> [--skills <ref>] [--model sonnet] [--effort high]

records one run of one Spec for a later Replay (record.py, ADR-0086) and runs at once, with no --yes."""
import argparse
import hashlib
import json
import os
import shutil
import signal
import stat
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import collect
import guards
import metrics
import record
import score
import seed
import usage_share
import yamlish

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent  # the skills checkout this benchmark lives in
BENCH_PROMPT = ("Benchmark mode: SKILLS_BENCHMARK=1. SKILLS_BENCHMARK_LOG names the log file and bench-log appends to it. "
                "Follow the Benchmark mode section of the implement skill.")
DOLLARS_PER_RUN = (20, 30)  # ref/token-analysis.md: about $20 on Sonnet only, $29 on average, per /implement run


@dataclass
class Settings:
    model: str
    effort: str
    claim: str
    claude_cmd: list = field(default_factory=lambda: [shutil.which("claude") or "claude"])
    timeout: int = 7200
    max_budget: float = 100.0
    run_checks: bool = True
    clone: Path = None
    record: bool = False


def git(cwd, *args):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        raise SystemExit(f"git {' '.join(args)} failed in {cwd}: {r.stderr.strip()}")
    return r.stdout.strip()


def load_specs(ids=None, path=HERE / "specs.yaml"):
    data = yamlish.load(path)
    specs = [{"repo": data["defaults"]["repo"], **s} for s in data["specs"]]
    for s in specs:
        todo = [k for k, v in s.items() if v == "TODO"]
        if todo and (ids is None or s["id"] in ids):
            raise SystemExit(f"Spec {s['id']} has TODO fields: {', '.join(todo)}")
    unknown = set(ids or []) - {s["id"] for s in specs}
    if unknown:
        raise SystemExit(f"unknown Spec id(s): {', '.join(sorted(unknown))}")
    return [s for s in specs if ids is None or s["id"] in ids]


def skills_checkout(ref, root=ROOT):
    """A throwaway worktree of the skills repo at ref: the plugin under test."""
    sha = git(root, "rev-parse", "--verify", f"{ref}^{{commit}}")
    if "SKILLS_BENCHMARK" not in git(root, "show", f"{sha}:skills/implement/SKILL.md"):
        raise SystemExit(f"{ref} ({sha[:12]}) has no benchmark mode in skills/implement/SKILL.md: its claim and pushes "
                         "would not be no-ops. Compare commits that both carry it (ADR-0066).")
    path = HERE / "work" / f"skills-{sha[:12]}"
    if not path.exists():
        git(root, "worktree", "add", "--detach", str(path), sha)
    return sha, path


def target_clone(repo, override, specs):
    path = Path(override) if override else HERE / "work" / repo.split("/")[1]
    if path.exists():
        git(path, "fetch", "--quiet", "origin")
    else:
        git(HERE, "clone", "--quiet", f"https://github.com/{repo}.git", str(path))
    for s in specs:
        git(path, "cat-file", "-e", f"{s['base']}^{{commit}}")
    return path


def reset_clone(clone):
    """No worktree and no branch of an earlier run: a leftover <slug> branch would make /implement resume it."""
    main = git(clone, "worktree", "list", "--porcelain").splitlines()[0].split(" ", 1)[1]
    for line in git(clone, "worktree", "list", "--porcelain").splitlines():
        if line.startswith("worktree ") and Path(line[9:]) != Path(main) and Path(line[9:]).exists():  # a worktree /implement made inside the run's goes with it
            shutil.rmtree(line[9:], onerror=_unlock)
    git(clone, "worktree", "prune")
    keep = git(clone, "branch", "--show-current")
    for branch in git(clone, "for-each-ref", "--format=%(refname:short)", "refs/heads").splitlines():
        if branch != keep:
            git(clone, "branch", "-D", branch)


def _unlock(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def other_plugins_off(worktree):
    """Settings that turn off every plugin the user or the target repo enables, so only the plugin under test loads."""
    config = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")
    names = set()
    for path in (config / "settings.json", worktree / ".claude" / "settings.json", worktree / ".claude" / "settings.local.json"):
        try:
            names |= set(json.loads(path.read_text(encoding="utf-8")).get("enabledPlugins") or {})
        except (OSError, ValueError, AttributeError):
            pass
    return {"enabledPlugins": {name: False for name in sorted(names)}}


def mcp_config(spec, worktree):
    """The MCP servers a run loads: only those the Spec names, from the .mcp.json of the worktree at the Spec's base."""
    names = spec.get("mcp_servers") or []
    try:
        servers = json.loads((Path(worktree) / ".mcp.json").read_text(encoding="utf-8")).get("mcpServers") or {}
    except (OSError, ValueError):
        servers = {}
    missing = [n for n in names if n not in servers]
    if missing:
        raise SystemExit(f"Spec {spec['id']} names MCP server(s) its .mcp.json at the base lacks: {', '.join(missing)}")
    return {"mcpServers": {n: servers[n] for n in names}}


def run_settings(worktree, run_dir, record_run_id=None):
    """Every plugin but the one under test off, a status line that captures the weekly limit, and when recording, the dispatch hook."""
    settings = other_plugins_off(worktree)
    settings["statusLine"] = {"type": "command", "command": usage_share.status_line_command(run_dir / "usage.log")}
    if record_run_id:
        hook = {"type": "command", "command": record.hook_command(run_dir / "dispatches.jsonl", record_run_id)}
        settings["hooks"] = {"PreToolUse": [{"matcher": "Agent", "hooks": [hook]}]}
    return settings


def build_argv(settings, spec, plugin_dir, session_id, mcp_file, settings_file, prompt=None, agent=None):
    """The `claude -p` command of a run: /implement on the Spec's Issue, or a Replay's recorded prompt as the named agent."""
    return [*settings.claude_cmd, "-p", prompt or f"/implement #{spec['issue']}", *(["--agent", agent] if agent else []),
            "--model", settings.model, "--effort", settings.effort,
            "--permission-mode", "bypassPermissions", "--max-budget-usd", str(settings.max_budget),
            "--plugin-dir", str(plugin_dir), "--strict-mcp-config", "--mcp-config", str(mcp_file),
            "--settings", str(settings_file), "--session-id", session_id, "--output-format", "stream-json", "--verbose",
            "--append-system-prompt", BENCH_PROMPT,
            "--disallowedTools", *guards.DENIED_TOOLS]  # variadic, so it goes last


def spec_hash(spec):
    """Hash of the Issue as /implement will read it now, so compare can tell a Spec that changed between runs."""
    r = subprocess.run(["gh", "issue", "view", str(spec["issue"]), "-R", spec["repo"], "--json", "title,body"],
                       capture_output=True, text=True, encoding="utf-8")
    return hashlib.sha256(r.stdout.encode()).hexdigest()[:12] if r.returncode == 0 else None


def read_stream(path):
    init = result = None
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            o = json.loads(line)
        except ValueError:
            continue
        if o.get("type") == "system" and o.get("subtype") == "init":
            init = o
        elif o.get("type") == "result":
            result = o
    return init, result


def plugin_verified(init, plugin_dir):
    """True when the plugin under test is the only one that loaded, built-ins aside; None when the stream cannot say."""
    plugins = [p for p in (init or {}).get("plugins") or [] if isinstance(p, dict) and p.get("path") and p["path"] != "builtin"]
    if not plugins:
        return None
    norm = lambda p: os.path.normcase(os.path.realpath(p))
    return len(plugins) == 1 and norm(plugins[0]["path"]) == norm(plugin_dir)


def copy_transcripts(session_id, dest):
    config = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")
    found = list((config / "projects").glob(f"*/{session_id}.jsonl"))
    if not found:
        return False
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(found[0], dest / found[0].name)
    if (found[0].parent / session_id).is_dir():
        shutil.copytree(found[0].parent / session_id, dest / session_id, dirs_exist_ok=True)
    return True


def kill_tree(proc):
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True)
    else:
        os.killpg(proc.pid, signal.SIGKILL)


def guard_env(run_dir):
    """The environment every benchmark session runs in: the guards of guards.py and no wait ceiling on background agents."""
    # print mode stops a session 10 minutes after its last turn while a Step agent still runs in the background; 0 waits for it
    (run_dir / "bench.log").touch()
    return {**os.environ, **guards.install(run_dir / "guards", run_dir / "bench.log"), "CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS": "0"}


def run_session(argv, cwd, env, run_dir, timeout):
    """Run one session to stream.jsonl and stderr.log in run_dir; (exit code, timed out)."""
    with open(run_dir / "stream.jsonl", "w", encoding="utf-8") as out, open(run_dir / "stderr.log", "w", encoding="utf-8") as err:
        proc = subprocess.Popen(argv, cwd=cwd, env=env, stdout=out, stderr=err, start_new_session=os.name != "nt")
        try:
            return proc.wait(timeout=timeout), False
        except subprocess.TimeoutExpired:
            kill_tree(proc)
            return None, True


def run_one(side, sha, plugin_dir, spec, index, settings):
    started = datetime.now(timezone.utc)
    run_id = f"{started:%Y%m%dT%H%M%S}-{sha[:8]}-{spec['id']}-{index}"
    run_dir = HERE / "runs" / run_id
    clone, worktree, session_id = settings.clone, HERE / "work" / "w", str(uuid.uuid4())
    reset_clone(clone)
    git(clone, "-c", "core.longpaths=true", "worktree", "add", "-q", "-b", "bench-run", str(worktree), spec["base"])
    try:
        mcp = mcp_config(spec, worktree)
    except SystemExit:  # refused before the run starts: leave no worktree behind
        reset_clone(clone)
        raise
    run_dir.mkdir(parents=True)
    (run_dir / "mcp.json").write_text(json.dumps(mcp, indent=2), encoding="utf-8")
    (run_dir / "settings.json").write_text(json.dumps(run_settings(worktree, run_dir, run_id if settings.record else None), indent=2),
                                           encoding="utf-8")
    env = guard_env(run_dir)
    meta = {"run_id": run_id, "side": side, "skills_sha": sha, "spec": spec["id"], "issue": spec["issue"], "index": index,
            "model": settings.model, "effort": settings.effort, "claim": settings.claim, "spec_hash": spec_hash(spec),
            "base": spec["base"], "worktree": str(worktree), "session_id": session_id, "started": started.isoformat(),
            "load": os.getloadavg()[0] if hasattr(os, "getloadavg") else None, "timed_out": False}
    argv = build_argv(settings, spec, plugin_dir, session_id, run_dir / "mcp.json", run_dir / "settings.json")
    try:
        meta["exit_code"], meta["timed_out"] = run_session(argv, worktree, env, run_dir, settings.timeout)
        init, result = read_stream(run_dir / "stream.jsonl")
        meta.update(plugin_verified=plugin_verified(init, plugin_dir), result_is_error=bool(result and result.get("is_error")),
                    result_subtype=result.get("subtype") if result else None, ended=datetime.now(timezone.utc).isoformat())
        meta["transcripts_found"] = copy_transcripts(session_id, run_dir / "transcripts")
        (run_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        m = metrics.extract(run_dir / "transcripts")
        (run_dir / "metrics.json").write_text(json.dumps(m, indent=2), encoding="utf-8")
        s = score.score_run(run_dir, meta, spec, m, run_checks=settings.run_checks)
        if settings.record:
            if s["valid"]:
                s["recorded"] = str(HERE / "work" / "recorded" / run_id)
                try:
                    record.finish(run_dir, s["recorded"], meta, spec, m, worktree, clone)
                except seed.Refused as e:
                    s["recorded"], s["refused"] = None, str(e)
            else:
                record.discard(clone, run_id)
        (run_dir / "final.log").write_text(git(worktree, "log", "--stat", f"{spec['base']}..HEAD"), encoding="utf-8")
        return s
    finally:
        reset_clone(clone)
        collect.rebuild(sha)


def record_run(a):
    """One run on one side of one Spec, kept as a Recorded run; refused when the scorer finds the run invalid."""
    specs = load_specs([a.record])
    sha, plugin_dir = skills_checkout(a.skills)
    model, effort = a.model or "sonnet", a.effort or "high"
    print(f"Recording 1 /implement run of {a.record} on skills {sha[:12]} ({model}, {effort}): about "
          f"${DOLLARS_PER_RUN[0]}-{DOLLARS_PER_RUN[1]} of list-price tokens, up to {a.timeout // 3600} h at the {a.timeout}s timeout.", flush=True)
    settings = Settings(model, effort, f"record {a.record}", timeout=a.timeout, max_budget=a.max_budget, run_checks=not a.no_checks,
                        clone=target_clone(specs[0]["repo"], a.target_clone, specs), record=True)
    if a.claude:
        settings.claude_cmd = [a.claude]
    s = run_one("record", sha, plugin_dir, specs[0], 1, settings)
    if not s["valid"]:
        raise SystemExit("Refused as a Recorded run, the run is invalid: " + "; ".join(s["invalid_reasons"]))
    if s.get("refused"):
        raise SystemExit(f"Refused as a Recorded run, it cannot be seeded: {s['refused']}")
    print(f"Recorded: {s['recorded']}")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--record", metavar="SPEC_ID", help="record one run of this Spec for a later Replay, at once; replaces --baseline, --candidate, --claim and --runs")
    p.add_argument("--skills", default="HEAD", help="with --record: the skills ref to record on (default: this checkout's HEAD)")
    p.add_argument("--baseline", help="skills ref without the change")
    p.add_argument("--candidate", help="skills ref with the change")
    p.add_argument("--model", help="required unless --record (then sonnet)")
    p.add_argument("--effort", help="required unless --record (then high)")
    p.add_argument("--claim", help="the claim you expect to make, in the words you would ship")
    p.add_argument("--runs", type=int, default=5, help="runs per Spec per side (default 5)")
    p.add_argument("--specs", help="comma-separated Spec ids (default: all)")
    p.add_argument("--target-clone", help="a clone of the target repo to use instead of benchmark/work/<name>")
    p.add_argument("--claude", help="path to claude (default: PATH)")
    p.add_argument("--timeout", type=int, default=7200, help="seconds per run")
    p.add_argument("--max-budget", type=float, default=100.0, help="USD cap per run, passed to claude")
    p.add_argument("--no-checks", action="store_true", help="skip the scorer's build and tests (the report is then inconclusive)")
    p.add_argument("--yes", action="store_true", help="run; without it only the plan is printed")
    a = p.parse_args(argv)
    if a.record:
        return record_run(a)
    missing = [f"--{name}" for name in ("baseline", "candidate", "model", "effort", "claim") if not getattr(a, name)]
    if missing:
        p.error(f"the following arguments are required: {', '.join(missing)}")

    specs = load_specs(a.specs.split(",") if a.specs else None)
    sides = {side: skills_checkout(ref) for side, ref in (("baseline", a.baseline), ("candidate", a.candidate))}
    if sides["baseline"][0] == sides["candidate"][0]:
        raise SystemExit("baseline and candidate are the same commit")
    total = len(specs) * a.runs * 2
    print(f"{len(specs)} Spec(s) x {a.runs} run(s) x 2 sides = {total} /implement runs, alternating baseline, candidate.")
    print(f"At about ${DOLLARS_PER_RUN[0]}-{DOLLARS_PER_RUN[1]} of list-price tokens per run that is ${total * DOLLARS_PER_RUN[0]}-{total * DOLLARS_PER_RUN[1]}, "
          f"and up to {total * a.timeout // 3600} h at the {a.timeout}s timeout.")
    for side, (sha, _) in sides.items():
        print(f"  {side}: {sha[:12]}")
    if not a.yes:
        print("Plan only. Add --yes to run.")
        return 0

    settings = Settings(a.model, a.effort, a.claim, timeout=a.timeout, max_budget=a.max_budget, run_checks=not a.no_checks,
                        clone=target_clone(specs[0]["repo"], a.target_clone, specs))
    if a.claude:
        settings.claude_cmd = [a.claude]
    for index in range(1, a.runs + 1):
        for spec in specs:
            for side, (sha, plugin_dir) in sides.items():
                started = time.time()
                s = run_one(side, sha, plugin_dir, spec, index, settings)
                print(f"{side:9} {spec['id']} #{index}: {'valid' if s['valid'] else 'INVALID ' + '; '.join(s['invalid_reasons'])} "
                      f"({time.time() - started:.0f}s)", flush=True)
    for side, (sha, _) in sides.items():
        print(f"{side}: {collect.rebuild(sha)[0]}")
    print("Next: python benchmark/compare.py", sides["baseline"][0][:12], sides["candidate"][0][:12])
    return 0


if __name__ == "__main__":
    sys.exit(main())
