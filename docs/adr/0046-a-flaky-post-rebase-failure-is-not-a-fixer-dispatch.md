# A flaky post-rebase failure is not a fixer dispatch

[ADR-0029](0029-green-is-measured-against-master.md) made **Green** a comparison against `master`, so a failure `master` already has is a Deviation, not the run's to fix. It does not cover a failure that is not on `master` and is not caused by the branch either: a flaky test. In a run on the `mvdmio-suite` repo, the post-rebase run went red from two flaky tests, one after the other, in a project the branch never touched. Proving they were flaky took three project runs. A fixer dispatch would have been worse: it costs a full sub-agent run, finds nothing to fix, and uses up the one retry the retry-then-halt rule allows.

`/implement` and `/implement-oneshot` now re-run each project that failed after the post-rebase build, once, before treating the run as red. A failure that passes on the re-run is a flaky test: it is a Deviation, reported by test name on the deviations line and in the final report, and does not block landing. A failure that fails again is red and gets the one fixer dispatch the retry-then-halt rule allows, as before.

Checking the failure against `master` at the merge-base first, the way ADR-0029 checks a pre-existing failure, was rejected: it also tells a flaky test from a real one, but it costs a build on another checkout, while a re-run costs one project run.

## Consequences

- The re-run is the Driving session's own command, not a sub-agent, and covers only the projects that failed, not the whole suite.
- **Deviation** now also covers a post-rebase failure that passed on the re-run.
- The fixer's one retry is spent only on a failure the re-run reproduced, so a flaky test cannot use it up and halt a run that was green.
- `/implement-yolo` has no rebase at land, so it is unaffected.
