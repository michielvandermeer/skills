---
name: doctor
description: "Moves documents into this project's canonical .agents/ layout, removes implemented Spec and Idea documents, and brings every ADR to state the decision in force."
disable-model-invocation: true
---

# Doctor

Keep a project's decision documents healthy: move every document into its canonical `.agents/` location, clear out Specs and Ideas that already shipped, and bring every ADR in `docs/adr/` to the shape where it states the decision in force, as things stand today — see [domain-modeling/ADR-FORMAT.md](../domain-modeling/ADR-FORMAT.md) for that shape. Act on your own judgement from start to finish: make every change below, commit them all in one commit, then report.

## Layout

Run this pass first, so a Spec or Idea moved out of an old location is also visible to the Specs and Ideas pass below.

Find every Markdown and near-Markdown (`.html`) document in the project, skipping `.git/`, `node_modules/`, `vendor/`, build output, `.agents/steps/`, `.agents/worktrees/`, and anything already sitting in its canonical location. Work only on the checkout you're running in — never touch another worktree or branch.

When a root `CONTEXT-MAP.md` exists, read [MULTI-CONTEXT.md](MULTI-CONTEXT.md) before moving anything: it decides which `docs/adr/` an ADR goes to.

### Canonical locations

| Document type | Canonical location |
|---|---|
| Spec (also plan and PRD) | `.agents/specs/<slug>.md` |
| Idea | `.agents/ideas/<slug>.md` |
| ADR | `docs/adr/<NNNN>-<slug>.md`, or a context's own `docs/adr/` in a multi-context repo |
| Coding standards (also contribution guidelines) | `.agents/refs/<slug>.md` |
| Issue, Decision ticket, and Map | `.agents/issues/<effort>/` |
| Architecture review | `.agents/architecture-reviews/<timestamp>/` — `report.md` and `report.html` |
| Codebase audit | `.agents/codebase-audits/<timestamp>/report.md` |
| Prototype | `.agents/prototypes/<slug>/` |

`.agents/refinements/` is not a canonical location any more. An old refinement converts to an Idea — see below.

### Mechanical moves

Read [LEGACY-MOVES.md](LEGACY-MOVES.md) for the old layouts whose destination follows from the source path alone — a `.scratch/` tracker, flat session output that should be a folder, a flat refinement. Relocate the whole tree; don't read these file by file.

### Classify everything else by content shape

Classify each remaining document by what it actually contains. Filename and current directory are hints at best — a document could be anywhere.

- **Spec**: has (or is clearly meant to have) sections like Problem Statement, Solution, User Stories, Implementation Decisions, Testing Decisions, Out of Scope — the `/to-spec` template — or a `Status:` line with a triage role plus prose describing a feature to build.
- **Idea**: has sections like Motivation, Goal, Decisions (locked), Out of scope, Open questions — the idea-doc shape `/validate-spec` checks against. Looser and earlier-stage than a Spec; no implementation detail.
- **ADR**: the shape in [domain-modeling/ADR-FORMAT.md](../domain-modeling/ADR-FORMAT.md) — a short title plus 1-3 sentences of context/decision/why, with or without a `status:` line, optionally Considered Options or Consequences. Usually sequentially numbered. The ADR pass below strips any status line once the ADR lands.
- **Coding standards**: documents how code should be written or how the repo/team works, contribution guidelines included. Common filenames: `CODING_STANDARDS.md`, `CONTRIBUTING.md`, `STYLEGUIDE.md`.
- **Old refinement**: the legacy `/refine` shape — Intent, How it works today, In scope, Out of scope, Prototype, Open Questions — or an older variant: Introduction, Use cases, Scope, Notes, and older still a Technical details section. Functional throughout, with no implementation decisions and no `Status:` line. `/refine` no longer writes this shape; it's a source only, and it converts to an Idea (below).
- **Issue**: a `Category:` line and a `Status:` line near the top.
- **Decision ticket**: a `Type:` line and a `## Question` section.
- **Map**: a file named `map.md` with `## Destination` and `## Decisions so far` sections.
- **Architecture review**: matches the report shape from `/improve-codebase-architecture` — cards with What this does/Files/Problem/Solution/Wins/Before-After diagram/Recommendation strength, a Top recommendation section. A review written before the current card contract says `Benefits` where this one says `Wins`, and carries no `What this does` at all. Usually a `.md`/`.html` pair sharing a timestamp.
- **Codebase audit**: matches the report shape from `/codebase-audit` — a coverage-contract table of subsystems with ownership boundaries and queued/recommend/skip status, recommendations with evidence/scope/risk/validation, explicit skips, and a priority ranking. Usually a `report.md` in a timestamp folder.

Prototypes get no content shape: a Prototype has no marker file and is plain app code or HTML, so a content match would risk moving real code. A Prototype moves only as the `prototype/` folder of an old refinement (below).

A document that matches no shape cleanly is **unclassified**. Leave it where it is and list it in the report.

### An old refinement becomes an Idea

Apply this to every folder under `.agents/refinements/`, and to a flat or loose refinement-shaped document found anywhere. The slug is the folder's name, or the file's own name for a flat or loose document.

- The Idea at `.agents/ideas/<slug>.md` is `complete.md` as it stands. When the folder has no `complete.md`, the Idea is `session.md` as it stands instead.
- Delete `session.md` once `complete.md` exists to read from. Always delete `complete.html`.
- Move a `prototype/` folder inside the refinement to `.agents/prototypes/<slug>/`, and add one line to the Idea naming that path.
- Remove the emptied refinement folder, and `.agents/refinements/` itself once nothing is left in it.
- An Idea or Prototype folder that already holds that slug is a collision (see Moving).

### Issues, tickets, and Maps

An Issue, Decision ticket, or Map moves together with its whole parent folder to `.agents/issues/<effort>/`, where `<effort>` is that folder's name — an effort's tickets stay together with its Map. One found with no folder of its own around it, such as a loose file at the repo root, is left in place and listed in the report: `/doctor` never invents an effort folder to hold it.

### ADR numbers

A moved ADR keeps its number when that number is free in its target `docs/adr/`. One with no number gets the next free number there, found by scanning that folder. One whose number is already taken there is a collision (see Moving), not a move.

### Moving

Move with `git mv`, creating destination folders as needed — this keeps each file's history. A move whose destination already exists is a **collision**: leave the document where it is and list it, and the file already occupying the destination, in the report.

Done when every document found sits in its canonical location or is listed in the report.

## Specs and Ideas

Go through the Idea (`.agents/ideas/`) and Spec (`.agents/specs/`) documents and remove every one that has been implemented. Judge that from the codebase; a status the document states is a hint at most.
When you remove a Spec, also remove every `Blocked by: <spec-slug>` line in another Spec that names it.
When you remove an Idea that names a folder under `.agents/prototypes/` as its Prototype, delete that folder too — no document points at it any more.

Done when every Spec and Idea left describes work the codebase does not have yet.

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

### Align with the code

Check every ADR you keep against the code, and bring it in line where the decision moved on.

Dispatch `skills:explorer` agents, each with a batch of about ten ADRs. In a multi-context repo, a batch holds one context's ADRs and the explorer reads that context's code. Ask each explorer to return, for every claim an ADR makes that the code contradicts:

- the claim, and the code that contradicts it, with file and line
- any **intent** behind the change, made after the ADR's decision: a migration, a commit whose message states the change, or a newer Spec or ADR that covers it
- the reason the commit that changed the code gives, if any

Give each batch the Specs its ADRs came from, too. An ADR is written in the same commit as its Spec, so `git log --follow` on the ADR lists the commits that wrote it, and the newest one that also added a file under `.agents/specs/` names its Spec; an ADR with no such commit has no Spec to check. When that Spec's file is gone from `.agents/specs/`, pass the explorer the commit's SHA and the Spec's path, and ask which parts of what the Spec planned the code has; it reads the Spec with `git show <sha>:<path>`. Judge that ADR against what was built: delete it when nothing was, and rewrite it to describe the part that was built when the code lacks the rest.

Wait for every report; the judgement is yours. Judge each mismatch:

- **Moved on** — the change has intent. Rewrite the ADR in place as [domain-modeling/ADR-FORMAT.md](../domain-modeling/ADR-FORMAT.md) sets out, with the smallest edit that makes it state what the code does; the parts that still hold keep their wording. In the rewritten ADR, state the reason the commit that changed the code gives, or say that the reason was not recorded when git gives none. Delete the ADR when the code keeps nothing of its decision.
- **Bug** — the change has no intent. The ADR wins: leave that claim as written. Leftover code the decision already removed is a bug too, even when an older migration or commit built it.

Application code stays as it is, and the report is the only record of a bug.

Done when every ADR you keep has no `status:` line, states the decision in force, and agrees with the code — or disagrees only where the code has a bug the report names.

## Update every link

Grep the whole repo for every path the Layout pass moved and every ADR you Folded, renamed, or deleted — search both the old path and the bare filename, and include `CLAUDE.md` and `AGENTS.md`. Fix every link you find, in skills, READMEs, code comments, anywhere a path, a bare filename, or an `ADR-NNNN` reference appears. A link to a deleted ADR with no Folded successor goes, along with any words that only make sense beside it.

Done when every old path and bare filename greps clean across the repo.

## Report

Close with what moved and where, what stayed and why (unclassified, collision, no effort folder), and what you Folded, rewrote, and deleted among the ADRs, with the evidence for each ADR changed because of the code — the reader's way of knowing what to look at in the diff. List every bug the code check found, with its evidence and a suggestion to take it to `/triage`. Run the `/plain-language` skill for the report.

Done when every move, every document left where it was, every ADR you Folded, rewrote, or deleted, and every bug appears in the report. Then run `/retro`.
