# A multi-context repo files work documents per context

In a repo with a `CONTEXT-MAP.md`, every work document the repo keeps under `.agents/` gets a context subfolder right after its kind folder: `.agents/prototypes/<context>/<slug>/`, and the same for Architecture reviews, Codebase audits, and Issues on the local Tracker. Work that belongs to no single context goes in `common`. A repo with several contexts sorts its work by them, as mvdmio-suite does, and ADRs, Changelogs, and Run recipes already sit per context. The layout is built in and keyed off the map, so a repo writes no setup for it. On GitHub or Jira, an Issue carries its context as a label instead, as the Tracker ref says ([ADR-0001](0001-each-repo-describes-its-tracker.md)).

The kind folder comes first so that every skill keeps the root path it already names and adds one level under it. `/doctor` keeps one table of canonical locations, with one rule for a multi-context repo.

## Considered Options

- One root `.agents/` for every repo. Rejected: it works against a layout that multi-context repos choose for themselves, and `/doctor` undid that layout on every run.
- Paths for Prototypes, Architecture reviews, and Codebase audits read from a ref the repo writes, the way Issues follow the Tracker ref. Rejected: these documents sit in the repo whatever Tracker it uses, so no repo needs a different place for them, and each repo could drift into its own shape.
- The context folder level first, `.agents/<context>/<kind>/`. Rejected: every skill's root path would change, not just gain a level.

## Consequences

- Steps, worktrees, and `.agents/refs/` take no context subfolder. A new slug must not already exist in another context subfolder of the same kind, so a lookup by slug finds one document and a Step folder keyed on a run's slug stays unique.
- A skill that cannot tell the context asks; `/doctor`, which never asks, uses `common`.
- `/doctor` moves a multi-context repo's root-level work documents, and an app-first `.agents/<app>/<kind>/` layout, into this shape.
