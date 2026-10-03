# A multi-context repo files work documents per context

In a repo with a `CONTEXT-MAP.md`, every work document gets a context subfolder right after its kind folder: `.agents/specs/<context>/<slug>.md`, `.agents/issues/<context>/<effort>/`, and the same for Ideas, Prototypes, Architecture reviews, and Codebase audits. Work that belongs to no single context goes in `common`. A repo with several contexts sorts its work by them, as mvdmio-suite does, and ADRs, Changelogs, and Run recipes already sit per context. The layout is built in and keyed off the map, so a repo still writes no setup for it, and [ADR-0001](0001-a-fixed-local-issue-tracker-except-on-a-github-issue.md) holds.

The kind folder comes first so that every skill keeps the root path it already names and adds one level under it. `/doctor` keeps one table of canonical locations, with one rule for a multi-context repo.

## Considered Options

- One root `.agents/` for every repo. Rejected: it works against a layout that multi-context repos choose for themselves, and `/doctor` undid that layout on every run.
- Paths read from a ref the repo writes, such as an `issue-tracker.md`. Rejected: it brings back the per-repo setup layer ADR-0001 removed, every skill would have to obey free-form prose, and each repo could drift into its own shape.
- The context folder level first, `.agents/<context>/<kind>/`. Rejected: every skill's root path would change, not just gain a level.

## Consequences

- Steps, worktrees, and `.agents/refs/` take no context subfolder. A new slug must not already exist in another context subfolder of the same kind, so a Step folder keyed on the Spec slug stays unique.
- A skill that cannot tell the context asks; `/doctor`, which never asks, uses `common`.
- `/doctor` moves a multi-context repo's root-level work documents, and an app-first `.agents/<app>/<kind>/` layout, into this shape.
