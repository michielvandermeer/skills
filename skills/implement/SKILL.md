---
name: implement
description: "Implement a piece of work based on a spec."
argument-hint: "Which spec, issue, or idea to implement?"
disable-model-invocation: true
---

# Process

1. **Work in a worktree.** Call the `EnterWorktree` tool to start this session in a fresh worktree and branch — not `git worktree add`, which leaves the session in the original directory. You MUST work in a worktree and branch; the only exemption is an `/implement` prompt that explicitly waives it.
2. Implement every User Story in the spec, following its Implementation Decisions and writing tests per its Testing Decisions. Done when every User Story is implemented and the full test suite passes.
3. Run `/code-review` with `master` as the fixed point, and fix every issue it recommends.
4. Run `/improve-data-structures`.
5. Delete the spec — and any idea or issue documents it came from — now that they are implemented.
6. Commit everything to the branch: code, tests, and the deletions. `git rebase` refuses a dirty tree, so the branch can't land until this is clean.
7. **Land the branch on master.** Each command runs where its branch is checked out, and that constraint fixes the order:
   1. From the worktree, still on the branch: `git rebase master`, resolving any conflicts. (The branch lives here, so only the worktree can rebase it.)
   2. Call the `ExitWorktree` tool with `action: "keep"` to return the session to the original directory, preserving the branch and its commits.
   3. From the original directory: `git merge --ff-only <branch>`. (master lives here, so only the original directory can fast-forward it.) The rebase above makes this a fast-forward with no merge commit; if it errors, master moved during the session — re-enter the worktree, rebase again, and retry.
   4. `git worktree remove <path>` and `git branch -d <branch>`.

   With the worktree waived there is none to exit or remove: check out master yourself before the fast-forward, then delete the branch.
