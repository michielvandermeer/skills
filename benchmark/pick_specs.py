"""Pick the two mvdmio-suite Specs to record, from the real Claude Code session logs (#79).
Reads <root>/*/<session>.jsonl and the sub-agent logs next to them with compaction_logs.py, for the project folders of
mvdmio-suite, runs first recorded from --since on. A run that did not land is not a real implement run and is left out.
Prints one line per run: its Issue, Steps, Iterations, test runs and browser commands. Steps are
recount_compaction.run_steps; Iterations are the run's Verifier dispatches, a reduced verify after the rebase included
(a run with none counts its Reviewer dispatches, and at least 1); test runs and browser commands are the Verifiers' Bash
calls matching metrics.TEST_RE and tool calls whose name contains playwright. Then the median shape and the 90th-percentile shape over the
four counts, and the run nearest each. The distance is the sum over the four counts of the gap to the target value, each
gap divided by that count's median across all runs (a median of 0 divides by 1); the smallest distance wins and a tie
goes to the earlier run. A run with no browser command is skipped for the pick, and so is the run already picked for the
median. For each pick it prints the Issue and the commit the run started from (the parent of its landing commit, or
unresolved), as an entry for specs.yaml with landing, landing_lines, build and tests left as TODO.
Prints counts, Issue numbers and commits, never log text.
Usage: python benchmark/pick_specs.py [--root log-root] [--since YYYY-MM-DD]"""
import argparse
import sys
from datetime import datetime, timezone
from typing import NamedTuple

from compaction_logs import landing_parent, read_runs
from recount_compaction import DEFAULT_ROOT, run_steps
from recount_startup import percentile

PROJECT = "mvdmio-suite"
DEFAULT_SINCE = "2026-11-07"
COUNTS = ("steps", "iterations", "test runs", "browser commands")
BROWSER = COUNTS.index("browser commands")


class Row(NamedTuple):
    """One landed run: its Issue, the working directory its main session started in, and its four counts in COUNTS order."""
    issue: int
    cwd: str
    counts: tuple


def _date(text):
    """Midnight UTC of a YYYY-MM-DD date, as a timestamp."""
    return datetime.strptime(text, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()


def run_iterations(run):
    """The run's Verifier dispatches, whatever their prompts say; with none, its Reviewer dispatches; at least 1."""
    count = lambda role: sum(a["role"] == role for a in run["agents"])
    return count("verifier") or count("reviewer") or 1


def row_of(run):
    verifiers = [a for a in run["agents"] if a["role"] == "verifier"]
    return Row(run["issue"], run["cwd"], (run_steps(run), run_iterations(run), sum(a["test_runs"] for a in verifiers),
                                          sum(a["browser_commands"] for a in verifiers)))


def shape(rows, q):
    """The q-th percentile of each count over rows, in COUNTS order."""
    return tuple(percentile([row.counts[i] for row in rows], q) for i in range(len(COUNTS)))


def distance(row, target, medians):
    """The sum over the counts of the gap between row and target, each gap divided by that count's median (0 divides by 1)."""
    return sum(abs(c - t) / (m or 1) for c, t, m in zip(row.counts, target, medians))


def pick(rows, target, medians, taken=()):
    """The row nearest target among those with a browser command that are not in taken; the earliest of equals; None when
    no row qualifies."""
    eligible = [row for row in rows if row.counts[BROWSER] > 0 and row not in taken]
    return min(eligible, key=lambda row: distance(row, target, medians), default=None)


def _numbers(values):
    return ", ".join(f"{name} {value:g}" for name, value in zip(COUNTS, values))


def _entry(label, row):
    """The lines of a pick: which shape it is nearest and an entry for specs.yaml."""
    base = landing_parent(row.cwd, row.issue) or "unresolved"
    return [f"{label} pick: #{row.issue}, started from {base}",
            f"  - id: spec-{row.issue}", f"    issue: {row.issue}", f"    base: {base}",
            *(f"    {field}: TODO" for field in ("landing", "landing_lines", "build", "tests"))]


def report(rows):
    """The lines to print for rows, oldest run first: a line per run, the two shapes and the two picks."""
    median, p90 = shape(rows, 0.5), shape(rows, 0.9)
    lines = [f"#{row.issue}: " + ", ".join(f"{name} {n}" for name, n in zip(COUNTS, row.counts))
             + ("" if row.counts[BROWSER] else " (skipped: no browser command)") for row in rows]
    lines += [f"median shape: {_numbers(median)}", f"90th-percentile shape: {_numbers(p90)}"]
    first = pick(rows, median, median)
    second = pick(rows, p90, median, taken=[first])
    for label, chosen in (("median", first), ("90th-percentile", second)):
        lines += _entry(label, chosen) if chosen else [f"{label} pick: none, no run left with a browser command"]
    return lines


def main(argv):
    parser = argparse.ArgumentParser(prog="pick_specs.py", usage=__doc__.splitlines()[-1])
    parser.add_argument("--root", default=DEFAULT_ROOT)
    parser.add_argument("--since", type=_date, default=_date(DEFAULT_SINCE))
    args = parser.parse_args(argv)
    runs = read_runs(args.root, float("inf"), keep=lambda log: PROJECT in log.parent.name.lower())
    rows = [row_of(run) for run in sorted(runs, key=lambda r: r["first"]) if run["landed"] and run["first"] >= args.since]
    if not rows:
        sys.exit(f"no landed {PROJECT} run since {datetime.fromtimestamp(args.since, timezone.utc):%Y-%m-%d} under {args.root}")
    print("\n".join(report(rows)))


if __name__ == "__main__":
    main(sys.argv[1:])
