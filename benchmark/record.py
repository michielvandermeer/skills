"""Records an /implement run so a later Replay sees what the original agent saw (ADR-0086).

  python record.py hook <dispatch file> <run id>    hook mode: Claude Code's PreToolUse JSON for an Agent call on stdin

The run's --settings fires the hook before every Agent tool call. It appends the dispatched agent's type, its prompt
and the HEAD of the repo the hook's cwd names to the dispatch file, and points refs/recorded/<run id>/<n> at that
commit, so the commit outlives the Landing commit that replaces the run's commits. It always exits 0: a hook that
failed must not block the dispatch. After the run, finish() joins each dispatch to its sub-agent transcript and
writes recorded.json, with the seeded Verify dispatch (seed.py) beside the dispatches."""
import contextlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import metrics
import seed

HERE = Path(__file__).resolve()
STATUS_RE = re.compile(r"^\s*status:\s*([a-z]+)", re.I | re.M)
REVIEW_FINDING_RE = re.compile(r"^[ \t>*\-#]*((?:Hard violation|Judgement call):.*)$", re.M)
FINDINGS_RE = re.compile(r"^\s*findings:(.*)$", re.I)
REPORT_KEY_RE = re.compile(r"^\s*(status|deviations|stop|declined):", re.I)
LOCK_WAIT = 10.0  # seconds a hook waits for another hook's lock before it takes the lock as stale


def hook_command(dispatch_file, run_id):
    return f'"{Path(sys.executable).as_posix()}" "{HERE.as_posix()}" hook "{Path(dispatch_file).resolve().as_posix()}" "{run_id}"'


def _git(cwd, *args):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout.strip() if r.returncode == 0 else None


@contextlib.contextmanager
def _locked(path):
    """Holds <path>.lock while the body runs, so two hooks that fire together number their dispatches one after the other.
    A lock still there after LOCK_WAIT seconds is a crashed hook's: it is taken over, and removed at the end."""
    lock = Path(f"{path}.lock")
    deadline = time.monotonic() + LOCK_WAIT
    while time.monotonic() < deadline:
        try:
            os.close(os.open(lock, os.O_CREAT | os.O_EXCL))
            break
        except FileExistsError:
            time.sleep(0.02)
    try:
        yield
    finally:
        lock.unlink(missing_ok=True)


def hook(dispatch_file, run_id, stdin_text):
    try:
        data = json.loads(stdin_text)
        tool_input = data.get("tool_input") or {}
        head = _git(data.get("cwd"), "rev-parse", "HEAD")
        path = Path(dispatch_file)
        with _locked(path):
            n = (path.read_text(encoding="utf-8").count("\n") if path.exists() else 0) + 1
            if head:
                _git(data.get("cwd"), "update-ref", f"refs/recorded/{run_id}/{n}", head)
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"n": n, "agent": tool_input.get("subagent_type") or "general-purpose",
                                    "prompt": tool_input.get("prompt"), "start": head}) + "\n")
    except Exception as e:  # noqa: BLE001 - a recording hook must never block the dispatch
        print(f"record hook: {e}", file=sys.stderr)
    return 0


def verdict(role, text):
    """The report's status line, plus every Hard violation and Judgement call of a Reviewer or every finding of a Verifier."""
    statuses = STATUS_RE.findall(text)
    findings = []
    if role == "reviewer":
        findings = REVIEW_FINDING_RE.findall(text)
    elif role == "verifier":
        findings = _verifier_findings(text)
    return {"status": statuses[-1].lower() if statuses else None, "findings": findings}


def _verifier_findings(text):
    findings, inside = [], False
    for line in text.splitlines():
        opened = FINDINGS_RE.match(line)
        if opened:
            inside = True
            line = opened.group(1)
        elif REPORT_KEY_RE.match(line):
            inside = False
        if not inside or not line.strip():
            continue
        if line.strip().startswith("- ") or opened:
            findings.append(line.strip().removeprefix("- ").strip())
        elif findings:
            findings[-1] += "\n" + line.rstrip()
    return [f for f in findings if f.rstrip(".").lower() != "none"]


def read_dispatches(path):
    path = Path(path)
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()] if path.exists() else []


def _subagents(transcripts, session_id):
    """[(agent id, prompt, last assistant text)] of the run's sub-agents, in the order they started."""
    found = []
    for path in (Path(transcripts) / session_id / "subagents").glob("agent-*.jsonl"):
        prompt = first = None
        last = ""
        for o in metrics._lines(path):
            message = o.get("message") if isinstance(o.get("message"), dict) else {}
            if o.get("type") == "user" and prompt is None:
                prompt = metrics._text(message)
            if o.get("type") == "assistant":
                last = metrics._text(message) or last
            first = first or o.get("timestamp")
        found.append((first or "", path.stem, (prompt or "").strip(), last))
    return [(agent, prompt, last) for _, agent, prompt, last in sorted(found)]


def _cost(by_model):
    return {"cost_usd": sum(m["cost_usd"] for m in by_model.values()), "by_model": by_model}


def join(raw, subagents, by_agent):
    """One row per dispatch: each takes the first sub-agent transcript, in start order, whose first user message is its prompt."""
    unused, rows = list(subagents), []
    for d in sorted(raw, key=lambda d: d["n"]):
        role = metrics.role_of(d["agent"])
        match = next((s for s in unused if s[1] == (d["prompt"] or "").strip()), None)
        if match:
            unused.remove(match)
        rows.append({"n": d["n"], "role": role, "agent": d["agent"], "prompt": d["prompt"], "start": d["start"],
                     "cost": _cost(by_agent[match[0]]) if match and match[0] in by_agent else None,
                     "verdict": verdict(role, match[2]) if match else None})
    return rows


def seed_dispatch(rows, clone, run_dir, meta, spec, landed):
    """The last Verify dispatch's row pointed at the seeded commit, with the reverted hunk and the failing test; no verdict, no cost."""
    verify = next((r for r in reversed(rows) if r["role"] == "verifier"), None)
    if verify is None:
        raise seed.Refused("the run has no Verify dispatch to seed")
    run_dir = Path(run_dir)
    found = seed.seed(clone, meta["run_id"], spec["base"], landed, spec["tests"], run_dir / "seed", run_dir / "seed-tests.log")
    return {**verify, "start": found["commit"], "cost": None, "verdict": None, "seeded": True, "hunk": found["hunk"],
            "failing_test": found["failing_test"]}


def finish(run_dir, recorded_dir, meta, spec, m, worktree, clone):
    """Keep the landed commit, join the dispatches to their transcripts, seed a Verify dispatch, and write recorded.json
    with the transcripts. A run that cannot be seeded raises seed.Refused, its refs and folder removed."""
    run_id = meta["run_id"]
    landed = _git(worktree, "rev-parse", "HEAD")
    if not landed:
        raise SystemExit(f"{run_id}: the run worktree has no HEAD to keep as the landed commit")
    _git(worktree, "update-ref", f"refs/recorded/{run_id}/landed", landed)
    rows = join(read_dispatches(Path(run_dir) / "dispatches.jsonl"), _subagents(Path(run_dir) / "transcripts", meta["session_id"]),
                m["by_agent"])
    recorded_dir = Path(recorded_dir)
    try:
        seeded = seed_dispatch(rows, clone, run_dir, meta, spec, landed)
    except seed.Refused:
        discard(clone, run_id)
        shutil.rmtree(recorded_dir, ignore_errors=True)
        raise
    recorded = {"run_id": run_id, "spec": spec["id"], "skills_sha": meta["skills_sha"], "model": meta["model"],
                "effort": meta["effort"], "base": spec["base"], "landed": landed, "session_id": meta["session_id"],
                "main_cost": _cost(m["by_agent"].get("main", {})), "dispatches": rows, "seeded_dispatch": seeded}
    recorded_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(Path(run_dir) / "transcripts", recorded_dir / "transcripts", dirs_exist_ok=True)
    (recorded_dir / "recorded.json").write_text(json.dumps(recorded, indent=2), encoding="utf-8")
    return recorded


def discard(clone, run_id):
    """Drop the refs of a run that is refused as a Recorded run, so its commits can be collected."""
    for ref in (_git(clone, "for-each-ref", "--format=%(refname)", f"refs/recorded/{run_id}/") or "").splitlines():
        _git(clone, "update-ref", "-d", ref)


def main(argv):
    if argv[:1] == ["hook"] and len(argv) == 3:
        sys.stdin.reconfigure(encoding="utf-8")  # a prompt with non-ASCII text must match its transcript
        return hook(argv[1], argv[2], sys.stdin.read())
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
