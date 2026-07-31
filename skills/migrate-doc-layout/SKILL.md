---
name: migrate-doc-layout
description: Move documents that predate this project's canonical .agents/ layout into it.
disable-model-invocation: true
---

# Migrate Doc Layout

These skills assume a fixed per-repo layout for the documents they read and write:

| Document type | Canonical location |
|---|---|
| Spec / plan / PRD | `.agents/specs/<slug>.md` |
| Idea (feeds a `/grilling` session) | `.agents/ideas/<slug>.md` |
| ADR | `docs/adr/<NNNN>-<slug>.md` |
| Skill-supporting reference (coding standards, etc.) | `.agents/refs/<slug>.md` |
| Refinement | `.agents/refinements/<slug>/` — `session.md`, `complete.md`, and their `.html` renders |
| Architecture review | `.agents/architecture-reviews/<timestamp>/` — `report.md` and `report.html` |

Older projects — or ones that adopted these skills before this layout existed — often have the same kinds of documents scattered elsewhere (`.agents/plans/`, `docs/specs/`, a root `CODING_STANDARDS.md`, etc.). This skill finds them and relocates them.

Two kinds of relocation run through the same flow. A **classified move** is one where the destination has to be inferred from what a document contains — most of this skill. A **mechanical move** is one where a known legacy layout fixes the destination from the source path alone, so the tree relocates without any document being read; those layouts live in [LEGACY-MOVES.md](LEGACY-MOVES.md).

## Process

### 1. Explore

Search the repo for markdown (and near-markdown, e.g. `.html` reports) documents, skipping `.git/`, `node_modules/`, `vendor/`, and build output directories. Skip anything already sitting in its canonical location — this skill moves misplaced documents only.

Read [LEGACY-MOVES.md](LEGACY-MOVES.md) if you find a `.scratch/` tree, or flat files where the table above says folder. Those are mechanical moves and skip step 2 entirely.

Done when every candidate document has a path and you know which ones are mechanical.

### 2. Classify by content shape

Classify each remaining document by what it actually contains, matching the templates the other skills already define. Filename and current directory are hints at best — a doc could be anywhere.

- **Spec**: has (or is clearly meant to have) sections like Problem Statement, Solution, User Stories, Implementation Decisions, Testing Decisions, Out of Scope — the `/to-spec` template — or a `Status:` line with a triage role plus prose describing a feature to build.
- **Idea**: has sections like Motivation, Goal, Decisions (locked), Out of scope, Open questions — the idea-doc shape `/validate-spec` checks against. Looser and earlier-stage than a spec; no implementation detail.
- **ADR**: a short title plus 1-3 sentences of context/decision/why, optionally with Status frontmatter, Considered Options, or Consequences sections — the shape in `domain-modeling/ADR-FORMAT.md`. Usually sequentially numbered.
- **Reference / skill-supporting doc**: documents how code should be written or how the repo/team works — coding standards, contribution guidelines, style guides. Common filenames: `CODING_STANDARDS.md`, `CONTRIBUTING.md`, `STYLEGUIDE.md`.
- **Refinement**: the `/refine` shape — Introduction, Open Questions, Use cases, Scope, Out-of-scope, Technical details, Notes for a finished one; Intent, How it works today, What changes, Use Cases for one still in session. Functional throughout, with no implementation decisions and no `Status:` line.
- **Architecture review**: matches the report shape from `/improve-codebase-architecture` — cards with What this does/Files/Problem/Solution/Wins/Before-After diagram/Recommendation strength, a Top recommendation section. A review written before the current card contract says `Benefits` where this one says `Wins`, and carries no `What this does` at all. Usually a `.md`/`.html` pair sharing a timestamp.

A document that matches no shape cleanly is **unclassified** — carry it to step 3 as such and let the user say what it is.

Done when every document carries a shape or the unclassified label.

### 3. Present findings and confirm

Show the user a table: current path → proposed new path, grouped by target folder. Call out:

- Any unclassified documents, asking the user what they are (or to skip them).
- Any filename collision at the destination (two docs that would land on the same path) — ask how to disambiguate, since which one keeps the name is the user's call.

Let the user edit the plan — drop entries, redirect a target path, reclassify something — before moving anything.

Done when the user has approved a plan with no unclassified entries and no collisions left in it.

### 4. Move

For each confirmed entry, `git mv` the file into its canonical folder, creating the folder if it doesn't exist yet. `git mv` preserves history where a plain move loses it.

Done when every approved entry sits at its new path.

### 5. Fix references

For each move, grep the repo for the old path and the old bare filename, and update every markdown link and plain-text path mention you find — including in `CLAUDE.md`/`AGENTS.md`.

Done when the old paths and bare filenames grep clean across the repo.

### 6. Report

Summarize what moved (old → new) and which files had references updated. Name anything still sitting where it started, and why the user left it there.
