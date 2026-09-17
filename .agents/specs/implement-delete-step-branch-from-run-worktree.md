# Delete each Step branch from the run worktree

Status: ready-for-agent

## Problem Statement

When you type `/implement`, each Step runs on its own branch. When that Step finishes, the session puts its commits onto the run and then deletes the Step's branch.

Git's safe delete only works when that branch is already merged into the checkout you delete from. The Step's branch is merged into the run. The directory you started in is still on master. A delete from there fails. The Step's branch stays in the repository.

A Retrospective on another repository hit this: leftover Step branches after a run that had already merged them.

## Solution

After a Step's commits are on the run, the session removes that Step's worktree and deletes that Step's branch from the run worktree — the checkout whose branch is the run. Git then sees the branch as merged, and the safe delete succeeds.

The directory you started in stays on master until the run lands. Landing still deletes the run's own branch from there, after that branch has been merged into master.

## User Stories

1. As a developer, I want each Step's branch gone after that Step is on the run, so leftover Step branches do not pile up in the repository.

2. As a developer, I want that delete to succeed, so I do not see "not fully merged" for a branch the run already contains.

3. As a Driving session, I want to delete the Step's branch from the run worktree, so Git's safe delete sees it as merged.

4. As a Driving session on a host whose shell starts every command in the original directory, I want that delete to use the run worktree path the way every other run-worktree command already does, so the host's start directory does not put the delete on master.

5. As a developer, I want the safe delete, so a Step whose commits are not on the run is not force-removed.

6. As a Driving session, I want the Step worktree removed before its branch is deleted, so Git is not asked to delete a branch that is still checked out.

7. As a Driving session, I want a finished Step's cleanup complete only when that Step's worktree and that Step's branch are both gone, so a failed delete cannot be treated as done.

8. As a developer, I want the original directory left on master until land, so my working copy stays as I left it during the run.

9. As a developer, I want land to keep deleting the run's own branch from the original directory after that branch is merged into master, so the run branch does not stay after a successful land.

10. As a developer who waived the worktree, I want this change to leave that path alone, so a sequential run that never created a Step branch does not grow new checkout rules.

11. As a developer who types `/implement-oneshot`, I want that skill unchanged, so a run with no Step branches does not learn a Step-branch rule.

12. As a Driving session, I want rebase of a finished Step to stay in that Step's worktree, so the rebase still starts where the Step's commits live.

13. As a Driving session, I want the fast-forward onto the run to stay in the run worktree, so the run branch remains a linear stack.

14. As a Driving session, I want a conflict during rebase or fast-forward to still go to `/resolving-merge-conflicts`, then to delete the Step's branch from the run worktree once the run is linear, so a conflict does not change where the delete runs.

15. As a Driving session, I want completions that arrive together to still join the run one at a time, lowest number first, so this change does not reorder parallel Steps.

16. As a Driving session, I want the next Ready Steps to dispatch after that Step is on the run and its branch is gone, so waiting Steps still start as soon as their blockers are on the run.

17. As a developer, I want a halt to still leave in-flight Step worktrees and their branches as they are, so a stopped run stays resumable.

18. As a Driving session resuming an in-flight run, I want to enter the run worktree, so resume still does not sit on a Step branch.

19. As a Step agent, I want the Driving session to delete my branch, so I still return the three-line report and do not clean up the run.

20. As a developer, I want Git's branch list from the original directory to show no Step branches after each finished Step is on the run, so I can tell cleanup worked without entering the run worktree.

21. As a developer, I want the last Step to still leave the whole suite Green, so this cleanup does not replace that check.

22. As a maintainer, I want no new glossary term for this, so "run worktree" stays the phrase the implement skill already uses.

23. As a maintainer, I want no ADR for this, so a location pin on an existing command is not recorded as an architectural trade-off.

24. As a developer, I want work in another repository left on its unpushed run-named branch, so this cleanup applies only to Step branches in this repository.

25. As a Driving session, I want the checkout named on the merge, the worktree remove, and the branch delete together, so a sentence about conflicts cannot send the delete back to the original directory.

26. As a developer, I want a Step whose worktree is still locked by a live agent left alone, so this delete never races an agent that is still working.

## Implementation Decisions

- After a finished Step is rebased onto the run and fast-forwarded into it, the Driving session removes that Step's worktree and then deletes that Step's branch. Both the remove and the delete run from the run worktree. Rebase stays in the Step worktree. Fast-forward stays in the run worktree.

- The sequence names that checkout on the merge, the worktree remove, and the branch delete together. A conflict during rebase or fast-forward still goes to `/resolving-merge-conflicts` with the same stated goal as today. Once the run is linear again, the remove and the delete still run from the run worktree.

- The delete is Git's safe branch delete. Force-delete is not used. Safe delete succeeds here because the run worktree's current branch already contains the Step.

- Hosts whose shell starts every command in the original directory already prefix run-worktree commands with a directory change or an equivalent Git path flag. This delete is one of those commands. No second path mechanism is added.

- Cleanup after a finished Step is complete when that Step's worktree is gone and that Step's branch is gone. The run then reports the Step done and dispatches any Step that just became Ready. Completions that arrive together still join the run one at a time, lowest number first.

- Green stays as it is: each Step greens its Footprint's projects, and the last Step greens the whole suite. Deleting a Step branch is not a substitute for that check.

- Land is unchanged: return to the original directory, fast-forward the run branch into master, remove the run worktree, and safe-delete the run branch from there. Until then the original directory stays on master. The land delete succeeds because master now contains the run.

- Worktree waived stays sequential in the one checkout and never creates a Step branch. `/implement-oneshot` never creates a Step branch. Neither skill gains this rule.

- A halt still leaves the Spec, the Step files, the run worktree, and any Step worktrees as they are. This cleanup runs only after a successful rebase and fast-forward, not on a Step that did not finish.

- Resume still enters the run worktree. A locked Step worktree still means that Step agent is live and is left alone.

- The Step agent still does not delete its branch. The Driving session does, after the structural check, the rebase, and the fast-forward.

- [ADR-0033](../../docs/adr/0033-implement-runs-ready-steps-in-parallel.md) still governs parallel Ready Steps and linear fast-forward onto the run. [ADR-0015](../../docs/adr/0015-implement-worktree-host-agnostic.md) still governs the run worktree and the land order. No ADR is added. No glossary entry is added or rewritten.

- Work a Spec puts in another repository stays on the unpushed branch named after the run. This cleanup is for Step branches in this repository only.

## Testing Decisions

A good check is what Git still lists after a Step is on the run, not how the skill sentence is worded.

- After a finished Step is on the run and cleaned up, the Step's branch does not exist. `git branch` from the original directory does not list it. The session did not print Git's "not fully merged" refusal.
- After land, the run's own branch is also gone.
- A waived run and an `/implement-oneshot` run still create no Step branch.

This repo has no automated suite for skill prose. Do not add one. The prior art is the Git reproduction in this triage: after a Step branch is fast-forwarded into the run, safe-delete from master fails with "not fully merged", and the same safe-delete from the run worktree succeeds.

Do not assert on force-delete. The skill must not use it.

## Out of Scope

- Force-deleting a Step branch.
- Sweeping leftover Step branches from earlier runs when `/implement` resumes.
- Changing land of the run branch, including where that branch is deleted.
- Changing `/implement-oneshot`.
- Changing the worktree-waived path.
- Changing rebase, fast-forward, or the lowest-number-first join order.
- Cleaning branches in another repository.
- Adding a glossary term or an ADR for this location pin.
- A halt that deletes in-flight Step worktrees or their branches.

## Further Notes

Git's safe branch delete checks whether the branch is merged into the current checkout (or into the branch's upstream). The run worktree's current branch is the run, which already has the Step. The original directory's current branch is master, which does not have the Step until land. That is why the same command succeeds in one checkout and fails in the other.

The implement skill already names the run worktree as the place to fast-forward a finished Step. The delete belongs in that same place. A sentence about conflicts currently sits between the fast-forward and the delete, and that gap is how the delete drifts to the original directory.
