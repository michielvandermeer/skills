# A run lands on the branch it started from

`/implement` and `/implement-oneshot` rebased onto `master` and fast-forwarded `master`, and Green was measured against `master` ([ADR-0029](0029-green-is-measured-against-master.md)). A run started on a feature branch therefore left that branch: the run's commits, and every commit the feature branch had over `master`, landed on `master`. Every implement command now works against the **base branch**: the branch the original directory is on when the command starts, read again on a resume. The run branches from it, is reviewed and measured Green against it, and lands back on it. A detached HEAD has no base branch, so the run halts, as `/implement-yolo` already did.

## Considered Options

- **The repository's default branch, unless the prompt names another.** Rejected: the user already chose a branch by checking it out, and a run that leaves it surprises them.
- **Recording the base branch in the Step files at the start.** Rejected: the Planner and the oneshot Step file would carry a field only the land reads. A resume reads the branch the user is on now, which is what they want it to land on.

## Consequences

- A fresh worktree is reset to the base branch, not rebased onto it: its branch has no commits of its own yet, and a host tool may have created it from another branch.
- Under `/implement-yolo` the base branch is the branch it works on, so its merge-base is the HEAD at the start of the run.
- `/retro` judges a new check against the current branch.
