# `/implement-yolo` is a second command

`/implement` works in a worktree on branch `<slug>` and lands on the base branch. We wanted a command that implements a Spec on the session's current branch, a dirty tree included, with no worktree and no branch of its own. `/implement-yolo` is its own skill, and its `SKILL.md` is a pointer: it runs `/implement`'s steps from `../implement/SKILL.md` with the worktree waived, `<start>` standing in for `<base>`, and the landing folded into one commit on this branch with `git reset --soft <start>` ([ADR-0054](0054-the-implement-commands-differ-only-in-the-worktree.md), [ADR-0062](0062-an-implement-run-lands-as-one-commit.md)). It then pushes and starts a Retrospective on this branch.

A flag on `/implement` was rejected: a `/goal` starts a command by its name ([ADR-0067](0067-the-implement-commands-are-model-invoked-so-a-goal-can-start-them.md)), and a flag would hide "this checkout, this branch" inside a command that still means worktree, `<slug>` branch, and land. A second full skill body was rejected: two copies of one flow drift, and an earlier fix to in-flight detection reached two sibling files and missed the third.

## Consequences

- Other skills do not start `/implement-yolo`.
- `/implement-yolo` joins the Named session skill list ([ADR-0038](0038-named-session-skills-apply-high-priority-retro.md)). The retro commit is on this branch; there is no merge.
- A dirty tree is the working copy. Uncommitted files may land in a unit's commit, and a resume never stashes or resets the tree. Detached HEAD halts. A run for the same slug in another worktree, or on branch `<slug>` while this checkout is on a different branch, halts, and a Run directory in this checkout with an open item resumes. This checkout being on branch `<slug>` is not another run: it is the branch `/implement-yolo` works on.
- Leftover gaps, what a run claims and pushes, and failures measured against the base branch apply as they do to `/implement` ([ADR-0026](0026-implement-agents-close-leftover-gaps.md), [ADR-0028](0028-implement-claims-its-issue-and-pushes-only-what-lands.md), [ADR-0029](0029-test-failures-are-measured-against-the-base-branch.md)). Under `/implement-yolo` the base branch is the branch it works on, so its merge-base is the HEAD at the start of the run ([ADR-0055](0055-a-run-lands-on-the-branch-it-started-from.md)).
- `/implement-yolo` has no benchmark mode ([ADR-0066](0066-a-benchmark-run-writes-nothing-outside-its-checkout.md)).
