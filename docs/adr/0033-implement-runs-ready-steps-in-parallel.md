# `/implement` runs Ready Steps in parallel

`/implement` used to run Step agents one at a time in a shared worktree because the numbering was the dependency order and two editors cannot share a tree. Independent Steps now run together: the Planner records real `Blocked by:` edges, each Ready Step gets its own worktree off the run branch, and the Driving session rebases it onto the run branch so that branch stays a linear commit stack. The highest-numbered Step still waits for every other Step and leaves the whole suite green. A waived worktree stays sequential, because there is only one checkout. A confined host stays sequential too — see [ADR-0045](0045-implement-stays-sequential-on-a-confined-host.md).

A merge commit per Step was rejected: land is still rebase onto `master` and fast-forward, and rebasing merge commits is a different operation. Inferring independence from footprint overlap at dispatch time was rejected: the Planner already walked the code, and overlapping footprints are a blocking edge it writes down. A merger sub-agent on every rebase was rejected: a clean rebase is the Driving session's, and a conflict is `/resolving-merge-conflicts`.

## Consequences

- Resume enters the run worktree (branch `<slug>`), not a Step worktree (`<slug>-<NN>`).
- A second failure on one Step stops new dispatch; in-flight siblings finish or fail, then the session ends.
- [ADR-0015](0015-implement-worktree-host-agnostic.md) still governs the run worktree. Step worktrees are always `git worktree add`; a host enter-tool would move the Driving session.
