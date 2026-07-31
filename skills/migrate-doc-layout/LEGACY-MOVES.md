# Legacy layouts and their mechanical moves

Each layout below predates a decision that changed where documents live. All of them are **mechanical moves**: the destination follows from the source path, so relocate the tree rather than classifying file by file. They still go through the same present → confirm → `git mv` → fix-references flow as classified documents, and a collision at the destination is handled the same way.

## Flat session output that should be a folder

A session producing several files that belong together gets a folder per session ([ADR-0008](../../docs/adr/0008-session-output-gets-a-folder.md)). Refinements and architecture reviews were flat before that, so a repo may hold either shape.

- `.agents/refinements/<slug>.md` → `.agents/refinements/<slug>/complete.md`
- `.agents/refinements/<slug>.html` → `.agents/refinements/<slug>/complete.html`
- `.agents/architecture-reviews/<timestamp>.md` → `.agents/architecture-reviews/<timestamp>/report.md`
- `.agents/architecture-reviews/<timestamp>.html` → `.agents/architecture-reviews/<timestamp>/report.html`

A flat Refinement is a finished one, so it becomes `complete.md`. The session document it was written from no longer exists, and the migration leaves it that way — a fabricated `session.md` would carry a today the code walk never confirmed.

## The `.scratch/` tracker

Repos that adopted these skills before [ADR-0003](../../docs/adr/0003-tracker-under-agents.md) keep their issue tracker under `.scratch/` — `triage` issues at `.scratch/<slug>/issues/<NN>-<slug>.md` and `wayfinder` maps at `.scratch/<effort>/map.md`. The tracker now lives at `.agents/issues/<slug>/`, with the nested `issues/` subfolder flattened away: tickets sit directly in the per-slug directory, maps alongside them.

- `.scratch/<slug>/issues/<NN>-<slug>.md` → `.agents/issues/<slug>/<NN>-<slug>.md` (lift tickets up one level)
- `.scratch/<slug>/map.md` → `.agents/issues/<slug>/map.md`

Remove the emptied `.scratch/` tree once the moves land.
