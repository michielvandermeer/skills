"""Frozen measurement for the implement-run-cost Hillclimb (#80): what an /implement run costs, measured on the Recorded
runs (ADR-0086), by the cheapest way that still sees what changed.

  python measure.py <before> <after> [runs]    both sides, alternating before, after, before, after
  python measure.py <checkout> [runs]          one side, both roles replayed: the baseline
  add --plan to print the path it would take and stop: nothing is spent and no total is written

<before> and <after> are skills checkouts; <after> may hold uncommitted changes (an Attempt). The path comes from the files
that differ between <before>'s commit and <after>'s working tree:
  only agents/verifier.md and agents/reviewer.md changed   replay the dispatches of those roles (benchmark/replay.py)
  any other file under agents/ or skills/ changed          rerun both Specs in full (benchmark/run.py)
  no file under agents/ or skills/ changed                 measure nothing
Prints one line per side and nothing else: the number (list-price dollars per run, summed over the Recorded runs), its
range, runs, work count, error count, the split by role, the weekly-limit share, the running total of dollars spent and the
guard. The running total lives in scratch/spend.json beside this script and survives across calls."""
import argparse
import json
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "benchmark"))
import compare  # noqa: E402
import metrics  # noqa: E402
import replay  # noqa: E402
import run  # noqa: E402
import usage_share  # noqa: E402

SCRATCH = HERE / "scratch"
RECORDED = run.HERE / "work" / "recorded"
RESULTS = run.HERE / "results"
RUNS = run.HERE / "runs"
COUNTED = ("agents/", "skills/")
REPLAYED_ROLE = {"agents/verifier.md": "verifier", "agents/reviewer.md": "reviewer"}  # a file the Replay holds nothing else fixed for
ROLE_ORDER = [*metrics.ROLES, "other"]
CLAIM = "Replaying or rerunning the recorded /implement runs shows the change cuts the list-price cost of a run with the same quality."


# ---- the path ---------------------------------------------------------------------------------------------------------

def choose(changed):
    """(path, roles) from the changed files: "nothing", "replay" with the roles to replay, or "rerun"."""
    counted = [f for f in changed if f.startswith(COUNTED)]
    if not counted:
        return "nothing", ()
    roles = {REPLAYED_ROLE.get(f) for f in counted}
    return ("rerun", ()) if None in roles else ("replay", tuple(sorted(roles)))


def git(cwd, *args, env=None):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    if r.returncode:
        raise SystemExit(f"git {' '.join(args)} failed in {cwd}: {r.stderr.strip()}")
    return r.stdout


def changed_files(before, after):
    """Tracked changes (staged or not) of <after>'s working tree against the commit <before> is at, and its untracked files not ignored."""
    sha = git(before, "rev-parse", "HEAD").strip()
    tracked = git(after, "diff", "--name-only", "--no-renames", "-z", sha)
    untracked = git(after, "ls-files", "--others", "--exclude-standard", "-z")
    return sorted(f for f in (tracked + untracked).split("\0") if f)


def throwaway_commit(checkout):
    """The SHA of a commit of the checkout's working tree (untracked files not ignored included) on top of its HEAD, made
    through a temporary index: no branch, no index, no file of the checkout changes."""
    with tempfile.TemporaryDirectory() as tmp:
        env = {**os.environ, "GIT_INDEX_FILE": str(Path(tmp) / "index"), "GIT_AUTHOR_NAME": "hillclimb", "GIT_AUTHOR_EMAIL": "hillclimb@localhost",
               "GIT_COMMITTER_NAME": "hillclimb", "GIT_COMMITTER_EMAIL": "hillclimb@localhost"}
        head = git(checkout, "rev-parse", "HEAD").strip()
        git(checkout, "read-tree", head, env=env)
        git(checkout, "add", "-A", env=env)
        tree = git(checkout, "write-tree", env=env).strip()
        return git(checkout, "commit-tree", tree, "-p", head, "-m", "implement-run-cost: working tree of an Attempt", env=env).strip()


# ---- Recorded runs ----------------------------------------------------------------------------------------------------

def recorded_runs(root=None):
    """The newest Recorded run of each Spec that has one; SystemExit with what to do when there is none."""
    newest = {}
    for folder in sorted(Path(root or RECORDED).glob("*/recorded.json")):
        recorded = json.loads(folder.read_text(encoding="utf-8"))
        newest[recorded["spec"]] = recorded  # run ids start with their timestamp, so the last in order is the newest
    if not newest:
        raise SystemExit(f"no Recorded run under {root or RECORDED}: record one first, with `python benchmark/run.py --record <spec-id>`")
    return [newest[spec] for spec in sorted(newest)]


def replay_jobs(recorded, roles):
    """(run id, dispatch, role) to replay: each dispatch of a replayed role that has a recorded verdict, then the seeded one when the Verifier is among them."""
    jobs = [(r["run_id"], str(d["n"]), d["role"]) for r in recorded for d in r["dispatches"] if d["role"] in roles and d["verdict"] is not None]
    return jobs + [(r["run_id"], "seeded", "verifier") for r in recorded if "verifier" in roles and r.get("seeded_dispatch")]


# ---- the running total ------------------------------------------------------------------------------------------------

def spent_so_far():
    try:
        return json.loads((SCRATCH / "spend.json").read_text(encoding="utf-8"))["total"]
    except (OSError, ValueError, KeyError):
        return 0.0


def ensure_scratch():
    """scratch/ beside the script, with its own .gitignore."""
    SCRATCH.mkdir(parents=True, exist_ok=True)
    if not (SCRATCH / ".gitignore").exists():
        (SCRATCH / ".gitignore").write_text("*\n", encoding="utf-8")


def add_spend(dollars):
    ensure_scratch()
    (SCRATCH / "spend.json").write_text(json.dumps({"total": spent_so_far() + dollars}), encoding="utf-8")


# ---- the numbers ------------------------------------------------------------------------------------------------------

def totals(fixed, units, runs):
    """(number, (low, high)) of one side. fixed is a cost held still; each unit is ({run: cost}, fallback): its median over
    the runs that produced a cost, else the fallback. The range is over the runs, a unit missing in one run at its median."""
    medians = [statistics.median(costs.values()) if costs else fallback for costs, fallback in units]
    per_run = [fixed + sum(costs.get(i, m) for (costs, _), m in zip(units, medians)) for i in range(runs)]
    number = fixed + sum(medians)
    return number, (min(per_run), max(per_run)) if per_run else (number, number)


def total_share(shares):
    """The weekly-limit share of a measurement: the sum over its runs, None when it has none or one has no value."""
    return None if not shares or None in shares else sum(shares)


def measure_replays(recorded, roles, sides, runs, claude):
    """One dict per side label, from replaying each job `runs` times alternating the sides."""
    jobs = replay_jobs(recorded, roles)
    attempts = {label: {job: {} for job in jobs} for label in sides}  # label -> job -> run index -> result dict, or {"error": why}
    for i in range(runs):
        for job in jobs:
            for label, checkout in sides.items():
                try:
                    result = replay.replay(job[0], job[1], checkout, claude, on_spend=add_spend)  # a Replay that fails still reports its spend
                except SystemExit as e:
                    result = {"error": f"could not run: {e.code}"}
                attempts[label][job][i] = result
    return {label: summarise_replays(recorded, got, runs) for label, got in attempts.items()}


def summarise_replays(recorded, attempts, runs):
    fixed, split, units, unit_roles = 0.0, dict.fromkeys(ROLE_ORDER, 0.0), [], []
    cost_of = lambda d: d["cost"]["cost_usd"] if d["cost"] else 0.0
    bucket = lambda role: role if role in metrics.ROLES else "other"
    for r in recorded:
        split["main"] += r["main_cost"]["cost_usd"]
        fixed += r["main_cost"]["cost_usd"]
        for d in r["dispatches"]:
            job = (r["run_id"], str(d["n"]), d["role"])
            if job in attempts:
                units.append(({i: a["cost"]["cost_usd"] for i, a in attempts[job].items() if "cost" in a}, cost_of(d)))
                unit_roles.append(bucket(d["role"]))
            else:
                fixed += cost_of(d)
                split[bucket(d["role"])] += cost_of(d)
    number, span = totals(fixed, units, runs)
    for (costs, fallback), role in zip(units, unit_roles):
        split[role] += (statistics.median(costs.values()) if costs else fallback)
    everything = [(job, a) for job, by_run in attempts.items() for a in by_run.values()]
    failed = [a.get("error") or a["reason"] for _, a in everything if "error" in a or not a["passed"]]
    shares = [a["limit_share"] for _, a in everything if "cost" in a]
    return side(number, span, runs, len(everything), len(failed), split, total_share(shares),
                f"{len(failed)} of {len(everything)} Replays failed: {failed[0]}" if failed else None)


def side(number, span, runs, work, errors, split, share, failure):
    """One side's result. A missing weekly-limit share counts as one error."""
    return {"number": number, "span": span, "runs": runs, "work": work, "errors": errors + (share is None), "split": split,
            "share": share, "failure": failure}


# ---- the rerun path ---------------------------------------------------------------------------------------------------

def rerun_argv(before_sha, after_sha, runs, spec_ids):
    return [sys.executable, str(run.HERE / "run.py"), "--baseline", before_sha, "--candidate", after_sha, "--runs", str(runs),
            "--specs", ",".join(spec_ids), "--model", "sonnet", "--effort", "high", "--claim", CLAIM, "--yes"]


def unscored_spend(sha):
    """The list-price dollars of the runs on sha that left a transcript but no score.json: the CSV has no row for them."""
    return sum(metrics.extract(meta.parent / "transcripts")["cost_usd"] for meta in sorted(RUNS.glob("*/meta.json"))
               if json.loads(meta.read_text(encoding="utf-8")).get("skills_sha", "").startswith(sha) and not (meta.parent / "score.json").exists())


def measure_rerun(spec_ids, checkouts, runs):
    """Rerun the Specs on the throwaway commits of both checkouts; one dict per side label."""
    shas = {label: throwaway_commit(path) for label, path in checkouts.items()}
    ensure_scratch()
    with open(SCRATCH / "run.out", "a", encoding="utf-8") as out:
        code = subprocess.run(rerun_argv(shas["before"], shas["after"], runs, spec_ids), stdout=out, stderr=subprocess.STDOUT).returncode
    rows = {}
    for label, sha in shas.items():
        try:
            rows[label] = compare.load_rows(sha[:12], RESULTS)
        except SystemExit:
            if not code:
                raise
            rows[label] = []  # run.py died before it wrote this side's CSV
    # the runs that finished count even when run.py failed, and so do the runs that spent money but left no score.json
    add_spend(sum(compare.num(r["cost_usd"]) or 0.0 for got in rows.values() for r in got) + sum(unscored_spend(sha) for sha in shas.values()))
    if code:
        raise SystemExit(f"run.py exited {code}: see {SCRATCH / 'run.out'}")
    out = {label: summarise_rerun(got, spec_ids, runs) for label, got in rows.items()}
    regressions = compare.regressions(compare.quality(rows["before"]), compare.quality(rows["after"]))
    if regressions and not out["after"]["failure"]:
        out["after"]["failure"] = "; ".join(regressions)
    return out


def summarise_rerun(rows, spec_ids, runs):
    valid = [r for r in rows if compare.is_true(r["valid"])]
    units = []
    split = dict.fromkeys(ROLE_ORDER, 0.0)
    for spec in spec_ids:
        mine = [r for r in valid if r["spec"] == spec]
        units.append(({int(r["index"]) - 1: compare.num(r["cost_usd"]) for r in mine if compare.num(r["cost_usd"]) is not None}, 0.0))
        for role in ROLE_ORDER:
            split[role] += statistics.median([compare.num(r[f"cost_{role}"]) or 0.0 for r in mine] or [0.0])
    number, span = totals(0.0, units, runs)
    broken = [r for r in rows if not compare.is_true(r["valid"]) or compare.is_true(r["failed"])]
    shares = [usage_share.share([RUNS / r["run_id"] / "usage.log"]) for r in rows]
    return side(number, span, runs, len(rows), len(broken), split, total_share(shares),
                f"{len(broken)} of {len(rows)} runs invalid or failed: {broken[0]['invalid_reasons'] or 'claude failed'}" if broken else None)


# ---- the plan and the line --------------------------------------------------------------------------------------------

def plan_text(path, roles, recorded, sides, runs):
    if path == "nothing":
        return "plan: measure nothing: no file under agents/ or skills/ changed"
    if path == "rerun":
        ids = [r["spec"] for r in recorded]
        return (f"plan: rerun {', '.join(ids)} in full: {runs} run(s) of each per side, {len(ids) * runs * len(sides)} /implement runs in all, "
                "through benchmark/run.py with --yes")
    jobs = replay_jobs(recorded, roles)
    per_run = "; ".join(f"{r['run_id']}: " + ", ".join(f"{sum(1 for j in jobs if j[0] == r['run_id'] and j[2] == role and j[1] != 'seeded')} {role}"
                                                       for role in roles) + (" + 1 seeded" if "verifier" in roles and r.get("seeded_dispatch") else "")
                        for r in recorded)
    return (f"plan: replay the {' and '.join(roles)} dispatches ({per_run}), {runs} time(s) per side: "
            f"{len(jobs) * runs * len(sides)} Replays in all")


def line(label, s, total):
    split = ", ".join(f"{role} ${s['split'][role]:.2f}" for role in ROLE_ORDER if role in metrics.ROLES or s["split"][role])
    share = f"{s['share']:.1f}% of the weekly limit (upper bound)" if s["share"] is not None else "no weekly-limit share"
    guard = f"FAILED ({s['failure']})" if s["failure"] else "passed"
    return (f"{label}: ${s['number']:.2f} per run summed over the Recorded runs (range ${s['span'][0]:.2f}-${s['span'][1]:.2f}), "
            f"{s['runs']} runs, work {s['work']}, errors {s['errors']}; {split}; {share}; total spent ${total:.2f}; guard: {guard}")


# ---- the command ------------------------------------------------------------------------------------------------------

def parse(argv):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("paths", nargs="+", help="<before> <after> [runs], or <checkout> [runs]")
    p.add_argument("--plan", action="store_true", help="print the path and what it would replay or rerun, and stop")
    p.add_argument("--claude", help="path to claude (default: PATH)")
    a = p.parse_args(argv)
    paths = list(a.paths)
    a.runs = int(paths.pop()) if len(paths) > 1 and paths[-1].isdigit() else 3
    if len(paths) not in (1, 2):
        p.error("expected <before> <after> [runs] or <checkout> [runs]")
    for path in paths:
        if not Path(path).is_dir():
            p.error(f"{path} is not a directory")
    if a.runs < 1:
        p.error("runs must be at least 1")
    a.sides = dict(zip(("before", "after") if len(paths) == 2 else ("checkout",), (str(Path(x).resolve()) for x in paths)))
    return a


def main(argv=None):
    a = parse(argv)
    if len(a.sides) == 2:
        path, roles = choose(changed_files(a.sides["before"], a.sides["after"]))
    else:
        path, roles = "replay", ("verifier", "reviewer")
    if path == "nothing":
        print(plan_text(path, roles, [], a.sides, a.runs))
        return 0
    recorded = recorded_runs()
    if a.plan:
        print(plan_text(path, roles, recorded, a.sides, a.runs))
        return 0
    if path == "replay":
        results = measure_replays(recorded, roles, a.sides, a.runs, [a.claude or shutil.which("claude") or "claude"])
    else:
        results = measure_rerun([r["spec"] for r in recorded], a.sides, a.runs)
    total = spent_so_far()
    for label, s in results.items():
        print(line(label, s, total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
