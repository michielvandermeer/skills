# `/implement-yolo` is a third command

`/implement-oneshot` already skips the Planner, and it already skips a worktree when the prompt asks. That waived path still creates branch `<slug>` and still merges onto master. We wanted a command that implements a Spec on the session's current branch — dirty tree and `master` included — with no worktree and no branch of its own. We added `/implement-yolo` as its own user-invoked skill: one Oneshot agent implements the whole Spec in this checkout, then the Driving session runs the same review, improve, and document sequence, deletes the Spec, and starts a Retrospective, all on this branch. `/implement` and `/implement-oneshot` are unchanged.

A flag on `/implement-oneshot` was rejected: [ADR-0031](0031-implement-oneshot-is-a-second-command.md) already made variants second commands, and a flag would hide "this checkout, this branch" inside a command that still means worktree, `<slug>` branch, and land. Extending the waived path to drop the branch was rejected: that path is the oneshot run without a second working copy, and it still lands.

## Consequences

- Other skills do not start `/implement-yolo`.
- `/implement-yolo` joins the Named session skill list ([ADR-0038](0038-named-session-skills-apply-high-priority-retro.md)). The retro commit is on this branch; there is no land.
- A dirty tree is the working copy. Uncommitted files may land in the Oneshot agent's commits. Detached HEAD halts. An `/implement` or `/implement-oneshot` already in flight for the same slug halts.
- Leftover gaps, local-only, and green-against-master apply as they do to `/implement-oneshot` ([ADR-0026](0026-implement-agents-close-leftover-gaps.md), [ADR-0028](0028-implement-never-leaves-the-repository.md), [ADR-0029](0029-green-is-measured-against-master.md)). When the session is on `master`, green is measured against the HEAD at the start of the run.
