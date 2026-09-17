# Implement removes the run worktree after fast-forward succeeds

Status: ready-for-agent

## Problem Statement

You ran `/implement`. The default branch moved while the run was landing. The fast-forward merge failed. The session then removed the worktree the run opened.

The skill already says to go back into that worktree, rebase, and try the merge again. The next numbered step still removes the worktree. After the remove, the retry has nowhere to rebase.

The same land order lives in `/implement-oneshot`.

## Solution

The run's worktree stays until the fast-forward merge onto the default branch succeeds. After a failed fast-forward, the session goes back into that worktree, rebases, and tries the merge again. It removes the worktree and deletes the branch only after that merge succeeds.

`/implement-oneshot` does the same.

When the worktree was waived, the session still deletes the branch only after the fast-forward succeeds.

## User Stories

1. As a developer, I want the run's worktree still there after a failed fast-forward, so the session can rebase and try the merge again.

2. As a developer, I want the run's branch still there after a failed fast-forward, so the retry has something to merge.

3. As a developer, I want a successful fast-forward to remove the worktree and delete the branch, so a landed run still leaves a clean checkout.

4. As a developer whose default branch moved once during land, I want the session to rebase in the run's worktree and retry the merge, so one move does not strand the branch.

5. As a developer whose default branch moved again during that retry, I want the worktree to stay until a later retry succeeds, so a second move is the same case as the first.

6. As a Driving session, I want the merge step done only when the fast-forward succeeded, so cleanup is not the next numbered action after a failed attempt.

7. As a Driving session, I want a failed fast-forward to send me back into the run's worktree, so the rebase runs where the branch is checked out.

8. As a Driving session, I want that retry rebase to re-check Green when it replayed the branch onto new default-branch commits, so land still measures Green against the default branch it is about to fast-forward.

9. As a Driving session, I want a Changelog conflict on that retry rebase to keep both entries with this run's entry above, so the retry uses the same Changelog rule land already has.

10. As a Driving session, I want a conflict on that retry rebase to use `/resolving-merge-conflicts`, so the retry does not invent a second conflict path.

11. As a developer who ran `/implement-oneshot`, I want the same keep-until-success rule, so a copied land sequence cannot strand a oneshot branch.

12. As a developer who waived the worktree, I want the branch deleted only after the fast-forward succeeds, so the waived path does not drop the branch after a failed merge.

13. As a developer who waived the worktree, I want no worktree remove on that path, so the waived branch stays a checkout with no extra tree.

14. As a developer whose fast-forward succeeded on the first try, I want the worktree removed and the branch deleted as today, so the happy path does not grow extra steps.

15. As a developer, I want land to stay a rebase plus a fast-forward, so the default branch still gains no merge commit.

16. As a Driving session, I want the host leave-worktree action still to return to the original directory and keep the branch, so leaving is not the same as removing.

17. As a Driving session, I want `git worktree remove` still never forced, so a lock still means another session has the tree.

18. As a Driving session, I want Step worktrees still removed after they land on the run branch, so this change does not keep per-Step trees until the default-branch merge.

19. As a developer, I want `/prototype` still to remove its own worktree on its own ending, so implement land does not rewrite prototype cleanup.

20. As a developer whose session dies after a failed fast-forward, I want the run's worktree still listed, so a re-invoke can find the tree the retry needs.

21. As a Driving session, I want the Spec and Step files still deleted before land, so this change only gates the worktree and branch cleanup.

22. As a later reader of ADR-0015, I want the recorded land order to say remove follows a successful fast-forward, so the ADR matches the skill.

23. As a developer, I want no new glossary term for this, so "run worktree" stays the skill's name for the tree the run opened.

24. As a developer, I want no new ADR, so a gated cleanup is recorded as a fact on the land order that already exists.

## Implementation Decisions

- The land merge step is done when the fast-forward onto the default branch has succeeded. Removing the run's worktree and deleting the run's branch are that step's cleanup, not a later numbered action that runs after a failed attempt.

- A failed fast-forward means the default branch moved. The session re-enters the run's worktree, rebases onto the default branch, returns to the original directory, and retries the fast-forward. The worktree and the branch stay for every retry.

- That retry rebase is the same rebase land already runs: a conflict is `/resolving-merge-conflicts`; a Changelog conflict keeps both with this run's entry above; Green is unknown again when the rebase replayed onto new default-branch commits, and is re-established before the next fast-forward.

- `/implement-oneshot` uses the same land order and the same done condition.

- The Worktree waived path has no worktree to remove. It still deletes the branch only after the fast-forward succeeds.

- A first-try successful fast-forward still removes the worktree (when one exists) and deletes the branch.

- Land stays rebase, then return to the original directory keeping the branch, then fast-forward, then cleanup. The host leave action still keeps the branch and the worktree. Remove is never forced.

- Step worktrees still come off the run branch and still go after they fast-forward onto that branch. `/prototype` still removes its own worktree on its own ending.

- When the Spec and the Step files are deleted does not change. This Spec does not add a land-failed resume path beyond keeping the worktree the retry already needs.

- ADR-0015's land-order consequence names that remove and branch delete follow a successful fast-forward. No new ADR. No CONTEXT.md change.

## Testing Decisions

A good check is what git still lists after each land outcome, not how the numbered list is worded.

- After a failed fast-forward, `git worktree list` still shows the run's worktree, the run's branch still exists, and the default branch does not have the run's commits.
- After a successful fast-forward, that worktree is gone, the run's branch is gone, and the default branch has the run's commits.
- The same two outcomes hold for `/implement-oneshot`.
- On the waived path, a failed fast-forward leaves the branch; a successful one deletes it.

This repo has no automated suite for skill prose. The check is a read of the land steps in `/implement` and `/implement-oneshot` against ADR-0015, the way `/validate-spec` already reads a Spec against the current skills. Prior art for "the worktree stays until the ending that consumes it" is a halt, which already leaves the run's worktree in place.

## Out of Scope

- Changing when the Spec and the Step files are deleted.
- Rebuilding a worktree a past run already removed.
- Bounding how many times land retries the fast-forward.
- Changing how Step worktrees are opened or removed.
- Changing `/prototype` cleanup.
- Teaching `/implement` a new resume path for a land that already deleted the Spec.
- Pushing the landed branch.
- Host tools that remove a worktree when the session leaves it.

## Further Notes

The retry after a failed fast-forward is already in the skill. The bug is that cleanup is the next numbered step after that attempt. The merge step's done condition is the fast-forward succeeding, and cleanup belongs to that success.
