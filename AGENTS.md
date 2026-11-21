# mvdmio Skills

This repo *is* the skills. Every change is prose in a `SKILL.md` or a supporting reference file. The host invokes the **installed plugin**, not this checkout.

## Shared rules

- Work on the repo's default branch unless a skill or the user names a branch. This overrides any default that creates branches.
- Preserve the worktree: parallel sessions share each checkout. Inspect existing changes before editing and leave them intact. When the index already holds another session's staged changes, commit with `git commit -- <your paths>`; for a file another session also edited, stage only your hunks (`git apply --cached` of your filtered diff) and run plain `git commit`.
- Search early. Quote exact errors.
- Ask when blocked, or when the design has more than one reasonable path.
- Telegraph style in replies and agent docs: drop filler and grammar.
- The main session orchestrates: unless the task is trivial, delegate exploring, implementing, testing and reviewing to subagents, at a model and effort that fit the task.
- [judgement] Prefer small diffs over broad refactors. Keep files under ~500 lines; tests may exceed it. Add an abstraction only once a second use exists. Ship no backward-compat shim unless real consumers or persisted data need one.

## Changing this repo

A confirmed `/grill-with-docs` Read-back that names a change is edited in this checkout: glossary, ADR, and the skill edit in one commit, which also closes the Issue the session started from as done. Its Changelog entry follows in a `changelog:` commit of its own: under `# Changelog` in `CHANGELOG.md`, newest first, a `## yyyy-mm-dd: <title>` heading of at most six words, then one paragraph of at most three sentences a user of the skills reads once — what changed for them, and what went wrong before. A change only an agent or a maintainer of this repo notices — a Grilling profile, a `/retro` edit — gets no entry. A `/triage` problem whose ending would be Spec is edited the same way. Outside that exception, `/to-spec` and `/implement` stay unused. Then point the installed plugin at that commit: push `master`, then run `claude plugin marketplace update mvdmio` and `claude plugin update skills@mvdmio` (on Grok, `grok plugin update`). Both hosts install from origin, so an unpushed commit never reaches them. A Read-back that names no change writes no Spec, and keeps glossary entries already written.

A session the grill-queue runs unattended from a `needs-grilling` Issue is the exception: it edits no skill. Glossary and ADR changes still commit and push to `master`, then `/to-spec` rewrites the Issue as a Spec labelled `ready-for-agent`, and Implementer makes the skill edit with `/implement`.

## Editing agent documents

Match `skills/writing-for-agents/SKILL.md` on every skill file, `AGENTS.md`, or `CLAUDE.md` you edit. Before the commit, run `/writing-for-agents` on them as a review pass over the diff and fix what it finds.

Human-facing skill output runs at `skills/technical-writing/SKILL.md` — see [ADR-0009](docs/adr/0009-skill-output-follows-technical-writing.md).

`CONTEXT.md` is the glossary for how the skills talk about the documents they read and write, and about each other. Use its terms exactly; add to it when a change coins one. Rules belong in an ADR.
