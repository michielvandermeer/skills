# `/retro` learns from Corrections

Status: ready-for-agent

## Problem Statement

A session sometimes fixes code that an earlier session built wrong. The fix lands, but the lesson behind it goes nowhere. `/retro` looks only at the conversation and the steering files, and it leaves the code diff to `/code-review` and `/improve-data-structures`. The repo's Coding standards stay as they were, so the implementers in the next session can build the same thing wrong again.

## Solution

`/retro` also reads the code the session changed. In that diff it looks for **Corrections**: changes to code that existed before the session started, where the session also shows the old code was wrong. When a Correction points to a pattern that future code could repeat, `/retro` writes a rule for it into the repo's Coding standards. The rule is **High-priority**, so `/retro` applies it without asking. The implementers and `/code-review` already read the Coding standards, so the rule reaches every later session with no further change.

## User Stories

1. As a developer, I want `/retro` to notice when my session fixed code an earlier session built wrong, so that the lesson is not lost when the session ends.
2. As a developer, I want that lesson written into my repo's Coding standards, so that the implementers in future sessions get it right the first time.
3. As a developer, I want `/retro` to apply that rule without asking, so that the lesson lands even when I do not read the summary closely.
4. As a developer, I want `/retro` to count a change as a Correction only when the session shows the old code was wrong, so that a change that follows a new requirement does not become a rule.
5. As a developer, I want my own words ("this was wrong") to count as that proof, so that a fix I asked for teaches a lesson.
6. As a developer, I want a bug fix, a failing test, or a review finding against old code to count as that proof, so that a fix is recognised even when I said nothing.
7. As a developer, I want code written and fixed within the same session left out, so that `/implement`'s own review-and-fix loop does not pile duplicate rules into my Coding standards.
8. As a developer, I want `/retro` to skip a one-off fact such as a wrong constant, so that my Coding standards hold only rules future code could break again.
9. As a developer, I want `/retro` to skip a mistake a lint rule or a test could catch, so that the Automated checks suggestion covers it instead of a written rule.
10. As a developer, I want `/retro` to add no rule when my Coding standards already hold one the old code broke, so that the same rule is not written twice.
11. As a developer, I want `/retro` to change or remove an existing rule that a Correction contradicts, so that my Coding standards never hold two rules that disagree.
12. As a developer, I want the rule written into the Coding standards file my repo already keeps, so that I find it where I look for the rest.
13. As a developer in a repo with no Coding standards, I want `/retro` to create `.agents/refs/coding-standards.md`, so that the first lesson has a home the implementers already read.
14. As a developer, I want it not to matter whether a person or an agent wrote the old code, so that the lesson stands either way.
15. As a developer running `/implement`, I want `/retro` to find the run's code changes even though the run branch is gone, so that Corrections made during the run still count.
16. As a developer typing `/retro` on a named past session, I want the same Correction check on that session's changes, so that I can learn from a session after it ended.
17. As a developer typing `/retro` with work not yet committed, I want uncommitted changes included, so that a Correction still in the working tree counts.
18. As a developer, I want a Correction in a file my repo does not own to still produce its rule in my repo's own Coding standards, so that the lesson about how code gets written here is kept.
19. As a developer, I want the new rule in the same single commit as `/retro`'s other edits, so that I can undo the retrospective in one step.
20. As a developer, I want the new rule listed under applied items in the summary, with its path, so that I can see it and undo it.
21. As a developer, I want each rule kept to the smallest wording that encodes what the session showed, so that my Coding standards stay short.

## Implementation Decisions

- Only the `/retro` skill changes. `/code-review`, `/implement`, `/implement-oneshot`, `/implement-yolo`, and the implementer and oneshot agents already find and follow Coding standards, so they are left alone. No calling skill passes anything new to `/retro`.
- **Sources** gains the session's code changes. `/retro` takes them from the commits the session log records, plus any uncommitted changes in the working tree. This holds for the current session and for a named one. It does not depend on a branch or a recorded start commit, because `/implement` deletes its branch before `/retro` runs.
- The opening line saying `/code-review` and `/improve-data-structures` "own the product diff" is narrowed: they still review the diff, and `/retro` reads it only to find Corrections.
- The Correction test follows the glossary entry:
  - Old code means lines the session's diff removed or changed that were committed before the session's first commit. `git blame` shows which commit wrote each line.
  - The session must also show the old code was wrong: the user said so, a bug was being fixed, a test failed, or a review flagged it.
  - Code written earlier in the same session is not a Correction. The existing "reviewer missed a mistake" bar still covers what the reviewer let through.
  - A change that follows a changed requirement is not a Correction.
  - Who wrote the old code does not matter.
- A Correction becomes a rule only when the fix points to a pattern future code could repeat. `/retro` writes no rule when:
  - the Correction is a one-off fact, such as a wrong constant;
  - a check could catch the mistake, in which case the Automated checks category applies;
  - the Coding standards already hold the rule, in which case the reviewer-missed bar applies.
- When a Correction contradicts a rule already written, `/retro` changes or removes that rule rather than adding a second one.
- The Coding standards category gains the Correction as a second *Use when* bar, next to "the reviewer missed a mistake".
- The rule goes into the repo's existing Coding standards: `.agents/refs/` first, then a root `CODING_STANDARDS.md` or `CONTRIBUTING.md`. When none exists, `/retro` creates `.agents/refs/coding-standards.md`. A Correction in a file the repo does not own still writes its rule here.
- The rule is **High-priority**. It is applied without asking, only to **Owned files**, in the single retrospective commit, as the smallest change that encodes what the session showed. It appears under applied items in the summary.
- The glossary already defines **Correction** and names it under **High-priority**. [ADR-0050](../../docs/adr/0050-retro-learns-from-corrections.md) records why `/retro` now reads the product diff.

## Testing Decisions

- This repo is prose, and it has no test suite for skills. Verification is a read of the edited `SKILL.md` against each user story above, plus a `/writing-for-agents` pass, as `AGENTS.md` requires.
- A good check exercises behaviour, not wording: take a session that fixed old code after the user said it was wrong, and one that changed old code for a new requirement. Confirm the skill's text sends the first to a Coding standards rule and the second to nothing.
- Prior art: the existing Categories in the `/retro` skill, each with a *Use when* evidence bar that the new Correction bar sits beside.

## Out of Scope

- Turning same-session fixes into rules, including `/implement`'s fixer correcting a Step agent's code.
- Treating every change to old code as a lesson, without proof that the old code was wrong.
- Changes to `/code-review`, the implement skills, or the implementer and oneshot agents.
- Having calling skills pass a commit range or start commit to `/retro`.
- Writing rules into Coding standards this repository does not own.

## Further Notes

The user's brief called the target "coding-standards.md". The glossary term is **Coding standards**, and that name appears only as the file `/retro` creates when a repo has none.
