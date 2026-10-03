# A run lands on the branch it started from, or opens a pull request

Every implement command works against the **base branch**. For a Spec in the repo it is the branch the session is on when the command starts, read again on a resume: the run branches from it, is reviewed and measured Green against it, and lands back on it. The user chose that branch by checking it out, and a run that landed on the repository's default branch would carry a feature branch's commits where they did not choose. A detached HEAD has no base branch, so the run halts.

For a Spec on a GitHub issue the base branch is the repository's default branch as GitHub has it, and the run ends in a pull request against it instead of a land ([ADR-0028](0028-an-implement-run-leaves-the-repository-only-for-its-pull-request.md)). It continues the grilling draft when one is open, and otherwise branches from the default branch. Each change to a GitHub issue is a pull request, and its merge is what closes the issue.

## Considered Options

- **The repository's default branch for every run, unless the prompt names another.** Rejected: the user already chose a branch by checking it out, and a run that leaves it surprises them.
- **Recording the base branch in the Step files at the start.** Rejected: the Planner and the oneshot Step file would carry a field only the land reads. A resume reads the branch the user is on now, which is what they want it to land on.

## Consequences

- A fresh worktree is reset to the base branch, not rebased onto it: its branch has no commits of its own yet, and a host tool may have created it from another branch.
- A GitHub-issue run rebases a fresh branch onto the default branch before its first push. A continued grilling draft that is behind gets the default branch merged in, at the start and again before the push. New commits from either mean a rebuild under the flaky re-run ([ADR-0046](0046-a-flaky-post-rebase-failure-is-not-a-fixer-dispatch.md)), and nothing force-pushes.
- A GitHub-issue run halts when an open pull request ready for review already closes the issue, and names it. Its `/retro` commit stays on the branch the session started from, outside the pull request.
- `/implement-yolo` works on a branch of its own in this checkout and measures Green against the commit it started from. On a resume from that branch, the branch it started on is read from its upstream ([ADR-0042](0042-implement-yolo-is-a-third-command.md)).
- `/retro` judges a new check against the current branch.
