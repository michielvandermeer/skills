---
name: fix-merge-conflicts
description: Resolve an in-progress git merge or rebase conflict non-interactively, validate build and tests, and finish the operation
---

# Fix merge conflicts

## Trigger

A merge or rebase stopped on conflicts and needs a reliable path to a buildable state.

## Workflow

1. Find every conflicting file from `git status` and the conflict markers, and whether a merge or a rebase is in progress.
2. Read each side's intent: the commit messages on both sides, and the Spec, ADRs, `CONTEXT.md`, PR, or issue that motivated them when one exists.
3. Resolve each hunk with minimal, correctness-first edits, using only behavior already on one side or the other. Preserve both intents when they can both stand. Otherwise pick the one that matches the merge's goal, keeps public behavior stable, and compiles, and note the trade-off.
4. Regenerate lockfiles with package manager tools instead of hand-editing.
5. Run the project's compile, lint, and relevant tests, and fix what the merge broke.
6. Finish the operation: stage everything and commit the merge, or `git rebase --continue` until every commit is replayed, resolving each new stop the same way.

## Guardrails

- Always resolve; never `--abort`.
- Keep changes minimal and readable.
- Do not leave conflict markers in any file.
- Avoid broad refactors while resolving conflicts.
- Do not push or tag during conflict resolution.

## Output

- Files resolved
- Notable resolution choices and trade-offs
- Build/test outcome
