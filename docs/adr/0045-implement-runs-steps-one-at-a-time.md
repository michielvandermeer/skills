# `/implement` runs Steps one at a time

[ADR-0033](0033-implement-runs-ready-steps-in-parallel.md) let independent Steps run together, each in its own Step worktree off the run branch, rebased back onto it as it finished. In use it did not make runs noticeably faster, and it caused repeated trouble: Step worktrees are worktrees opened from inside a worktree, and some hosts confine a worktree session to its own tree, so the Driving session could not open them and Step agents could not reach them. We went back to the sequential run: Steps run strictly in `NN` order, one Step agent at a time, in the run worktree, each committing straight to the run branch. The numbering is the dependency order again, so Step files carry no `Blocked by:` line.

Keeping parallel Steps with a sequential fallback for confined hosts was rejected: it keeps two ways to run step 3, and the parallel one bought no speed worth that cost.

## Consequences

- There are no Step worktrees or Step branches, so there is no per-Step rebase and no per-Step cleanup. `/resolving-merge-conflicts` is used only at land.
- Resume resets the run worktree and restarts at the lowest-numbered Step not yet `done`.
- A waived worktree and the run worktree now run step 3 the same way.
- [ADR-0015](0015-implement-worktree-host-agnostic.md) still governs the run worktree.
- A Step file's `Depends on:` line names the earlier Steps whose Outcomes that Step reads. It never changes the order Steps run in, and it is not the `Blocked by:` edge this decision removed.
