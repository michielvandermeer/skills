# Implement agents start from smaller contexts

Status: ready-for-agent

## Problem Statement

`/implement` runs use up the maintainer's 5-hour and 7-day rate limits fast. Almost all of the cost is cache reads: on every turn, an agent re-reads its whole context. So the bigger an agent's context grows, the more each of its turns costs.

In 48 hours of transcripts (2026-09-24 to 2026-09-26), three things kept contexts large:

- **Checks run at the Step agent's largest context.** Each Step agent runs `/code-review` on its own commit, fixes the findings, and runs the browser pass, after its code is already green. By then its context is 300–400k tokens. This work took 29% of Step agent spend, and browser turns averaged 288k tokens of context.
- **One fixer takes every final-review finding.** In step 4 of `/implement`, a single fixer gets the findings from both review axes. Fixers cost about 9% of total spend. One ran 285 turns, reached 586k tokens of context, and cost $57 on its own.
- **Every Step reads every earlier Outcome.** By Step 20 that is about 20k tokens, re-read on every turn, so the cost grows with the square of the Step count.

`/implement-oneshot` and `/implement-yolo` have a related waste. The Oneshot agent reviews its own work at the end, at a very large context. Then the Driving session reviews nearly the same changes again.

## Solution

Work that does not need a large context moves into agents that start small.

- After each Step agent commits its Step, the Driving session sends a fresh **Checker**. The Checker runs the browser pass, reviews the Step's commit, fixes what it finds, and folds the fixes into that commit. It starts from the Step file and the Step's changes, not from the Step agent's 300–400k tokens.
- The final review sends two fixers in turn: one for the Spec findings, then one for the Standards findings. Each starts fresh.
- The Planner writes, on each Step, which earlier Steps it depends on. A Step agent reads only those Steps' Outcomes.
- The Oneshot agent stops reviewing its own work. The final review already covers the same changes.

The runs build the same thing as before. Every Step is still reviewed on both axes before the next Step starts. The estimated saving is about 14–17% of total `/implement` spend.

## User Stories

1. As the maintainer, I want the per-Step review and browser pass to run in an agent that starts small, so that an `/implement` run uses less of my rate limit.
2. As the maintainer, I want every Step still reviewed on both axes before the next Step starts, so that problems are caught as early as they are today.
3. As the maintainer, I want `/implement` to build the same thing it builds today, so that saving tokens costs no quality.
4. As the Driving session, I want to send the Checker myself after the Step agent reports, so that no sub-agent waits at a large context while another works.
5. As the Driving session, I want a Step to show whether its Checker has run, so that I can tell a built Step from a finished one.
6. As the Driving session resuming a halted run, I want a Step that was built but not checked to restart at its Checker, so that no check is skipped.
7. As a Step agent, I want my green to mean my Footprint's tests pass, so that I can hand over as soon as the code works.
8. As a Step agent, I want to read only the Outcomes of the Steps mine depends on, so that my context starts smaller.
9. As a Step agent whose Step file has no dependency line, I want to read every earlier Outcome, so that I never miss a fact because a line was left out.
10. As a Checker, I want the Spec, the Step file, the commit before the Step, the Coding standards, the glossary and relevant ADRs, the Testing Decisions, and earlier deviations, so that I can review and fix without the Step agent's context.
11. As a Checker, I want to run the repo's browser pass or smoke run first, so that a broken surface is found before the review.
12. As a Checker, I want to fix a failed browser pass myself, so that the Step finishes without another agent.
13. As a Checker in a repo with no browser pass or smoke run, I want to review and fix only, so that I do not invent a check the repo does not use.
14. As a Checker, I want to re-run the Footprint's tests after my fixes, and the whole suite on the last Step, so that the Step leaves green.
15. As a Checker, I want to mark the Step done even when I found nothing to fix, so that the Driving session can tell the check ran.
16. As a Checker whose fix changes something a later Step needs, I want to add it to the Outcome and the deviations line, so that later Steps and the Driving session learn of it.
17. As the Driving session, I want the Checker to report in the same three lines as a Step agent, so that I handle both the same way.
18. As the Driving session, I want the Checker under the same retry-then-halt rule as a Step agent, so that a failing check gets one retry and then stops the run.
19. As the Planner, I want to write which earlier Steps each Step depends on, so that each Step agent reads only what it needs.
20. As the Planner, I want to write that a Step depends on none, so that a Step with no dependency reads no Outcomes.
21. As a future reader of the Step format, I want it clear that the dependency line picks Outcomes and never changes run order, so that nobody mistakes it for the parallel runs that were dropped.
22. As the Driving session in step 4, I want to send a Spec fixer and then a Standards fixer, so that no single fixer grows as long as the one that cost $57.
23. As the Driving session, I want to skip the fixer for an axis with no findings, so that no agent runs for nothing.
24. As a Standards fixer, I want to skip a finding whose code the Spec fixer already removed, so that I do not recreate or patch deleted code.
25. As the Driving session, I want each fixer to have its own retry, so that one fixer's failure is handled like any other sub-agent's.
26. As the maintainer running `/implement-oneshot` or `/implement-yolo`, I want the Oneshot agent to stop reviewing its own work, so that the same changes are not reviewed twice.
27. As the maintainer running `/implement-oneshot` or `/implement-yolo`, I want their final review to use the same two fixers, so that all three commands get that saving.
28. As the maintainer, I want to re-run the same transcript measurement after this lands, so that I can see whether contexts shrank.

## Implementation Decisions

**The Checker.**

- A new named plugin agent, `skills:checker`, with its own agent file. It runs on the session's model at `effort: medium`, which is the effort the review-and-fix loop runs at today inside the Step agent (ADR-0049). The README's list of effort-pinned agents gains it.
- The Driving session sends it in step 3 of `/implement`, right after each Step agent's report and structural check pass. The Step agent does not start it. A Step agent that started it would wait at peak context, and the reviewers would sit three agents deep.
- Its prompt is made of paths and section names, the same way the Step agent's prompt is. It holds the Spec, the Step file, the parent of the Step's commit as the review's fixed point, the Coding standards, `CONTEXT.md` and the ADRs for the area, the Spec's Testing Decisions, and earlier deviations verbatim. It does not receive earlier Outcomes.
- The Checker's work, in order:
  1. Run any verification the repo's conventions demand for the surface touched, such as a browser pass or smoke run. Skip this when the repo has none.
  2. Run `/code-review` on the Step's commit, on both axes, with the Step file as the spec. Tell both axes that later Steps build the rest of the Spec and that the Step file is run bookkeeping. This is the same framing the Step agent uses today.
  3. Fix every finding, and any failed verification. Where a finding and the Spec disagree, the Spec wins and the finding goes on the deviations line.
  4. Re-run the tests of the Footprint's projects, or the whole suite on the last Step, and the verification from 1 again.
  5. Set the Step file's `Status:` to `done`, add to the Outcome anything a later Step needs from its fixes, and fold everything into the Step's commit with `git commit --amend`. It amends even when there was nothing to fix, because the status flip must land.
- It returns the same three-line report as a Step agent: `status`, `built`, `deviations`.
- After it returns, the Driving session checks that the Step file reads `Status: done`.
- The Checker gets one retry and a second failure halts the run, the same rule as a Step agent.
- It may start sub-agents only for the reviewers `/code-review` starts.

**The Step agent.**

- Its "review your commit" line goes. So does its permission to start the reviewers' sub-agents. It keeps its permission to start sub-agents for reading a part of the codebase too large to hold.
- Its green is now the tests of its Footprint's projects, or the whole suite on the last Step, measured against `master` (ADR-0029). The browser pass or smoke run moves to the Checker. A Step is **Green** only once both have passed.
- It sets `Status: built`, not `done`, in the commit that holds its code, its Step file, and its Outcome.
- After it returns, the Driving session checks for `Status: built` and a new commit. A failed check earns its one retry, as today.
- In the dispatch list, the instruction to read the Outcome of every lower-numbered Step becomes: read the Outcome of each Step on the `Depends on:` line, or of every lower-numbered Step when the line is missing.

**Resume.** A run resumes at the lowest-numbered Step that is not `done`. A Step at `built` resumes at its Checker. A Step at `pending` resumes at its Step agent.

**The Step format and the Planner.**

- The Step file format gains a `Depends on:` line under `Status:`. It lists the numbers of the earlier Steps whose Outcomes this Step needs, such as `Depends on: 02, 05`, or `Depends on: none`.
- The Planner fills it on every Step, from the same code walk it already does for the Footprint. A Step that touches what an earlier Step creates or changes depends on it.
- The line never changes run order. Steps still run strictly in `NN` order (ADR-0045).
- The slicing rules do not gain a size target.

**The final review, in all three commands.**

- In step 4 of `/implement`, and in the "Review and improve" step of `/implement-oneshot` and `/implement-yolo`, one fixer for every finding becomes two fixers in turn. The Spec fixer gets the Spec axis's findings, as the reviewers wrote them. After it, the Standards fixer gets the Standards axis's findings.
- The Spec fixer goes first because a Spec fix can remove code that a Standards finding points at. The Standards fixer is told to skip a finding whose code is gone and to name it on its deviations line.
- A fixer whose axis reported nothing is skipped, and the Driving session says so.
- Each fixer is `general-purpose` at the session's own model and effort, as today. Each reports in three lines, leaves the projects it touched green, commits its own work, and gets its own one retry. A second failure of either one halts the run.
- `/improve-data-structures` still runs after the fixers. The post-rebase fixer at land does not change.

**The Oneshot agent.** Its "run `/code-review` on your commits and fix every finding" line goes. Its browser pass stays part of its green. The Driving session's final review and the two fixers cover the same changes.

**ADRs.**

- A new ADR: "A fresh Checker finishes each Step". It records why the Step agent does not review its own work: the Checker trades the Step agent's knowledge of the code for a much smaller context.
- ADR-0045 gains one consequence: the `Depends on:` line picks which Outcomes a Step reads, and never the order it runs in.
- Both are written in the same change as this Spec.

**Glossary.** `CONTEXT.md` already carries the **Checker** entry, and the updated **Step agent**, **Planner**, and **Outcome** entries. They were written during the grilling session.

**Agent documents.** Every edited agent file and skill file matches `skills/writing-for-agents/SKILL.md`. `/writing-for-agents` runs on them after the edit, as this repo's `CLAUDE.md` requires.

## Testing Decisions

- This repo is prose, so there are no automated tests. A good check looks at what agents do in real runs, not at the wording.
- The check is the transcript measurement from the Issue that started this work, re-run on `/implement` runs after this Spec lands. The numbers to compare:
  - Share of Step agent spend on turns above 200k context. Before: 54%.
  - Average context of Checker turns, and especially browser turns. Before: 288k for browser turns inside the Step agent.
  - Fixer turns and cost per run. Before: $122 across fixers in 48 hours, with one fixer at 285 turns.
  - Tokens of Outcomes in a Step agent's opening context at Step 20. Before: about 20k.
- The method: take transcripts under `~/.claude/projects/*/` (`<session>.jsonl`, and `<session>/subagents/*.jsonl` with their `.meta.json`). Group assistant messages by message id, and price each one's `usage` at Opus rates. Label each turn by the tools it called.
- Whether runs still land green, and whether review findings keep being caught at the Step, is seen in normal use.

## Out of Scope

- Dropping the per-Step Standards review. We keep both axes on every Step. Once the Checker runs the review at a small context, the saving left is small, and dropping it would give the final fixers more work.
- A Step size target in the slicing rules. The Idea `re-measure-step-size` holds it until the measurement is re-run after this Spec and the reads Spec land.
- Running read-only agents on Sonnet, and trimming the fixed baseline of each sub-agent turn. Each is its own Issue in `.agents/issues/implement-token-cost/`.
- How agents read code. The Spec `implement-agents-read-in-batches` covers it. The two Specs both edit the Step agent's working habits, but either can land first.
- Splitting final-review findings by area of code. It needs the Driving session to sort findings, and Spec findings often name no file.
- The post-rebase fixer at land, and `/improve-data-structures`.

## Further Notes

- The full 48-hour measurement is in commit `5d4d45e`, in the Issue this work was split from.
- The saving estimate adds the triage's estimates: 7–10% for fresh-agent checks, about 4% for the fixer split, and about 3% for fewer Outcomes. The Oneshot agent's dropped review was not measured.
- `/code-review` caps each axis report at 400 words. So the 285-turn fixer was long because of the work, not because of how many findings it had. That is why the split is by axis and not by count.
