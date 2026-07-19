---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

# Process

1. Call the `EnterWorktree` tool to start this session in a fresh worktree and branch — not `git worktree add`, which leaves the session in the original directory.
2. If the spec is large, start with the following prompt: `/goal implement <spec>`. Otherwise you may implement in the current session.
3. Once every requirement in the spec is implemented, run `/code-review` and fix all recommended issues.
4. Once code review is done, run `/improve-data-structures`.
5. Commit the changes to the branch.
6. Call the `ExitWorktree` tool with `action: "keep"` to return the session to the original directory, preserving the branch and its commits. (Merging must happen from the original directory, since the target branch — e.g. master — stays checked out there and can't be merged into from within the worktree.)
7. From the original directory, merge the session's branch into master, then remove the worktree and delete the branch (`git worktree remove <path>` and `git branch -d <branch>`).
8. Provide a summary of all the work in this session to the user.