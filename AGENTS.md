# mvdmio Skills

This repo *is* the skills. Every change is prose in a `SKILL.md` or a supporting reference file. Skip `/improve-data-structures` on every implement run. The host invokes the **installed plugin**, not this checkout.

A confirmed `/grill-with-docs` Read-back that names a change is edited in this checkout: glossary, ADR, and the skill edit in one commit. A `/triage` problem whose ending would be Spec is edited the same way. `/to-spec` and the implement commands stay unused. Run `/retro`, then point the installed plugin at the commit those steps left. `grok plugin update` follows origin and misses an unpushed commit. A Read-back that names no change writes no Spec, keeps glossary entries already written, and still runs `/retro`.

## Editing agent documents

Match `skills/writing-for-agents/SKILL.md` on every skill file, `AGENTS.md`, or `CLAUDE.md` you edit. Run `/writing-for-agents` on them after.

Human-facing skill output runs at `skills/plain-language/SKILL.md` — see [ADR-0009](docs/adr/0009-plain-language-for-output-not-source.md).

`CONTEXT.md` is the glossary for how the skills talk about the documents they read and write, and about each other. Use its terms exactly; add to it when a change coins one. Rules belong in an ADR.
