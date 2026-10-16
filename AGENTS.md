# mvdmio Skills

This repo *is* the skills. Every change is prose in a `SKILL.md` or a supporting reference file. The host invokes the **installed plugin**, not this checkout.

A confirmed `/grill-with-docs` Read-back that names a change is edited in this checkout: glossary, ADR, and the skill edit in one commit, which also closes the Issue the session started from as done. Its Changelog entry follows in a `changelog:` commit of its own: under `# Changelog` in `CHANGELOG.md`, newest first, a `## yyyy-mm-dd: <title>` heading of at most six words, then one paragraph of at most three sentences a user of the skills reads once — what changed for them, and what went wrong before. A change only an agent or a maintainer of this repo notices — a Grilling profile, a `/retro` edit — gets no entry. A `/triage` problem whose ending would be Spec is edited the same way. `/to-spec` and `/implement` stay unused. Read and follow `skills/retro/SKILL.md`, then point the installed plugin at the commit those steps left: push `master`, then run `claude plugin marketplace update mvdmio` and `claude plugin update skills@mvdmio` (on Grok, `grok plugin update`). Both hosts install from origin, so an unpushed commit never reaches them. A Read-back that names no change writes no Spec, keeps glossary entries already written, and still runs `/retro`.

## Editing agent documents

Match `skills/writing-for-agents/SKILL.md` on every skill file, `AGENTS.md`, or `CLAUDE.md` you edit. Run `/writing-for-agents` on them after.

Human-facing skill output runs at `skills/technical-writing/SKILL.md` — see [ADR-0009](docs/adr/0009-skill-output-follows-technical-writing.md).

`CONTEXT.md` is the glossary for how the skills talk about the documents they read and write, and about each other. Use its terms exactly; add to it when a change coins one. Rules belong in an ADR.
