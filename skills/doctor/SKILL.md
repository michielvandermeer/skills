---
name: doctor
description: "Removes implemented Spec and Idea documents, and brings every ADR to state the decision in force."
disable-model-invocation: true
---

# Doctor

Keep a project's decision documents healthy: clear out Specs and Ideas that already shipped, and bring every ADR in `docs/adr/` to the shape where it states the decision in force, as things stand today — see [domain-modeling/ADR-FORMAT.md](../domain-modeling/ADR-FORMAT.md) for that shape. Make every change below in one commit, and end with a report of what changed — no confirmation asked first.

## Specs and Ideas

Go through the Idea (`.agents/ideas/`) and Spec (`.agents/specs/`) documents and remove all that have been implemented.
Do not just look at the status in the document; verify their status in the codebase.
When you remove a Spec, also remove every `Blocked by: <spec-slug>` line in another Spec that names it.

## ADRs

Read every ADR in every `docs/adr/` folder the project has: the root one, plus every folder a `CONTEXT-MAP.md` lists.

### Find chains

A **chain** is the set of ADRs that record one decision at different points in time. Find one from:

- a `status:` frontmatter line (`superseded by ADR-NNNN`, `partially superseded by ADR-NNNN`)
- a newer ADR whose body says it replaces part of an older one, even with no `status:` line pointing back to it

### Fold each chain

Fold each chain into the ADR with the newest number: merge only the parts that overlap, keeping whatever part of an older ADR no newer one replaced. Delete an older file once nothing of its own remains in the chain. Keep the project's own section layout (Context / Decision / Consequences, or whatever it already uses) — reshape what an ADR says, not how it's laid out.

### Rewrite ADRs that tell history

Rewrite every ADR whose text narrates history — "used to", "ADR-NNNN had…" — so it states the decision as it stands today, whether or not anything ever replaced it.

### Update every link

Grep the whole repo for every ADR you Folded, renamed, or deleted, and fix every link to it — in skills, READMEs, code comments, anywhere a path or an `ADR-NNNN` reference appears.

### Flag, don't fix

When the code contradicts an ADR and no newer ADR explains why, list the mismatch and change nothing in that ADR — the contradiction is a bug in the code, not license to rewrite the rule it breaks. Flag the same way an ADR whose Spec was dropped before it landed: a decision never built should not read as one still in force, but this run reports it rather than rewriting it.

## Report

Close with what you Folded, rewrote, deleted, and flagged — the reader's way of knowing what to look at in the diff.
