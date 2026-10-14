"""Frozen measurement for the implement-cost Hillclimb: a thin wrapper around benchmark/run.py and compare.py.

  python measure.py <baseline-ref> <candidate-ref> <pairs>    run <pairs> more alternating pairs (baseline, candidate), then judge
  python measure.py <baseline-ref> <candidate-ref> 0          judge the runs already on disk

One pair is one baseline run and one candidate run of /implement on ui-bug-394 (model sonnet, effort high, the mvdmio-suite
clone). The budget is the account's weekly limit: before every pair it reads `claude -p /usage` and stops at LIMIT percent
used, or when the points spent since the Hillclimb started reach CAP (state in scratch/usage.json, which survives a weekly reset).
Prints the verdict line, one line per side and the regressions; the full report goes to benchmark/results/."""
import json
import os
import re
import statistics
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SCRATCH = HERE / "scratch"
STATE = SCRATCH / "usage.json"
sys.path.insert(0, str(ROOT / "benchmark"))
import compare  # noqa: E402

CLONE = r"C:\Users\MichielvanderMeer\work\mvdmio-suite"
SPECS = "ui-bug-394"
LIMIT, CAP, START = 80, 25, 57
CLAIM = "Cutting agent hand-offs, pinned models and tool output cuts the list-price cost of an /implement run by 30% with the same quality."


def weekly_used():
    env = {**os.environ, "MSYS_NO_PATHCONV": "1"}
    r = subprocess.run(["claude", "-p", "/usage"], stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding="utf-8", env=env)
    m = re.search(r"Current week \(all models\): (\d+)% used", r.stdout)
    if not m:
        raise SystemExit(f"cannot read /usage: {r.stdout[:200]!r}")
    return int(m.group(1))


def budget_left():
    """(percent used now, points spent since the start across a weekly reset, may another pair start)."""
    used = weekly_used()
    state = json.loads(STATE.read_text()) if STATE.exists() else {"before_reset": 0, "base": START, "last": START}
    if used < state["last"] - 2:  # the week reset: bank the points spent so far
        state["before_reset"] += state["last"] - START
        state["base"] = 0
    state["last"] = used
    spent = state["before_reset"] + used - state["base"]
    STATE.write_text(json.dumps(state))
    return used, spent, used < LIMIT and spent < CAP


def run_pair(baseline, candidate):
    r = subprocess.run([sys.executable, str(ROOT / "benchmark" / "run.py"), "--baseline", baseline, "--candidate", candidate,
                        "--model", "sonnet", "--effort", "high", "--claim", CLAIM, "--runs", "1", "--specs", SPECS,
                        "--target-clone", CLONE, "--max-budget", "60", "--yes"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    (SCRATCH / "run.out").open("a", encoding="utf-8").write(r.stdout + r.stderr)
    lines = [l for l in r.stdout.splitlines() if l.startswith(("baseline ", "candidate "))]
    return r.returncode, lines


def side(rows):
    cost = compare.by_spec(rows, "cost_usd").get(SPECS, [])
    sub = compare.by_spec(rows, "subagents").get(SPECS, [])
    q = compare.quality(rows)
    if not cost:
        return f"no valid runs of {q['runs']}"
    return (f"median ${statistics.median(cost):.2f} (${min(cost):.2f}-${max(cost):.2f}), {len(cost)} valid of {q['runs']} runs, "
            f"{statistics.median(sub):.0f} subagents, errors: invalid {q['invalid']}, failed {q['failed']}, API {q['api_errors']:.0f}, "
            f"tests ok {q['tests']}/{q['valid']}")


def main():
    baseline, candidate, pairs = sys.argv[1], sys.argv[2], int(sys.argv[3])
    stopped = None
    for i in range(pairs):
        used, spent, ok = budget_left()
        if not ok:
            stopped = f"BUDGET STOP: {used}% of the week used, {spent} points spent since the start (limit {LIMIT}%, cap {CAP} points)"
            break
        code, lines = run_pair(baseline, candidate)
        print(f"pair {i + 1}/{pairs}: " + " | ".join(lines) + (f" (run.py exit {code})" if code else ""), flush=True)
        if code:
            stopped = f"STOPPED: run.py exited {code} on pair {i + 1}; see scratch/run.out"
            break
    used, spent, _ = budget_left()
    base, cand = compare.load_rows(baseline), compare.load_rows(candidate)
    names = (base[0]["skills_sha"][:12], cand[0]["skills_sha"][:12])
    text, verdict = compare.report(base, cand, CLAIM, names)
    (ROOT / "benchmark" / "results" / f"compare-{names[0]}-{names[1]}.md").write_text(text + "\n", encoding="utf-8")
    print(next(l for l in text.splitlines() if l.startswith("VERDICT")))
    print(f"baseline  {names[0]}: {side(base)}")
    print(f"candidate {names[1]}: {side(cand)}")
    reg = text.split("Quality regressions:")[1].splitlines()
    print("regressions:" + (" none" if "none flagged" in reg[0] else "") + "".join("\n" + l for l in reg[1:] if l.strip().startswith("-")))
    print(f"budget: week {used}% used, {spent} points spent since the start")
    if stopped:
        print(stopped)
    return 2 if verdict == "inconclusive" else 0


if __name__ == "__main__":
    sys.exit(main())
