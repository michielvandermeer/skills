---
name: migrate-doc-layout
description: Scan a repo for spec, idea, reference, and architecture-review documents that aren't yet in this project's canonical .agents/ layout, and move them there. Run once per repo, or whenever legacy-location docs turn up.
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
| Architecture review | `.agents/architecture-reviews/<timestamp>.md` (+ matching `.html`) |

Older projects — or ones that adopted these skills before this layout existed — often have the same kinds of documents scattered elsewhere (`.agents/plans/`, `docs/specs/`, a root `CODING_STANDARDS.md`, etc.). This skill finds them and relocates them.

This is a prompt-driven skill, not a deterministic script: explore, classify, present, confirm, then move.

## Process

### 1. Explore

Search the repo for markdown (and near-markdown, e.g. `.html` reports) documents, skipping `.git/`, `node_modules/`, `vendor/`, and build output directories. Skip anything already sitting in its canonical location — this skill only moves misplaced documents.

### 2. Classify by content shape

Don't rely on filename or current directory — a doc could be anywhere. Classify by what it actually contains, matching the templates the other skills already define:

- **Spec**: has (or is clearly meant to have) sections like Problem Statement, Solution, User Stories, Implementation Decisions, Testing Decisions, Out of Scope — the `/to-spec` template — or a `Status:` line with a triage role plus prose describing a feature to build.
- **Idea**: has sections like Motivation, Goal, Decisions (locked), Out of scope, Open questions — the idea-doc shape `/validate-spec` checks against. Looser and earlier-stage than a spec; no implementation detail.
- **ADR**: a short title plus 1-3 sentences of context/decision/why, optionally with Status frontmatter, Considered Options, or Consequences sections — the shape in `domain-modeling/ADR-FORMAT.md`. Usually sequentially numbered.
- **Reference / skill-supporting doc**: documents how code should be written or how the repo/team works — coding standards, contribution guidelines, style guides. Common filenames: `CODING_STANDARDS.md`, `CONTRIBUTING.md`, `STYLEGUIDE.md`.
- **Architecture review**: matches the report shape from `/improve-codebase-architecture` — cards with Files/Problem/Solution/Benefits/Before-After diagram/Recommendation strength, a Top recommendation section. Usually a `.md`/`.html` pair sharing a timestamp.

If a document doesn't clearly match any shape, don't guess — list it separately as unclassified and ask the user during step 3.

### 3. Present findings and confirm

Show the user a table: current path → proposed new path, grouped by target folder. Call out:

- Any unclassified documents, asking the user what they are (or to skip them).
- Any filename collision at the destination (two docs that would land on the same path) — ask how to disambiguate rather than picking for the user.

Let the user edit the plan — drop entries, redirect a target path, reclassify something — before moving anything.

### 4. Move

For each confirmed entry, `git mv` the file into its canonical folder (creating the folder if it doesn't exist yet). Using `git mv` over a plain move preserves history.

### 5. Fix references

After each move, grep the repo for the old path and the old bare filename. Update any markdown links or plain-text path mentions you find — including in `CLAUDE.md`/`AGENTS.md` — so the migration doesn't leave dangling references behind.

### 6. Report

Summarize what moved (old → new) and which files had references updated. Note anything left in place because it couldn't be classified even after asking.

## Also: the legacy `.scratch/` tracker

Repos that adopted these skills before [ADR-0003](../../docs/adr/0003-tracker-under-agents.md) keep their issue tracker under `.scratch/` — `triage` issues at `.scratch/<slug>/issues/<NN>-<slug>.md` and `wayfinder` maps at `.scratch/<effort>/map.md`. The tracker now lives at `.agents/issues/<slug>/`, with the nested `issues/` subfolder flattened away: tickets sit directly in the per-slug directory, maps alongside them.

Unlike the documents above, this is a mechanical directory move, not a content-shape classification — relocate the whole tree rather than classifying file by file:

- `.scratch/<slug>/issues/<NN>-<slug>.md` → `.agents/issues/<slug>/<NN>-<slug>.md` (lift tickets up one level)
- `.scratch/<slug>/map.md` → `.agents/issues/<slug>/map.md`

Fold it into the same present → confirm → `git mv` → fix-references flow as the document moves, then remove the now-empty `.scratch/` tree. Watch for a `<slug>/<NN>-<slug>.md` that would collide with an existing ticket at the destination, and treat it like any other collision in step 3.
