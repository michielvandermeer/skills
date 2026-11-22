"""Count /implement runs and their Implementers in the Claude Code logs, to compare the Implementer's context and cost
before and after the skills commit 9356c58 (#61), which compacts an Implementer's context near a 200k window.

No flag: a before, after and mixed column of the same measures. before is the baseline selection below. after is a run whose
session names only plugin cache commits that contain 9356c58, or none and its first record is from that commit's push
(2026-11-07T04:50:16Z); mixed names both kinds; every other run is in no column. after and mixed end at SCAN_TIME_ISO.
Then the second baseline.
--baseline: the recovered #61 selection (top-level session logs written and first recorded from 2026-10-30 +01:00,
records up to 2026-11-07T00:23:26Z), its run, Implementer and cost counts and its measures table; then the second
baseline, the same selection kept to runs whose first record is at or after the standards cleanup, 2026-11-05 14:59 +01:00.
A run is one top-level session log with a sub-agent whose agentType is skills:planner, skills:implementer, skills:reviewer
or skills:verifier (no log records a typed /implement prompt as a display, so a session counts by its sub-agents only).
Reads <root>/*/<session>.jsonl and <root>/*/<session>/subagents/agent-*.jsonl with the agent-*.meta.json next to them,
for every project directory. Per window it also counts the runs that land (the main session ran a git commit with Closes #N), halt (wrote a
.agents/runs/<slug>/halt.md and did not land) or do neither, the Hard violations, Judgement calls and failed Verifies
per run, and the landing commits a later commit reverts, read from a read-only git log in the session's working directory.
For the after window only it counts the Implementers that compacted (a system record of subtype compact_boundary) and
how often, the context at and after each compaction, how often the host restored the builder's Step file, how many builders
read it again before their next change, and the Implementers that reported blocked after compacting, by run slug and agent id.
Then the measured saving of those compactions in dollars and as a share of the after window's spend, the mean builder cost of the
compaction group against the control group per Steps group before and after, and the Reviewer split per window and Reviewer model.
Then the verdict, keep the window or reopen it, with each condition that held and the raw counts behind it, and the noise list:
the commits in this repo and in mvdmio-suite since the before window's start that could have moved the numbers.
Prints counts, dates, commit subjects and model names, never log text.
Usage: python benchmark/recount_compaction.py [--baseline] [log-root]"""
import collections
import statistics
import sys
from datetime import datetime, timedelta, timezone
from fractions import Fraction
from pathlib import Path

from compaction_logs import _prices, read_runs
from metrics import _time
from plugin_windows import REPO_ROOT, _iso, commits_in_span, contains, listing, read_shas, split_windows
from recount import REPO_NOISE_PATHS, SUITE_ROOT
from recount_startup import SUITE_MODELS_PATHS, TRIAL_NOTE, TRIAL_SHA, _named, _share, percentile

DEFAULT_ROOT = Path.home() / ".claude" / "projects"
CET = timezone(timedelta(hours=1))  # the offset is written into the constants so a rerun on any machine agrees
BASELINE_START = datetime(2026, 10, 30, tzinfo=CET).timestamp()
BASELINE_END = _time("2026-11-07T00:23:26Z")  # the moment the original count ran; stands in for its missing end bound
CLEANUP_DONE = datetime(2026, 11, 5, 14, 59, tzinfo=CET).timestamp()  # the standards cleanup in mvdmio-suite finished
WINDOW_COMMIT = "9356c58"  # #61: the Implementer's compaction window
PUSHED = _time("2026-11-07T04:50:16Z")  # the push of 9356c58, from this checkout's origin/master reflog
SCAN_TIME_ISO = "2026-11-22T08:35:06Z"  # the UTC moment of the first run on the real logs; the after and mixed windows end here, never changed
SCAN_TIME = _time(SCAN_TIME_ISO)

STEP_GROUPS = [("0 (no builder)", 0, 0), ("1", 1, 1), ("2", 2, 2), ("3 to 4", 3, 4), ("5 to 7", 5, 7), ("8 or more", 8, 10**9)]
THRESHOLDS = (150_000, 200_000)  # a context is past one when it is strictly more
COMPACTION_PEAK = 165_000  # the host fired every after-window compaction between 165,576 and 180,954, so a builder strictly past this would have compacted
REOPEN_SAVING_UNDER = 0.02  # reopen the window when the measured saving is a smaller share of the after window's spend
REOPEN_ITERATION_3_OVER = 59  # percent of after runs of 3 or more Steps reaching Iteration 3: the Issue's baseline 49% plus 10 points, not recomputed
REOPEN_EXCESS = Fraction(1, 10)  # reopen when compacted runs reach Iteration 3 this much more often than the uncompacted runs of their Steps group
CALLED_OUT = {  # commit in this repo -> why the noise list names it
    "6bd7016": "#60, pushed 2026-11-07T01:47:33Z, shrinks every worker's start and so lowers both groups",
    "0f8254c": "#56, 2026-11-04; Step files grew from about 5k to about 15k characters from 2026-11-05, so the before window has smaller Steps"}
IN_COMPACTION_GROUP = {"before": lambda a: max((t["context"] for t in a["turns"]), default=0) > COMPACTION_PEAK,
                       "after": lambda a: bool(a["compactions"])}  # a builder is in the compaction group when it compacted, or would have


def baseline_runs(root, start=BASELINE_START, end=BASELINE_END):
    """The runs whose log was written and whose first record was made at or after start, records up to end."""
    return [r for r in read_runs(root, end, keep=lambda log: log.stat().st_mtime >= start) if r["first"] >= start]


def run_steps(run):
    return max((a["steps"] for a in run["agents"] if a["step"] is not None), default=0)


def run_iteration(run):
    return max((a["iteration"] for a in run["agents"] if a["iteration"] is not None), default=0)


def run_cost(run):
    return run["main_cost"] + run["subagent_cost"]


def _implementers(runs):
    return [a for run in runs for a in run["agents"] if a["role"] == "implementer"]


def _money(amount):
    amount = round(amount, 2) + 0.0  # a change that rounds to nothing prints $0.00, never -$0.00
    return f"-${-amount:,.2f}" if amount < 0 else f"${amount:,.2f}"


def measures(runs):
    """[(measure, value)] over a list of runs, the rows later Steps lay out per window."""
    implementers = _implementers(runs)
    implementer_cost = sum(t["cost"] for a in implementers for t in a["turns"])
    peaks = [max(t["context"] for t in a["turns"]) for a in implementers if a["turns"]]
    rows = [("runs", str(len(runs))), ("Implementers", str(len(implementers))),
            ("Implementer cost", _money(implementer_cost)), ("total cost", _money(sum(map(run_cost, runs))))]
    rows += [(f"Implementer peak context {name}", "-" if not peaks else f"{value:.0f}")
             for name, value in (("p50", percentile(peaks, 0.5)), ("p90", percentile(peaks, 0.9)),
                                 ("p99", percentile(peaks, 0.99)), ("max", max(peaks, default=0)))]
    for limit in THRESHOLDS:
        past = sum(p > limit for p in peaks)
        above = sum(t["cost"] for a in implementers for t in a["turns"] if t["context"] > limit)
        rows += [(f"Implementers past {limit // 1000}k", _share(past, len(implementers))),
                 (f"cost of turns above {limit // 1000}k",
                  f"{_money(above)} ({above / implementer_cost:.0%} of Implementer cost)" if implementer_cost else _money(above))]
    big = [r for r in runs if run_steps(r) >= 3]
    rows += [(f"runs of 3 or more Steps reaching Iteration {n}", _share(sum(run_iteration(r) >= n for r in big), len(big)))
             for n in (2, 3)]
    for name, low, high in STEP_GROUPS:
        costs = [run_cost(r) for r in runs if low <= run_steps(r) <= high]
        rows.append((f"Steps {name} runs", str(len(costs))))
        rows += [(f"Steps {name} median run cost", _money(statistics.median(costs)) if costs else "-"),
                 (f"Steps {name} mean run cost", _money(statistics.fmean(costs)) if costs else "-")]
    return rows + _outcome_rows(runs)


def _outcome_rows(runs):
    """How the runs ended, the findings and failed Verifies per run, and the reverted landing commits."""
    agents = [a for run in runs for a in run["agents"]]
    landed, halted = sum(r["landed"] for r in runs), sum(r["halted"] for r in runs)
    per_run = lambda count: f"{count / len(runs):.2f}" if runs else "-"
    landings = [r["landing"] for r in runs]
    return [("runs that land", _share(landed, len(runs))), ("runs that halt", _share(halted, len(runs))),
            ("runs that do neither", _share(len(runs) - landed - halted, len(runs))),
            ("Hard violations per run", per_run(sum(a["findings"]["Hard violation"] for a in agents if a["role"] == "reviewer"))),
            ("Judgement calls per run", per_run(sum(a["findings"]["Judgement call"] for a in agents if a["role"] == "reviewer"))),
            ("failed Verifies per run", per_run(sum(a["status"] == "failed" for a in agents if a["role"] == "verifier"))),
            ("reverted landing commits", f"{landings.count('reverted')} ({landings.count('unread')} unread)")]


def _table(runs):
    return [f"{name:<50}{value}" for name, value in measures(runs)]


def second_baseline(before):
    """The second baseline as text: the baseline selection kept to runs first recorded from the standards cleanup."""
    return "\n".join([f"second baseline: the same selection, first record from {_iso(CLEANUP_DONE)}",
                      *_table([r for r in before if r["first"] >= CLEANUP_DONE])])


def baseline_report(root):
    """The recovered #61 selection with its measures, then the second baseline, as text."""
    runs = baseline_runs(root)
    return "\n".join([f"baseline: top-level session logs written and first recorded from {_iso(BASELINE_START)}, "
                      f"records up to {_iso(BASELINE_END)}", *_table(runs), second_baseline(runs)])


def windowed_runs(root, scan, contains):
    """({window: [run]}, unresolved SHAs) with window in before, after, mixed. before is the baseline selection;
    after and mixed are what split_windows makes of the runs with records up to scan, by the plugin cache SHAs their
    session names and contains (a SHA to True, False or None). Every other run is in no window."""
    seen = {}
    for run in read_runs(root, scan):
        shas, _ = read_shas(Path(root) / run["project"], run["session"], scan)
        seen[(run["project"], run["session"])] = (run, shas, run["first"])
    windows, unresolved = split_windows(seen, contains, PUSHED)
    return {"before": baseline_runs(root), "after": list(windows["after"].values()), "mixed": list(windows["mixed"].values())}, unresolved


def window_report(windows, unresolved, scan=SCAN_TIME):
    """The window bounds and the measures table, a column per window, as text."""
    columns = {name: measures(runs) for name, runs in windows.items()}
    lines = [f"windows: before = top-level session logs written and first recorded from {_iso(BASELINE_START)}, records up to "
             f"{_iso(BASELINE_END)}; after = SHAs all with {WINDOW_COMMIT}, or none and first record from {_iso(PUSHED)}; "
             f"mixed = SHAs both with and without it; all end at scan time {_iso(scan)}; unresolved SHAs {len(unresolved)}",
             f"{'measure':<50}" + "".join(f"{name:>38}" for name in columns)]
    lines += [f"{row:<50}" + "".join(f"{column[i][1]:>38}" for column in columns.values())
              for i, (row, _) in enumerate(next(iter(columns.values())))]
    return "\n".join(lines)


def _spread(values):
    """min, median and max of values as text, dashes when there are none."""
    return "-" if not values else f"{min(values):.0f} / {statistics.median(values):.0f} / {max(values):.0f}"


def compaction_report(runs):
    """The compactions of the Implementers of runs (the after window) as text: how many compacted and how many times, the
    context at each compaction and on the first turn after it, the share restored with the Step file and the share of
    compacted builders that read it again, and the Implementers that reported blocked after compacting, by run slug and agent id."""
    implementers = [(run, a) for run in runs for a in run["agents"] if a["role"] == "implementer"]
    compacted = [(run, a) for run, a in implementers if a["compactions"]]
    compactions = [c for _, a in compacted for c in a["compactions"]]
    builders = [a for _, a in compacted if a["step"] is not None]
    times = collections.Counter(len(a["compactions"]) for _, a in compacted)
    blocked = [(run["slug"], a["id"]) for run, a in compacted if a["blocked"]]
    builder_compactions = [c for a in builders for c in a["compactions"]]
    rows = [("compacted Implementers", _share(len(compacted), len(implementers))),
            ("Implementers by compactions", ", ".join(f"{n}: {times[n]}" for n in sorted(times)) or "-"),
            ("context at compaction min / median / max", _spread([c["before"] for c in compactions])),
            ("context after compaction min / median / max", _spread([c["after"] for c in compactions if c["after"] is not None])),
            ("builder compactions with the Step file restored", _share(sum(c["restored"] for c in builder_compactions), len(builder_compactions))),
            ("compacted builders reading the Step file again", _share(sum(any(c["read_again"] for c in a["compactions"]) for a in builders), len(builders))),
            ("Implementers blocked after a compaction", str(len(blocked)))]
    return "\n".join(["compactions in the after window", *(f"{name:<50}{value}" for name, value in rows),
                      *(f"  {slug} {agent}" for slug, agent in blocked)])


def compaction_saving(implementers):
    """USD the compactions of implementers saved. Each compaction with a later turn drops (preTokens - context after) tokens
    from every turn from the first one after it to the last, priced at the cache-read rate of that first turn's model, and
    costs its own request (preTokens read, the context after written as output, as the log holds no usage record for it)
    and the cache write of that first turn. A later compaction stacks on an earlier one: each applies to its own later turns."""
    saved = 0.0
    for implementer in implementers:
        turns = implementer["turns"]
        for c in (c for c in implementer["compactions"] if c["after"] is not None):
            first = turns[c["place"]]
            _, output, read, write_5m, write_1h = _prices(first["model"])
            saved += ((c["before"] - c["after"]) * read * (len(turns) - c["place"]) - c["before"] * read - c["after"] * output
                      - first["cache_5m"] * write_5m - first["cache_1h"] * write_1h) / 1e6
    return saved


def saving_report(runs):
    """The measured saving of the compactions of the Implementers of runs (the after window), in dollars and as a share
    of the window's total spend, every role included, as text."""
    saved, spend = _saving_and_spend(runs)
    share = f"{saved / spend:.1%}" if spend else "-"
    return f"measured saving of the compactions in the after window: {_money(saved)}, {share} of the window's spend of {_money(spend)}"


def _saving_and_spend(runs):
    return compaction_saving(_implementers(runs)), sum(map(run_cost, runs))


def _builder_costs(runs, window, low, high, grouped):
    """The cost of each builder (an Implementer with a Step) of the runs whose Steps are low to high, in the compaction
    group of window when grouped, else in the control group."""
    return [sum(t["cost"] for t in a["turns"]) for r in runs if low <= run_steps(r) <= high for a in r["agents"]
            if a["role"] == "implementer" and a["step"] is not None and IN_COMPACTION_GROUP[window](a) == grouped]


def comparison_rows(before, after):
    """[(Steps group, [cell])] with the cells: mean builder cost of the compaction group before and after, its change, the
    same for the control group, and the compaction group's change minus the control group's. The 0 group has no builders.
    A cell with no builder, or a change needing one, is None."""
    rows = []
    for name, low, high in STEP_GROUPS[1:]:
        cells = []
        for grouped in (True, False):
            costs = [statistics.fmean(c) if c else None
                     for c in (_builder_costs(before, "before", low, high, grouped), _builder_costs(after, "after", low, high, grouped))]
            cells += costs + [None if None in costs else costs[1] - costs[0]]
        rows.append((name, cells + [None if None in (cells[2], cells[5]) else cells[2] - cells[5]]))
    return rows


def comparison_report(before, after):
    """The builder cost per Step of the compaction group against the control group, per Steps group and window, as text."""
    heads = ["compaction before", "compaction after", "compaction change", "control before", "control after", "control change", "difference"]
    cell = lambda value: "-" if value is None else _money(value)
    return "\n".join(["mean builder cost, compaction group against control group",
                      f"{'Steps':<12}" + "".join(f"{head:>19}" for head in heads),
                      *(f"{name:<12}" + "".join(f"{cell(value):>19}" for value in cells) for name, cells in comparison_rows(before, after)),
                      "#60, the Sonnet Reviewer trial, and the standards cleanup reach both groups; compaction reaches only one."])


def reviewer_split(runs):
    """[(Reviewer models, [runs, runs reaching Iteration 2, runs reaching Iteration 3, Hard violations per run, Judgement calls
    per run])] over runs, one row per set of models the Reviewers of a run ran on, named by the models joined. A run with no
    Reviewer is in no row."""
    by_models = collections.defaultdict(list)
    for run in runs:
        models = sorted({a["model"] or "unknown" for a in run["agents"] if a["role"] == "reviewer"})
        if models:
            by_models[" + ".join(models)].append(run)
    per_run = lambda group, kind: f"{sum(a['findings'][kind] for r in group for a in r['agents'] if a['role'] == 'reviewer') / len(group):.2f}"
    return [(models, [str(len(group)), *(_share(sum(run_iteration(r) >= n for r in group), len(group)) for n in (2, 3)),
                      per_run(group, "Hard violation"), per_run(group, "Judgement call")])
            for models, group in sorted(by_models.items())]


def reviewer_report(windows):
    """The Reviewer split of every window as text, a row per window and set of Reviewer models."""
    heads = ["runs", "Iteration 2", "Iteration 3", "Hard per run", "Judgement per run"]
    return "\n".join(["Reviewer model split", f"{'window':<8}{'Reviewer models':<42}" + "".join(f"{head:>20}" for head in heads),
                      *(f"{window:<8}{models:<42}" + "".join(f"{cell:>20}" for cell in cells)
                        for window, runs in windows.items() for models, cells in reviewer_split(runs))])


def verdict_groups(runs):
    """{Steps group: (compacted runs, of them reaching Iteration 3, uncompacted runs, of them reaching Iteration 3)} over the
    runs of 3 or more Steps; a compacted run has an Implementer that compacted."""
    groups = {}
    for name, low, high in STEP_GROUPS[3:]:
        in_group = [r for r in runs if low <= run_steps(r) <= high]
        has_compacted = lambda run: any(a["compactions"] for a in run["agents"] if a["role"] == "implementer")
        compacted = [r for r in in_group if has_compacted(r)]
        plain = [r for r in in_group if not has_compacted(r)]
        groups[name] = tuple(n for rs in (compacted, plain) for n in (len(rs), sum(run_iteration(r) >= 3 for r in rs)))
    return groups


def verdict(saving, spend, groups):
    """("reopen it" or "keep the window", [each condition that held, with its figures], [groups left out of the third
    condition]). Reopen when the saving is under REOPEN_SAVING_UNDER of the spend (a spend of 0 gives a share of 0), when
    over REOPEN_ITERATION_3_OVER percent of the runs of 3 or more Steps reach Iteration 3, or when the compacted runs
    reach it REOPEN_EXCESS or more above the average, over those runs, of the rate of the uncompacted runs of their Steps
    group. A group with compacted runs and no uncompacted ones is left out of the third condition. groups is verdict_groups."""
    held, share = [], saving / spend if spend else 0.0
    if share < REOPEN_SAVING_UNDER:
        held.append(f"the measured saving {_money(saving)} is {share:.1%} of the spend {_money(spend)}, under {REOPEN_SAVING_UNDER:.0%}")
    big, reached = sum(g[0] + g[2] for g in groups.values()), sum(g[1] + g[3] for g in groups.values())
    if reached * 100 > REOPEN_ITERATION_3_OVER * big:
        held.append(f"{_share(reached, big)} of the after runs of 3 or more Steps reach Iteration 3, over {REOPEN_ITERATION_3_OVER}%")
    left_out = [name for name, g in groups.items() if g[0] and not g[2]]
    used = [g for g in groups.values() if g[0] and g[2]]
    compacted, compacted_reached = sum(g[0] for g in used), sum(g[1] for g in used)
    if compacted:
        actual = Fraction(compacted_reached, compacted)
        expected = sum(g[0] * Fraction(g[3], g[2]) for g in used) / compacted
        if actual - expected >= REOPEN_EXCESS:
            held.append(f"the compacted runs reach Iteration 3 in {float(actual):.1%} ({compacted_reached}/{compacted}), "
                        f"{float(actual - expected) * 100:.1f} points above the expected {float(expected):.1%}, "
                        f"at least {float(REOPEN_EXCESS) * 100:.0f}")
    return ("reopen it" if held else "keep the window"), held, left_out


def verdict_report(runs):
    """The verdict on the after window's runs, each condition that held with its figures, the groups left out and the raw
    counts behind it, as text. The mixed window and the runs in no window never reach it."""
    saving, spend = _saving_and_spend(runs)
    groups = verdict_groups(runs)
    word, held, left_out = verdict(saving, spend, groups)
    lines = [f"verdict: {word}", *(f"  held: {condition}" for condition in held)]
    if left_out:
        lines.append(f"  left out of the compacted runs condition, no uncompacted runs: {', '.join(left_out)}")
    lines += ["raw counts:", f"  saving {_money(saving)}, spend {_money(spend)}",
              f"  after runs of 3 or more Steps: {sum(g[0] + g[2] for g in groups.values())}, "
              f"reaching Iteration 3: {sum(g[1] + g[3] for g in groups.values())}",
              f"  compacted runs: {sum(g[0] for g in groups.values())}, reaching Iteration 3: {sum(g[1] for g in groups.values())}",
              *(f"  Steps {name}: uncompacted runs {g[2]}, reaching Iteration 3: {g[3]}" for name, g in groups.items())]
    return "\n".join(lines)


def noise_report(repo=REPO_ROOT, suite=SUITE_ROOT, scan=SCAN_TIME):
    """The other changes from the before window's start to scan that could have moved the numbers, as text: commits in this
    repo and in mvdmio-suite, each section as the sibling recount scripts print it, with the commits called out."""
    span = f"{_iso(BASELINE_START)} to {_iso(scan)}"
    return "\n".join([
        *listing(f"skills commits touching the implement, code-review or agent files, {span}",
                 commits_in_span(repo, BASELINE_START, scan, REPO_NOISE_PATHS)),
        *(_named(repo, sha, note) for sha, note in CALLED_OUT.items()),
        *listing(f"mvdmio-suite commits touching the models ref, {span}", commits_in_span(suite, BASELINE_START, scan, SUITE_MODELS_PATHS)),
        _named(suite, TRIAL_SHA, TRIAL_NOTE)])


def main(argv):
    flags = [a for a in argv if a.startswith("--")]
    args = [a for a in argv if not a.startswith("--")]
    if len(args) > 1 or flags not in ([], ["--baseline"]):
        sys.exit(__doc__)
    root = args[0] if args else DEFAULT_ROOT
    if flags:
        print(baseline_report(root))
        return
    windows, unresolved = windowed_runs(root, SCAN_TIME, lambda sha: contains(WINDOW_COMMIT, sha))
    print(window_report(windows, unresolved))
    print(second_baseline(windows["before"]))
    print(compaction_report(windows["after"]))
    print(saving_report(windows["after"]))
    print(comparison_report(windows["before"], windows["after"]))
    print(reviewer_report(windows))
    print(verdict_report(windows["after"]))
    print(noise_report())


if __name__ == "__main__":
    main(sys.argv[1:])
