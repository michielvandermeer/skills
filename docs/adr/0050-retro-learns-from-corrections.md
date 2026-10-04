# `/retro` reads the session's code changes to learn from Corrections

`/retro` reads the code the session changed and looks for **Corrections**. When a session fixed code that an earlier session had built wrong, the lesson would otherwise go unrecorded and the next session could make the same mistake. When a Correction points to a pattern that future code could repeat, `/retro` writes a rule for it into the repo's Coding standards. That rule is **High-priority**, so `/retro` applies it without asking. An edit to an existing Run recipe is a Correction too: when a command could have caught what steered the agent wrong, `/retro` adds that command to the recipe's Check section ([ADR-0053](0053-green-needs-a-proof.md)); otherwise it records nothing, because the corrected recipe already holds the lesson.

Counting every change to old code was rejected. A change that follows a new requirement would then become a rule nobody asked for, and a wrong rule binds every later implementer. Counting code written and fixed within the same session was rejected too. The reviewer already catches those mistakes on every run, and the existing "reviewer missed a mistake" category already covers what it lets through. Having each calling skill pass a commit range was rejected, because the session log already records the commits the session made.

## Consequences

- `/code-review` and `/improve-data-structures` still review the product diff. `/retro` reads it only to find Corrections.
- A repo with no Coding standards gets `.agents/refs/coding-standards.md`, the first time a Correction produces a rule.
- `/retro` writes no rule for a one-off fact. It writes no rule for a mistake a check could catch, which the Automated checks category covers. It writes no rule when the Coding standards already hold one.
