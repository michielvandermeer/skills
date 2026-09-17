# Step agents read the repo's coding standards

Status: ready-for-agent

## Problem Statement

You ran `/implement`. A Step agent wrote tests that only assert what a test fake already returns. Your coding standards already call those tests harmful.

`/code-review` found the tests later. A fixer then rewrote them. You paid a second session to undo work the first agent should not have written.

The Step agent was told to read the Spec, the Step, the glossary, the ADRs, and the Spec's testing decisions. It was not told to read the coding standards. The Oneshot agent has the same gap.

## Solution

Before a Step agent or an Oneshot agent writes code, it reads the repo's coding-standards documents. It follows them when it writes tests and code.

The Driving session finds those documents the same way `/code-review` does, and puts the paths in the agent's prompt next to the glossary and the ADRs.

The skill does not copy a rule out of a consuming repo. A repo with no coding-standards document is unchanged. `/code-review` still runs after the work, as today.

## User Stories

1. As a developer, I want a Step agent to read my coding standards before it writes tests, so it does not ship tests those standards already forbid.

2. As a developer whose coding standards call tautological tests harmful, I want a Step agent not to write a test that only asserts a fake's own return, so `/code-review` is not the first place that rule is applied.

3. As a developer, I want that reading to happen on every Step, so Step 01 is not a special case that skips the standards.

4. As a developer who runs `/implement-oneshot`, I want the Oneshot agent to read the same documents, so skipping the Planner does not skip the standards.

5. As a Driving session, I want to find the coding-standards documents the same way `/code-review` finds them, so the implementer and the reviewer are not looking in different places.

6. As a Driving session, I want those paths in the agent's prompt next to the glossary and the ADRs, so "what to read" stays one list.

7. As a Driving session, I want a missing coding-standards document to add nothing to that prompt, so a repo without one does not invent a file.

8. As a Driving session, I want files in the references folder that are not about how code should be written to stay out of that prompt, so a Step agent does not load issue-tracker notes, build commands, or workflow.

9. As a developer, I want the Spec's testing decisions to still say what to test, so coding standards govern how those tests are written and do not replace the Spec.

10. As a developer, I want `/code-review` to still run after the Steps, so reading the standards before writing is not the only check.

11. As a developer, I want the skill not to restate "tautological tests are harmful", so the consuming repo stays the owner of that rule.

12. As a developer, I want the skill not to mention Stripe, so a payment-fake example from one retro does not become a plugin rule.

13. As a later reader of the Step agent file, I want "what to read" to stay on the dispatch prompt, so the agent file does not grow a second discovery of the same files.

14. As a later reader of the Oneshot agent file, I want the same split, so the Step agent and the Oneshot agent stay aligned.

15. As a developer, I want the Planner left as it is, so a plan that writes behaviour still does not load coding standards.

16. As a developer, I want the fixer left as it is, so this change stops bad tests being written rather than adding a second review prompt.

17. As a developer whose `CLAUDE.md` already points at coding standards, I want that pointer left as it is, so this change does not rewrite consuming repos.

18. As a developer, I want a pointer in `CLAUDE.md` not to be the only way a Step agent reaches the standards, so the prompt the Driving session writes still names the files.

19. As a developer whose coding standards live in a root-level file instead of the references folder, I want that file found, so a repo that has not moved the document still gets it read.

20. As a developer, I want existing patterns in the code to still fill leftover gaps, so coding standards join that close-the-gap set rather than replace it.

21. As a developer, I want Green still measured against the default branch, so reading standards does not change which tests must pass.

22. As a developer, I want no new glossary term for this, so "coding standards" stays ordinary words and "Step agent" stays the existing term.

23. As a developer, I want no new ADR, so adding a document the agent must read is not recorded as a hard-to-reverse choice.

24. As a later `/implement` run, I want a test that would fail the coding-standards review to not be written in the first place, so the fixer is not paid to delete it.

## Implementation Decisions

- `/implement`'s dispatch for each Step agent adds the repo's coding-standards sources to the prompt, beside the glossary and the ADRs. The Spec's testing decisions stay in that prompt and still govern what the Step tests.

- `/implement-oneshot`'s dispatch for the Oneshot agent adds the same sources in the same place.

- Discovery matches `/code-review`: look in the skill-supporting references folder first, then pick up a root-level coding-standards or contributing file when that is what the repo has. Only documents that say how code should be written go in the prompt. Other files in the references folder stay out of it.

- When discovery finds nothing, the prompt is unchanged from today.

- The Step agent file and the Oneshot agent file do not grow their own search for those documents. What to read stays the prompt, as it is for the glossary and the ADRs.

- The skill does not copy a consuming repo's rules, including the tautological-tests rule. Following the documents it was handed is enough. Leftover gaps still close from the Spec, the code, and existing patterns; the coding-standards documents join the documents the agent was handed.

- The Planner, the fixer, `/code-review`, and consuming-repo `CLAUDE.md` files are not part of this change. `/code-review` still runs after the Steps, as today.

- No `CONTEXT.md` entry. No new ADR.

## Testing Decisions

A good check is what the dispatch tells the agent to read, not how a sentence in the agent file is worded.

- The `/implement` dispatch names the coding-standards sources when those files exist, next to the glossary and the ADRs.
- The `/implement-oneshot` dispatch does the same.
- A checkout with no coding-standards document does not gain a new path in that prompt.
- The dispatch still names the Spec's testing decisions.
- The Step agent file and the Oneshot agent file do not contain a copied tautological-tests rule.

This repo has no automated suite for skill prose. The check is a read of the two dispatch lists against `/code-review`'s standards-source discovery, the way `/validate-spec` already reads a Spec against the current skills. Prior art for "the Driving session hands paths, the sub-agent reads them" is the glossary and ADR lines already in those prompts.

## Out of Scope

- Copying "tautological tests considered harmful" into the plugin.
- Loading every file in the references folder.
- Changing `/code-review`, the fixer, or the Planner.
- Editing `CLAUDE.md` or coding-standards files in consuming repos.
- Teaching the Step agent a definition of a tautological test.
- Changing Green, worktrees, or the three-line report.
- Adding a check that greps tests for fakes.

## Further Notes

The consuming-repo retro named the Step agent file. In this plugin, "what to read" lives on the Driving session's dispatch, not in that file. The same split already holds for the glossary and the ADRs. This Spec follows it.

`/code-review` already caught the tautological tests as a hard violation. This Spec makes the agent that writes the tests read the standards first, so the fixer is not the first reader of those documents.
