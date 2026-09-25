---
name: doctor
description: "Removes implemented Spec and Idea documents, and brings every ADR to state the decision in force."
disable-model-invocation: true
---

# Doctor

Keep a project's decision documents healthy: clear out Specs and Ideas that already shipped, and bring every ADR in `docs/adr/` to the shape where it states the decision in force, as things stand today — see [domain-modeling/ADR-FORMAT.md](../domain-modeling/ADR-FORMAT.md) for that shape. Act on your own judgement from start to finish: make every change below, commit them all in one commit, then report.

## Specs and Ideas

Go through the Idea (`.agents/ideas/`) and Spec (`.agents/specs/`) documents and remove every one that has been implemented. Judge that from the codebase; a status the document states is a hint at most.
When you remove a Spec, also remove every `Blocked by: <spec-slug>` line in another Spec that names it.

## ADRs

Read every ADR in every `docs/adr/` folder the project has: the root one, plus every folder a `CONTEXT-MAP.md` lists.

Every change in this section keeps the project's own section layout (Context / Decision / Consequences, or whatever it already uses) — reshape what an ADR says, not how it's laid out.

### Find chains

A **chain** is the set of ADRs that record one decision at different points in time. Find one from:

- a `status:` frontmatter line (`superseded by ADR-NNNN`, `partially superseded by ADR-NNNN`)
- a newer ADR whose body says it replaces part of an older one, even with no `status:` line pointing back to it

### Fold each chain

Fold each chain into the ADR with the newest number: merge only the parts that overlap, keeping whatever part of an older ADR no newer one replaced. Delete an older file once nothing of its own remains in the chain.

### Delete reversed decisions

An ADR whose `status:` line marks it superseded, deprecated, or rejected, with no newer ADR named there or found replacing it, records a decision reversed with nothing in its place. Delete it.

### Remove status lines

Remove the `status:` line from every ADR you keep: a Folded one, an older one keeping parts of its own, and every ADR outside any chain (`accepted`, `proposed`, and the like). Remove the frontmatter block too when `status:` was its only field. An ADR in `docs/adr/` is in force by being there.

### Rewrite ADRs that tell history

Rewrite every ADR whose text narrates history — "used to", "ADR-NNNN had…", "Superseded:" — so it states the decision as it stands today, whether or not anything ever replaced it.

### Update every link

Grep the whole repo for every ADR you Folded, renamed, or deleted, and fix every link to it — in skills, READMEs, code comments, anywhere a path or an `ADR-NNNN` reference appears. A link to a deleted ADR with no Folded successor goes, along with any words that only make sense beside it.

### Flag contradictions

When the code contradicts an ADR and no newer ADR explains why, list the mismatch and leave that ADR as written — the contradiction is a bug in the code, not license to rewrite the rule it breaks.

Flag the same way an ADR whose Spec was dropped before it landed: a decision never built should not read as one still in force, but this run reports it rather than rewriting it. An ADR is written in the same commit as its Spec, so `git log --follow` on the ADR lists the commits that wrote it, and the newest one that also added a file under `.agents/specs/` names its Spec. That Spec was dropped when it is gone from `.agents/specs/` and the code never built what it planned. When no such commit exists, this check has nothing to go on for that ADR.

## Report

Close with what you Folded, rewrote, deleted, and flagged — the reader's way of knowing what to look at in the diff. Run the `/plain-language` skill for the report.
