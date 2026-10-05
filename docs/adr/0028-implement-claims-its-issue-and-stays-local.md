# An implement run claims its Issue and otherwise stays local

An `/implement` run pushed a package release from a second repository and created live billing products, unattended, because a Step needed them and nothing said no. The run stays inside local working trees, this repository's or another's: nothing pushes, publishes, or changes an external system. Work a Spec puts in another repository goes on a branch named after the run there, committed and never pushed, and the final report names it. A Step that needs something published — a package, a deployed page, a live record — halts the run and says so.

The one write outside those working trees is the claim on the run's own Issue, made through the Tracker before the run does any other work. Several unattended runs can start from the same list of `ready-for-agent` Issues, and without a claim two of them build the same Issue. A run on an Issue another user has claimed stops and names them.

## Considered Options

- **The Step agent decides case by case.** Rejected: an unattended run has no one to weigh an irreversible action.
- **Asking the user mid-run.** Rejected: the run lands unattended by design, and a question stops it anyway — so it stops as a halt, which is resumable and leaves a record.
- **Whatever starts the runs claims the Issue.** Rejected: every scheduler would have to claim, and a run started by hand would still race one a scheduler started.
- **The run worktree's lock is the only claim.** Rejected: it is seen only by runs in the same repository on the same machine.
- **A status label marks the Issue as taken.** Rejected: an Issue carries one status at a time, and the status says where the Issue stands, not who holds it.

## Consequences

- The Planner plans another-repository work last and names its files by absolute path.
- Pushing the landed branch stays the user's action.
- The claim stays when the run halts or lands. A later run by the same user carries on past it; closing the Issue, or the user, clears it.
- The Tracker ref says how to claim an Issue. A ref that gives no claim for Issues leaves the run unclaimed. The local template gives none: its Issues live in the repository, so a claim written there would reach no session that the run's branch does not already reach.
