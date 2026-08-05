# mvdmio Skills

This repo *is* the skills. Every change is prose in a `SKILL.md` or a supporting reference file.

## Grilling ends in skill edits

`/grill-with-docs` normally chains into `/to-spec`. Here, when a grilling session's frontier is empty, edit the skill files directly — skip `/to-spec` and `/implement`. The driving session already holds the design tree; the work is a handful of markdown edits. A Spec only briefs a later `/implement` session that lacks that context.

Still owes:

- `/domain-modeling`: `CONTEXT.md` entries for terms settled, ADRs in `docs/adr/` on the three-part test
- A commit covering every file the change touched

## Editing agent documents

Match `skills/writing-for-agents/SKILL.md` on every skill file, `AGENTS.md`, or `CLAUDE.md` you edit. Run `/writing-for-agents` on them after.

Human-facing skill output runs at `skills/plain-language/SKILL.md` — see [ADR-0009](docs/adr/0009-plain-language-for-output-not-source.md).

`CONTEXT.md` is the glossary for how the skills talk about the documents they read and write, and about each other. Use its terms exactly; add to it when a change coins one. Rules belong in an ADR.

Before commit, run `/document-changes`.
