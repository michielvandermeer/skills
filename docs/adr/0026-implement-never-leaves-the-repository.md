# `/implement` never leaves the repository

An `/implement` run pushed a package release from a second repository and created live billing products, unattended, because a Step needed them and nothing said no. The run now stays inside local working trees, this repository's or another's: nothing pushes, publishes, or changes an external system. Work a Spec puts in another repository goes on a branch named after the run there, committed and never pushed, and the final report names it. A Step that needs something published — a package, a deployed page, a live record — halts the run and says so.

Letting the Step agent decide case by case was rejected: an unattended run has no one to weigh an irreversible action. Asking the user mid-run was rejected: the run lands unattended by design, and a question stops it anyway — so it stops as a halt, which is resumable and leaves a record.

## Consequences

- The Planner plans another-repository work last and names its files by absolute path.
- Pushing the landed branch stays the user's action.
