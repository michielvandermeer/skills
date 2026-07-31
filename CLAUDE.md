# mvdmio Skills

This repo *is* the skills. Every change here is an edit to prose in a `SKILL.md` or a supporting reference file — there is no application to run and no test suite.

## Grilling sessions end in edits, not a Spec

`/grill-with-docs` normally chains into `/to-spec`. **In this repo it does not.** When a grilling session reaches shared understanding, apply the changes to the skill files directly.

A Spec exists to brief an `/implement` agent session that will not have the design conversation in its context. Here the driving session already holds the whole design tree, and the work is a handful of markdown edits — so writing `.agents/specs/<slug>.md` first buys nothing and adds a document to keep current. The same goes for `/implement`: edit the files.

What the session still owes:

- `CONTEXT.md` entries for terms it settled, and ADRs in `docs/adr/` on the three-part test — that is `/domain-modeling` doing its job, not spec overhead.
- A commit covering every file the change touched.

## Before editing a skill

Read `skills/writing-great-skills/SKILL.md` and match it. Its house style is the standard this repo holds itself to — leading words over restatement, aggressive pruning of no-ops, positive phrasing over prohibition.

That density is for the source, which only the agent reads. Anything a skill puts in front of a *person* runs at the bar in `skills/plain-language/SKILL.md` — see [ADR-0009](docs/adr/0009-plain-language-for-output-not-source.md).

`CONTEXT.md` is the glossary for how the skills talk about the documents they read and write, and about each other. Use its terms exactly; add to it when a change coins one. It is a glossary and nothing else — rules belong in an ADR.
