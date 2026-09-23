# Run Ready Steps in the run worktree on confined hosts

Status: ready-for-agent

## Problem Statement

`/implement` runs each Ready Step in its own Step worktree. The Driving session opens that worktree from the main checkout: it resolves the main checkout from `git worktree list`, then runs `git worktree add` there. After the Step agent finishes, the Driving session rebases the Step branch onto the run branch and removes the Step worktree.

Some hosts confine a session that runs inside a worktree to that worktree. On those hosts, git commands aimed at the main checkout are refused. So the Driving session cannot open a Step worktree. A Step agent also cannot work in a Step worktree outside the session's own worktree.

This happened in a `/implement` run in another repository. The session ran inside a host-created worktree. The host blocked the git commands aimed at the main checkout. The Step agent could not use its Step worktree, so it committed straight to the run branch. The skill had no path for this. The run only continued because the agent improvised.

## Solution

When the host confines the session to its worktree, the Driving session runs Ready Steps **one at a time in the run worktree**. This is how a waived worktree already runs step 3: no Step worktree, no Step branch, no rebase. Each Step agent works in the run worktree and commits to the run branch. The Driving session then dispatches the next Ready Step.

The Driving session detects a confined host by what the host does, not by the host's name:

- the host refuses the git command that opens a Step worktree from the main checkout, or refuses another git command aimed there, or
- a Step agent reports that it cannot work in its Step worktree.

A refusal is a permission or sandbox block from the host. An ordinary git error, like a branch that already exists, is not a refusal. From the first refusal to the end of the session, every Step runs in the run worktree. The Driving session says in one line to the user that it switched to one Step at a time and why.

## User Stories

1. As a maintainer running `/implement` on a host that confines a worktree session to its worktree, I want Ready Steps to run one at a time in the run worktree, so the run finishes without git commands the host refuses.
2. As a maintainer on such a host, I want the Driving session to switch on the first refusal, so the run does not halt over a Step worktree it could never open.
3. As a maintainer on such a host, I want each Step agent to commit to the run branch, so the run branch stays a linear stack of Step commits, the same as after a rebase.
4. As a maintainer on such a host, I want the structural check to look for the new commit on the run branch, so a Step that committed there counts as done.
5. As a maintainer on such a host, I want a retry to reset the run worktree before the Step is dispatched again, so the second attempt starts clean.
6. As a maintainer on a host that allows Step worktrees, I want Ready Steps to keep running in parallel, so this fallback costs me nothing.
7. As a maintainer, I want a one-line notice when the run switches to one Step at a time, so I know why the run is slower.
8. As a maintainer resuming a halted run on a confined host, I want resume to work with no Step worktrees present, so a re-invoke picks the run back up.
9. As a maintainer resuming on a confined host, I want a Step that reads `Status: done` on the run branch to count as done, with no rebase waiting.
10. As a Step agent on a confined host, I want my prompt to name the run worktree as my only working directory, so I do not try to reach a path the host blocks.
11. As a maintainer, I want an ordinary git error while opening a Step worktree handled as it is today, so a real problem is not hidden by the fallback.
12. As a future editor of `/implement`, I want the rule recorded in an ADR, so I know why step 3 has a third way to run.

## Implementation Decisions

- The change is prose in the `/implement` skill, plus a new ADR. No other skill changes.
- Step 3 gains a **confined host** branch. It reuses the step 3 rule from **Worktree waived**: Ready Steps run one at a time in this checkout, and the Step worktree and the rebase are skipped. Here "this checkout" is the run worktree. Write the rule once and point to it from both places, instead of copying it.
- On the confined path, the structural check reads the Step file in the run worktree for `Status: done`, and reads `git log -1` on the run branch for a new commit. There is no Step branch to check.
- On the confined path, the retry reset (`git reset --hard && git clean -fd`) runs in the run worktree. Nothing else is in flight, so the reset cannot touch another Step's work.
- The "Done when" line for step 3 still holds: every Step reads `done`, and no Step worktree or Step branch remains. On the confined path, none was ever made.
- Step 1 and step 6 stay as they are. Resume already works when no Step worktree exists. Land already uses the host's leave-worktree action. The seed report named only step 3.
- The new ADR amends [ADR-0033](../../docs/adr/0033-implement-runs-ready-steps-in-parallel.md). ADR-0033 says a waived worktree stays sequential because there is one checkout. The new ADR adds that a confined host also stays sequential, because the session can reach only one worktree. It records the rejected option: treat every host-created run worktree as confined. That would drop parallel Steps on hosts that allow Step worktrees.
- If `CONTEXT.md` gains a term for a confined host, add it under Execution. Otherwise describe the condition in plain words in the skill.

## Testing Decisions

- This repo has no test suite. The check is a read of the edited `/implement` skill against the user stories above.
- A good check follows the confined path from start to land: step 1 on a fresh or resumed run, step 3 with a refused worktree add, the structural check, a retry, and step 6. Each place must say what happens with no Step worktree.
- Also check that the parallel path reads the same as before for a host that allows Step worktrees.
- Run `/writing-for-agents` on the edited skill, as `CLAUDE.md` requires.

## Out of Scope

- Detecting a confined host by name or from its docs.
- Changes to `/implement-oneshot` or `/implement-yolo`. They open no Step worktrees.
- Changes to the implementer agent's own instructions. The Driving session's prompt already names its working directory.
- A host that also refuses the land step's git commands. The report did not show that, and it is a separate problem.

## Further Notes

- Source: a `/retro` from a `/implement` run in another repository, triaged in this repository on 2026-09-23.
- The report gave two triggers: "the session is inside a host-created worktree" and "on such hosts" where git aimed at the main checkout is blocked. This Spec uses the host's refusal as the trigger. The first trigger would also stop parallel Steps on hosts that do allow Step worktrees.
