# Re-run a post-rebase red before fixing it

Status: ready-for-agent

## Problem Statement

When `/implement` lands, it rebases the run branch onto `master`. If `master` gained commits during the run, **Green** is not known any more, so the Driving session runs the projects again. The skill then says a red run "gets one fixer dispatch". It says nothing about flaky tests.

In a mvdmio-suite run, the post-rebase run went red. The cause was two flaky tests, one after the other, in a project the branch never touched. Proving that took three suite or project runs. A fixer dispatch on a flaky test costs a full sub-agent run, finds nothing to fix, and can use up the one retry the retry-then-halt rule allows.

`/implement-oneshot` has the same post-rebase line and the same gap.

## Solution

After the post-rebase run, the Driving session re-runs each project that failed, once, before it treats the run as red.

- A failure that passes on the re-run is a flaky test. It is not red. It goes on the deviations line and into the final report, the same way a failure that `master` already has does under ADR-0029.
- A failure that fails again is red. It gets the one fixer dispatch under the retry-then-halt rule, as today.

The re-run covers only the projects that failed, not the whole suite, so it costs one project run, not a sub-agent.

## User Stories

1. As a Driving session landing an `/implement` run, I want to re-run a project that failed after the rebase, so that a flaky test does not cost me a fixer dispatch.
2. As a Driving session, I want a failure that passes on the re-run to go on the deviations line, so that the run lands without hiding that a test is flaky.
3. As a Driving session, I want a failure that fails again to get the fixer dispatch, so that a real regression from the rebase is still fixed before the fast-forward.
4. As a Driving session, I want to re-run only the failing projects, so that the check stays cheap on a large suite.
5. As a Driving session landing an `/implement-oneshot` run, I want the same re-run rule, so that both commands treat a post-rebase red the same way.
6. As a maintainer reading the final report, I want each flaky test named, so that I can decide whether to fix or quarantine it outside the run.
7. As a maintainer, I want the fixer's retry kept for real failures, so that a flaky test cannot use it up and halt a run that was green.
8. As a maintainer, I want the rule written down as a decision, so that later edits do not quietly drop it.

## Implementation Decisions

- `/implement`, step 6.1: before "A red run gets one fixer dispatch", add that the Driving session first re-runs each failing project once. A failure that passes on the re-run is a flaky test: it goes on the deviations line and into the final report and does not block landing. Only a failure that fails again is red.
- `/implement-oneshot`, step 5.1: the same change to its matching sentence.
- The re-run is the Driving session's own command, not a sub-agent. It is one run of each failing project, not a loop.
- A new ADR records the rule and why: a flaky test is not a regression the branch caused, and a fixer dispatch is too costly to spend on finding that out. It points at ADR-0029, which it extends. Rejected alternative: checking the failure against `master` at the merge-base first. That also works, but it costs a build on another checkout, while a re-run costs one project run.
- `CONTEXT.md`: extend **Deviation** so it also covers a post-rebase failure that passed on the re-run. Leave **Green** as it is; a flaky test that passed on the re-run is green.
- `/implement-yolo` has no rebase at land, so it does not change.

## Testing Decisions

- This repo is prose, so there is no test suite. The check is reading the edited sentences against the Solution: a reader who meets a post-rebase red must be told to re-run the failing projects once before any fixer dispatch.
- Run `/writing-for-agents` on each edited skill file, as `CLAUDE.md` asks.
- Prior art: ADR-0029's wording for a failure `master` already has, which the new sentence should mirror.

## Out of Scope

- Flaky tests during a Step. The Step agent measures its own **Green** and is not changed here.
- Fixing, quarantining, or tracking flaky tests in the consuming repo.
- More than one re-run, or any retry loop.
- `/implement-yolo`.

## Further Notes

- Source: a `/retro` on mvdmio-suite, triaged on 2026-09-23. The same retro also asked for a fallback when a host blocks Step worktrees; ADR-0045 already removed Step worktrees, so that item was not filed.
