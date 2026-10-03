# An implement run leaves the repository only for its pull request

A run of `/implement`, `/implement-oneshot`, or `/implement-yolo` stays inside local working trees, this repository's or another's: nothing pushes, publishes, or changes an external system. An unattended run once pushed a package release from a second repository and created live billing products, because a Step needed them and nothing said no. Work a Spec puts in another repository goes on a branch named after the run there, committed and never pushed, and the final report names it. A Step that needs something published — a package, a deployed page, a live record — halts the run and says so.

A Spec on a GitHub issue is the one exception, and it covers three acts: pushing the run's own branch or the grilling draft's branch, opening the run's pull request, and marking the grilling draft ready for review. That pull request is how the change reaches review. A person still merges it, so nothing irreversible happens unattended, and the merge closes the issue through `Closes #N`.

## Considered Options

- **Letting the Step agent decide case by case.** Rejected: an unattended run has no one to weigh an irreversible action.
- **Asking the user mid-run.** Rejected: the run lands unattended by design, and a question stops it anyway — so it stops as a halt, which is resumable and leaves a record.
- **Closing the issue from the run.** Rejected: the issue would close before anyone merged the work, and a pull request closed unmerged must leave it open.

## Consequences

- The Planner plans another-repository work last and names its files by absolute path.
- A GitHub-issue run checks push and pull-request rights before it starts and halts without them. It never force-pushes, never closes the issue, and edits nothing on it, so `ready-for-agent` stays until the merge.
- For a Spec in the repo, pushing the landed branch stays the user's action.
