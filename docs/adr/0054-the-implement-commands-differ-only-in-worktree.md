# The implement commands differ only in worktree

`/implement` and `/implement-yolo` run the same loop of Implement, Review, and Verify over the whole Spec ([ADR-0072](0072-implement-is-a-loop-of-implement-review-verify.md)), with the same `skills:implementer`, `/code-review`, and `skills:verifier`. `/implement` runs it in a worktree on branch `<slug>` and lands on the base branch; `/implement-yolo` runs it in this checkout on this branch and folds it into one commit there. `/implement-yolo` reads the loop from `/implement`'s step 2 rather than keeping a copy.

## Considered Options

- **A copy of the loop in each command.** Rejected: two copies of one contract drift apart, as the in-flight check did when the commands kept their own.

## Consequences

- An edit to the loop is one edit, in `/implement`. An edit to a rule both commands spell out — in-flight detection, resume, cleanup — changes both in the same commit.
- `/implement-yolo` commits the Spec copy on your branch, and folding the run into its landing commit removes it. A retry there never resets the tree.
