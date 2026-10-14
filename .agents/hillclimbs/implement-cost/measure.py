"""Frozen measurement for the implement-cost Hillclimb: one side at a time, through benchmark/run.py's run_one.

  python measure.py run <ref> <runs>                   run <runs> /implement runs of skills commit <ref>, then summarise it
  python measure.py show <ref>                         summarise the runs of <ref> already on disk
  python measure.py judge <baseline-ref> <candidate-ref>   keep or revert, by the rule agreed for this Hillclimb

One run is `/implement` on SPEC (model sonnet, effort high, the mvdmio-suite clone), scored for build, tests, Proof and
diff size. The baseline is measured once on its own; an Attempt is one run (the user ruled out alternating pairs as too
costly). Budget: before every run the share of the week used (`claude -p /usage`) must not exceed the share of the
7-day window that has passed; while it does, the script waits, and gives up at DEADLINE.
Prints one summary line per side; the full rows go to benchmark/results/<sha12>.csv."""
import re
import statistics
import subprocess
import sys
import time
import os
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "benchmark"))
import collect  # noqa: E402
import compare  # noqa: E402
import run as bench  # noqa: E402

CLONE = r"C:\Users\MichielvanderMeer\work\mvdmio-suite"
SPEC = "backend-n-plus-1-393"
TZ =ZoneInfo("Europe/Amsterdam")
DEADLINE = datetime(2026, 10, 15, 11, 36, tzinfo=TZ)
CLAIM = "Cutting the tokens /implement spends cuts the list-price cost of a run by 20% with the same quality."
ROLES = ("main", "planner", "implementer", "checker", "reviewer", "prover", "fixer", "other")


def pace():
    """(percent of the week used, percent of the 7-day window passed)."""
    env = {**os.environ, "MSYS_NO_PATHCONV": "1"}
    out = subprocess.run(["claude", "-p", "/usage"], stdin=subprocess.DEVNULL, capture_output=True, text=True,
                         encoding="utf-8", env=env).stdout
    m = re.search(r"Current week \(all models\): (\d+)% used · resets (?:(\w{3} \d{1,2}), )?(\d{1,2}(?::\d\d)?[ap]m)", out)
    if not m:
        raise SystemExit(f"cannot read /usage: {out[:200]!r}")
    now = datetime.now(TZ)
    clock = m.group(3) if ":" in m.group(3) else m.group(3)[:-2] + ":00" + m.group(3)[-2:]
    day = m.group(2) or now.strftime("%b %d")
    reset = datetime.strptime(f"{now.year} {day} {clock}", "%Y %b %d %I:%M%p").replace(tzinfo=TZ)
    if reset < now - timedelta(days=1):  # a reset date in January read in December
        reset = reset.replace(year=now.year + 1)
    passed = 100 * (now - (reset - timedelta(days=7))) / timedelta(days=7)
    return int(m.group(1)), passed


def wait_for_budget():
    while True:
        used, passed = pace()
        if used <= passed:
            return used, passed
        if datetime.now(TZ) >= DEADLINE:
            raise SystemExit(f"BUDGET STOP: {used}% of the week used, {passed:.0f}% passed, deadline reached")
        print(f"waiting: {used}% of the week used, {passed:.0f}% passed", flush=True)
        time.sleep(900)


def rows_of(ref):
    sha = bench.git(ROOT, "rev-parse", "--verify", f"{ref}^{{commit}}")
    collect.rebuild(sha)
    return sha, [r for r in compare.load_rows(sha[:12]) if r["spec"] == SPEC]


def summary(ref):
    sha, rows = rows_of(ref)
    valid = [r for r in rows if compare.is_true(r["valid"])]
    if not valid:
        return f"{sha[:12]}: no valid runs of {len(rows)}"
    cost = [compare.num(r["cost_usd"]) for r in valid]
    q = compare.quality(rows)
    med = lambda key: statistics.median(compare.num(r[key]) or 0 for r in valid)
    roles = " ".join(f"{k} {med('cost_' + k):.2f}" for k in ROLES if med("cost_" + k))
    return (f"{sha[:12]}: median ${statistics.median(cost):.2f} (${min(cost):.2f}-${max(cost):.2f}), {len(valid)} valid of {len(rows)}, "
            f"{med('subagents'):.0f} subagents, {med('wall_s') / 60:.0f} min | build {q['build']} tests {q['tests']} proof {q['proof']} "
            f"of {len(valid)}, diff {q['diff_ratio']:.2f}, markup-tests {q['forbidden']}, guard trips {q['guard_trips']}, "
            f"API errors {q['api_errors']:.0f} | roles: {roles}")


def judge(baseline, candidate):
    """The agreed rule: the candidate's runs are all valid, cheaper than the cheapest baseline run, and lose no quality."""
    _, base = rows_of(baseline)
    _, cand = rows_of(candidate)
    bv = [r for r in base if compare.is_true(r["valid"])]
    if not bv or not cand:
        return "NO DATA"
    qb, qc = compare.quality(bv), compare.quality(cand)
    why = []
    if qc["invalid"]:
        why.append(f"{qc['invalid']} of {qc['runs']} runs invalid")
    floor = min(compare.num(r["cost_usd"]) for r in bv)
    worst = max((compare.num(r["cost_usd"]) or 0) for r in cand)
    if worst >= floor:
        why.append(f"${worst:.2f} is not below the cheapest baseline run ${floor:.2f}")
    for key in ("build", "tests", "proof"):
        if qc[key] < qc["valid"]:
            why.append(f"{key} held on {qc[key]} of {qc['valid']}")
    if qc["valid"] and not 0.67 <= qc["diff_ratio"] / qb["diff_ratio"] <= 1.5:
        why.append(f"diff size {qc['diff_ratio']:.2f} against baseline median {qb['diff_ratio']:.2f}")
    if qc["forbidden"] and qc["forbidden"] / qc["valid"] > qb["forbidden"] / qb["valid"]:
        why.append("more tests asserting markup or text")
    if qc["guard_trips"]:
        why.append("guard tripped")
    if qc["api_errors"] / qc["runs"] > qb["api_errors"] / qb["runs"]:
        why.append("more API errors")
    return "KEEP" if not why else "REVERT: " + "; ".join(why)


def main():
    mode = sys.argv[1]
    if mode == "run":
        ref, runs = sys.argv[2], int(sys.argv[3])
        sha, plugin_dir = bench.skills_checkout(ref)
        spec = bench.load_specs([SPEC])[0]
        bench.git(CLONE, "cat-file", "-e", f"{spec['base']}^{{commit}}")  # no fetch: the clone already holds the Spec's base
        settings = bench.Settings("sonnet", "high", CLAIM, max_budget=60.0, clone=Path(CLONE))
        for i in range(runs):
            used, passed = wait_for_budget()
            done = len(rows_of(sha)[1])
            started = time.time()
            s = bench.run_one("measured", sha, plugin_dir, spec, done + 1, settings)
            print(f"run {i + 1}/{runs}: {'valid' if s['valid'] else 'INVALID ' + '; '.join(s['invalid_reasons'])} "
                  f"({(time.time() - started) / 60:.0f} min; week {used}% used, {passed:.0f}% passed)", flush=True)
        print(summary(sha))
    elif mode == "show":
        print(summary(sys.argv[2]))
    elif mode == "judge":
        print(summary(sys.argv[2]))
        print(summary(sys.argv[3]))
        print(judge(sys.argv[2], sys.argv[3]))
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
