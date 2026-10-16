# `/implement-yolo` is a second command

`/implement` can skip its worktree when the prompt asks, but that waived path still creates branch `<slug>` and still lands on the base branch. We wanted a command that implements a Spec on the session's current branch — a dirty tree included — with no worktree and no branch of its own. `/implement-yolo` is its own skill. It runs the same loop of Implement, Review, and Verify ([ADR-0072](0072-implement-is-a-loop-of-implement-review-verify.md)) in this checkout, removes the run folder, folds the run into one landing commit that carries the closing reference of the Issue it started from, if any ([ADR-0062](0062-an-implement-run-lands-as-one-commit.md)), and pushes and starts a Retrospective, all on this branch ([ADR-0054](0054-the-implement-commands-differ-only-in-worktree.md)).

A flag on `/implement` was rejected: a flag would hide "this checkout, this branch" inside a command that still means worktree, `<slug>` branch, and land. Extending the waived path to drop the branch was rejected: that path is the `/implement` run without a second working copy, and it still lands.

## Consequences

- Other skills do not start `/implement-yolo`.
- `/implement-yolo` joins the Named session skill list ([ADR-0038](0038-named-session-skills-apply-high-priority-retro.md)). The retro commit is on this branch; there is no merge.
- A dirty tree is the working copy. Uncommitted files may land in the Implementer's commits, and a retry never resets the tree. Detached HEAD halts. A run for the same slug in another worktree, or on branch `<slug>` while this checkout is on a different branch, halts, and a run folder in this checkout resumes. This checkout being on branch `<slug>` is not another run: it is the branch `/implement-yolo` works on.
- Leftover gaps, what a run claims and pushes, and green against the base branch apply as they do to `/implement` ([ADR-0026](0026-implement-agents-close-leftover-gaps.md), [ADR-0028](0028-implement-claims-its-issue-and-pushes-only-what-lands.md), [ADR-0029](0029-green-is-measured-against-the-base-branch.md)). Under `/implement-yolo` the base branch is the branch it works on, so its merge-base is the HEAD at the start of the run ([ADR-0055](0055-a-run-lands-on-the-branch-it-started-from.md)).
