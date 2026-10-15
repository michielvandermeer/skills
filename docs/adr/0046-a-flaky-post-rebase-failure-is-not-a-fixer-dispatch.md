# A flaky post-rebase failure is not a fixer dispatch

[ADR-0029](0029-test-failures-are-measured-against-the-base-branch.md) measures a failure against the base branch, so a failure that branch already has is a Deviation, not the run's to fix. It does not cover a failure that is not on the base branch and is not caused by the branch either: a flaky test. In a run on the `mvdmio-suite` repo, the post-rebase run went red from two flaky tests, one after the other, in a project the branch never touched. Proving they were flaky took three project runs. A fixer dispatch would have been worse: it costs a full delegate run, finds nothing to fix, and spends one of the fix rounds the run allows before it halts.

`/implement` re-runs each project that failed after the post-rebase check, once, before treating the run as red. A failure that passes on the re-run is a flaky test: it is a Deviation, reported by test name in the final report, and does not block landing. A failure that fails again is red and goes to a fresh delegate; a third failure of the same check halts the run.

Checking the failure against the base branch at the merge-base first, the way ADR-0029 checks a pre-existing failure, was rejected: it also tells a flaky test from a real one, but it costs a build on another checkout, while a re-run costs one project run.

## Consequences

- The re-run is the Driving session's own command, not a delegate, and covers only the projects that failed, not the whole suite.
- **Deviation** covers a post-rebase failure that passed on the re-run.
- A fix round is spent only on a failure the re-run reproduced, so a flaky test cannot use one up and halt a run that was green.
- `/implement-yolo` has no rebase at land, so it is unaffected.
