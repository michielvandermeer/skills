# `/retro` reads the session's code changes to learn from Corrections

`/retro` reads the code the session changed and looks for **Corrections**. When a session fixed code that an earlier session had built wrong, the lesson would otherwise go unrecorded and the next session could make the same mistake. An edit to an existing Verify skill is a Correction too: when a check could have caught what steered the agent wrong, `/retro` adds that check to the skill's Doctor section. Otherwise it records nothing, because the corrected skill already holds the lesson.

A lesson goes to the strongest mechanism that can hold it, in the order of [poteto's inverse pyramid](https://x.com/poteto/status/2111133080526495985): a **Structural fix** first, then a check, then a Coding standards rule, leaving the least to human review. Agents copy what exists and take the shortest path, so code that makes the wrong thing impossible outlasts any rule. `/retro` searches the codebase for every other copy of the corrected pattern for the same reason.

A Structural fix, and a check that needs new code such as a Roslyn analyzer rule or a test, is a product change that needs review. `/retro` files it as one Issue per lesson in `needs-triage`, naming the fix, the check and where it goes, and every copy. An open Issue that already covers the fix gets a comment instead. `/retro` applies only what takes no new code: a check that configures a tool the repo already runs, or a Coding standards rule. A lesson that gets an Issue also gets that applied guard right away, and the Issue names it for deletion once the fix lands. Applying a check deletes the written rule it now enforces. Rules and checks are **High-priority**, so `/retro` applies them without asking.

## Considered Options

- **Applying a Structural fix without asking.** Rejected: it lands product code unreviewed, which is the work an `/implement` run exists for.
- **Listing a Structural fix in the chat summary only.** Rejected: the summary is gone when the session ends, so the mechanism the inverse pyramid weighs most would be the one least likely to happen.
- **Filing an Issue with no guard until it lands.** Rejected: an Issue can wait weeks in triage while the mistake and its copies stay open to the next agent.
- **Keeping a rule's sentence once a check enforces it.** Rejected: the check's failure names the fix, and the sentence is prose every session reads for nothing.
- **Counting every change to old code.** Rejected: a change that follows a new requirement would become a rule nobody asked for, and a wrong rule binds every later implementer.
- **Counting code written and fixed within the same session.** Rejected: the reviewer already catches those mistakes on every run, and the "reviewer missed a mistake" category covers what it lets through.
- **Having each calling skill pass a commit range.** Rejected: the session log already records the commits the session made.

## Consequences

- `/code-review` still reviews the product diff. `/retro` reads it only to find Corrections.
- A repo with no Coding standards gets `.agents/refs/coding-standards.md`, the first time a Correction produces a rule.
- `/retro` writes no rule for a one-off fact, and none when the Coding standards already hold one.
- `/retro` writes to the Tracker. Under benchmark mode its filing is a `bench-log` line ([ADR-0066](0066-a-benchmark-run-writes-nothing-outside-its-checkout.md)).
