# `/implement-yolo` is a third command

`/implement-oneshot` already skips the Planner, and it skips a worktree when the prompt asks. We wanted a command that implements a Spec in the session's own checkout and takes the tree as it is — uncommitted files included — as the working copy. `/implement-yolo` is its own user-invoked skill. It cuts a branch of its own in this checkout and carries the uncommitted files onto it. Its Driving session writes one Step file for the whole Spec, and the Step agent and Checker run that Step there. It then runs the same review, improve and document sequence and deletes the Spec and the Step file ([ADR-0054](0054-the-implement-commands-differ-only-in-planning-and-worktree.md)). For a Spec in the repo the branch starts from the current branch and lands back on it: rebase, fast-forward, delete the branch ([ADR-0055](0055-a-run-lands-on-the-branch-it-started-from-or-opens-a-pull-request.md)). For a Spec on a GitHub issue it starts from the default branch or the grilling draft and ends in a pull request, as the other commands do ([ADR-0028](0028-an-implement-run-leaves-the-repository-only-for-its-pull-request.md)).

## Considered Options

- **A flag on `/implement-oneshot`.** Rejected: [ADR-0031](0031-implement-oneshot-is-a-second-command.md) already made variants second commands, and a flag would hide "this checkout, these uncommitted files" inside a command that means a clean worktree.
- **Extending the waived path.** Rejected: that path resets the tree on a retry, and this command's working copy is the tree as the user left it.
- **Working on the current branch, with no branch of its own.** Rejected: a GitHub-issue run needs a branch to push, and a branch of its own keeps the run's commits apart until they land.

## Consequences

- Other skills do not start `/implement-yolo`.
- `/implement-yolo` joins the Named session skill list ([ADR-0038](0038-named-session-skills-apply-high-priority-retro.md)). Its retro commit goes on the branch the session started from, after the land or the pull request.
- Uncommitted files may land in the Step's commit, and a retry never resets the tree. Git refusing to carry them onto the run's branch halts the run, and so does a detached HEAD. A run in a linked worktree for the same slug halts. The run's own branch in this checkout is where it resumes, and that branch's upstream names the branch it started from.
- Green is measured against the commit the run started from. Leftover gaps and the local-only rule apply as they do to `/implement-oneshot` ([ADR-0026](0026-implement-agents-close-leftover-gaps.md), [ADR-0028](0028-an-implement-run-leaves-the-repository-only-for-its-pull-request.md), [ADR-0029](0029-green-is-measured-against-master.md)).
