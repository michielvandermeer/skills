---
name: implement
description: "Implement a piece of work based on a spec."
disable-model-invocation: true
---

# Process

1. Call the `EnterWorktree` tool to start this session in a fresh worktree and branch — not `git worktree add`, which leaves the session in the original directory.
2. Implement every User Story in the spec, following its Implementation Decisions and writing tests per its Testing Decisions.
3. Once every User Story is implemented, run `/code-review` and fix all recommended issues.
4. Once code review is done, run `/improve-data-structures`.
5. Commit the changes to the branch.
6. Delete the idea, spec, or bug documents that have been implemented by this session.
7. Rebase the branch onto master so history stays linear on top of the latest master — from the worktree (still on the branch), run `git rebase master`. Resolve any conflicts before continuing. (The rebase must happen here, since the branch is checked out in the worktree and can't be checked out from the original directory.)
8. Call the `ExitWorktree` tool with `action: "keep"` to return the session to the original directory, preserving the branch and its commits. (The fast-forward must happen from the original directory, since the target branch — e.g. master — stays checked out there and can't be merged into from within the worktree.)
9. From the original directory, fast-forward master onto the branch with `git merge --ff-only <branch>`. Because the branch was just rebased onto master, this fast-forwards with no merge commit; if it errors, master moved during the session — re-enter the worktree, rebase again, and retry.
10. Remove the worktree and delete the branch (`git worktree remove <path>` and `git branch -d <branch>`).
11. Provide a summary of all the work in this session to the user.