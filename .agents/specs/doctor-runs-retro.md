# `/doctor` runs `/retro` when it finishes

Status: ready-for-agent

## Problem Statement

`/doctor` is a skill you type. It tidies a repository's agent documents: it moves them into the standard layout, removes Specs and Ideas that are already built, folds ADRs, fixes links, and reports what it did. Nine other skills you type start a **Retrospective** (`/retro`) when they finish. `/doctor` does not. So a `/doctor` run never turns what it ran into — a repository that keeps putting documents in the wrong place, a steering file that points at an old path — into suggestions for your agent setup. It also never applies the **High-priority** ones.

The list of these skills is also out of date. ADR-0038 names eight skills. ADR-0042 added `/implement-yolo`, but only in its own text, so the list in ADR-0038 never shows it.

## Solution

`/doctor` becomes a **Named session skill**. It runs its passes and makes its one commit as it does today, then posts its report in the chat. After the report, it runs `/retro` as its last step. `/retro` applies High-priority suggestions for **Owned files** in a second commit and puts the rest in the chat summary. This is exactly what the other Named session skills do.

ADR-0038 is rewritten in place so that its list names all ten Named session skills.

## User Stories

1. As a user who types `/doctor`, I want it to run `/retro` after its report, so that I get suggestions for my agent setup from the run without typing a second command.
2. As a user who types `/doctor`, I want the High-priority suggestions applied without being asked, so that the problem they fix doesn't come back in the next session.
3. As a user who types `/doctor`, I want `/doctor`'s own changes to stay in their single commit, so that I can review or revert the tidy-up apart from the setup edits.
4. As a user who types `/doctor`, I want any `/retro` edits in a separate commit after `/doctor`'s commit, so that the two kinds of change never mix.
5. As a user who types `/doctor` on a repository that is already tidy, I want `/retro` to run anyway, so that I can tell the step ran and the behaviour is the same on every run.
6. As a user who types `/doctor`, I want the report to come before the retrospective summary, so that I read what `/doctor` changed first.
7. As a user who types `/doctor`, I want the session to be finished only when the retrospective summary is in the chat, so that I know when the work is done.
8. As a user who types `/doctor` in an app repository, I want `/retro` to change only files that repository owns, so that the installed plugin copy is never edited.
9. As a user who types `/doctor` in an app repository, I want suggestions for files the repository doesn't own to appear in the summary, labelled, so that I can apply them myself.
10. As a user who types `/doctor`, I want `/doctor` to keep running from start to finish without asking me anything, so that adding the retrospective doesn't add a pause.
11. As a maintainer of this repository, I want ADR-0038 to list every Named session skill, so that there is one list I can read without checking other ADRs.
12. As a maintainer, I want `/implement-yolo` written into that list, so that the list matches what the skills do.
13. As a maintainer, I want `/doctor` to use the same closing wording as `/codebase-audit` and `/triage`, so that the skills stay alike and a future edit finds the pattern easily.
14. As a maintainer, I want `/retro` itself left unchanged, so that a new caller costs one line in that caller.

## Implementation Decisions

- The `/doctor` skill changes in one place: its Report section ends with the line "Then run `/retro`." This is the wording `/codebase-audit` and `/triage` use. Nothing else in `/doctor` changes. That includes its passes, its single commit, its "act on your own judgement" rule, and its use of `/plain-language` for the report.
- `/retro` runs after the report, even when `/doctor` moved or removed nothing. No Named session skill skips the Retrospective.
- `/doctor` never pauses for the user, so there is no halt case to handle. `/retro` starts when the report is in the chat.
- Commits follow ADR-0038: `/doctor`'s own commit comes first, and any `/retro` edits to Owned files go in one commit after it.
- `/retro` does not change. Its only rule about callers is that it runs when the typed skill has reached its own done condition, and `/doctor` meets that rule once its report is posted.
- `/doctor`'s edits to documents and ADRs are not **Corrections**. Nothing in a `/doctor` run shows the old files were wrong in the way a Correction requires. So `/retro` writes no Coding standards rule from them.
- No other skill runs `/doctor`, so nesting needs no handling. Only the skill you typed starts a Retrospective.
- ADR-0038 is rewritten in place in this Spec's commit, as ADR-0050 requires. Its list is now `/implement`, `/implement-oneshot`, `/implement-yolo`, `/grill-with-docs`, `/triage`, `/wayfinder`, `/refine`, `/codebase-audit`, `/improve-codebase-architecture`, and `/doctor`. The note "list extended by ADR-0042" came off its frontmatter. ADR-0042's own line saying `/implement-yolo` joins the list stays, because it is still true.
- The skill file edit must match the repo's `/writing-for-agents` standard, and `/writing-for-agents` runs on it afterwards, as `AGENTS.md` requires.

## Testing Decisions

- This repository has no automated tests. Every change is prose in a skill file.
- A good check looks at what `/doctor` does from the outside. The skill must end with the `/retro` line after its report, and must say nothing that contradicts ADR-0038.
- Verify by reading the edited `/doctor` skill next to `/codebase-audit` and `/triage`. The closing lines should match, and the report should stay the last step before `/retro`.
- Grep the repository for every place that lists Named session skills. ADR-0038 should be the only full list in force, and it should include `/doctor` and `/implement-yolo`. ADR-0023 still holds an older list; it is superseded and belongs to the chain this Spec leaves alone.

## Out of Scope

- Folding the rest of ADR-0038's chain (ADR-0021, 0023, 0024, 0034, 0040) and removing `status:` lines. That is the work `/doctor` itself does.
- Any change to `/retro`.
- Any change to `/doctor`'s passes, its commit, or its report contents.
- `CONTEXT.md`. "Named session skill" is defined without a list, so it already covers `/doctor`.
- The README. Its Retrospective line names `/implement` only as an example.
- The duplicate ADR number 0050, which `.agents/ideas/duplicate-adr-numbers.md` already covers.

## Further Notes

The request came from a `/grill-with-docs` session. That session settled every decision as a Declaration (a decision stated rather than asked), because the nine existing Named session skills already set the pattern.
