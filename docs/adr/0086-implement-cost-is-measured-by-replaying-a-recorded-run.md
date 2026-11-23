# The cost of an `/implement` run is measured by replaying a Recorded run

A Hillclimb on what an `/implement` run costs measures each Attempt against a **Recorded run**, not against fresh runs of the whole Spec. An Attempt that changes only the Verifier's or the Reviewer's agent file reruns only their dispatches as **Replays**, on the commits and with the prompts the Recorded run kept, and counts every other dispatch at its recorded cost. Any other skills change runs the whole Spec again through `benchmark/run.py`. A change to the Implementer or the Planner reaches every dispatch after it. A change to the `/implement` or `/code-review` text reaches the Reviewer and the Verifier through the prompt the main session writes, which a Replay holds fixed.

Fresh runs vary too much to see the savings this effort is after. In mvdmio-suite, 45% of runs of 3 or more Steps reach Iteration 3 ([ADR-0072](0072-implement-plans-steps-then-loops-implement-review-verify.md)), so one run of a Spec can cost two to three times another. `/hillclimb` keeps a change only when it moves the number past the run-to-run spread, at 3 to 10 runs per side ([ADR-0061](0061-hillclimb-keeps-only-measured-wins.md)), and at that spread a 20% saving cannot show. A realistic run also costs $20 to $30 at list price, and each measurement takes at least 6, so the search would use up much of the usage limit it is meant to protect. A Replay holds the Iteration count fixed and costs only the dispatches the Attempt changed.

Two mvdmio-suite Specs are recorded: one at the median shape of real runs and one at the 90th percentile, measured by Steps, Iterations, test runs, and browser commands. Both have Hand checks that drive the browser. The number is list-price dollars per run, split by role. #79's weights (new input 1, cache write 1.25, cache read 0.1, output 5, times Haiku 1, Sonnet 3, Opus 5) are the list-price ratios, and tokens are kept by kind, so other weights can be applied to the same runs later.

## Considered Options

- **Repeat fresh full runs of a realistic Spec for every Attempt.** Rejected: the variance from Iteration count hides a 20% saving, and each Attempt costs 6 or more realistic runs.
- **Replay real mvdmio-suite sessions from their logs.** Rejected: a run's commits are squashed into its Landing commit at land, so the commit a dispatch started on is gone.
- **Ship one idea at a time and recount it from real session logs, as #63 did for the compaction window.** Rejected for this effort: it costs no usage, but each idea takes weeks of real runs, and the mix of Specs changes between windows.
- **A small synthetic Spec.** Rejected: the cost sits in long runs with many turns, and a small Spec has few.

## Consequences

- A Replay passes the quality guard only when it reaches the recorded verdict and raises every recorded finding. A Sonnet judge matches the findings, because they are prose. A full rerun passes when `score.py` finds it valid and `compare.py` finds no regression.
- Each Recorded run carries one seeded Verify dispatch: its landed change with one hunk the Spec needs reverted. Every Replay of it must report a finding, so an Attempt that lets a broken change land is rejected.
- `/hillclimb` takes a spend limit next to its time limit. For a number whose measurement runs Claude sessions it is required, with no default, and is checked against the measure script's running total after each measurement.
- A Replay is blind to an effect that changes how many Iterations a run needs, beyond the recorded verdict. Before the Hillclimb lands, its final check runs both Specs in full on each side.
