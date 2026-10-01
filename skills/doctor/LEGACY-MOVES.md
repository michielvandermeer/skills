# Legacy layouts and their mechanical moves

Each layout below predates a decision that changed where documents live. All of them are **mechanical moves**: the destination follows from the source path, so relocate the tree rather than classifying file by file. Move, then fix references; a collision follows [Moving](SKILL.md#moving).

## A flat refinement

A flat refinement predates [ADR-0008](../../docs/adr/0008-session-output-gets-a-folder.md), which gave a multi-file session its own folder. `/refine` no longer writes `.agents/refinements/` at all ([ADR-0039](../../docs/adr/0039-refine-ends-in-a-spec.md)), so a flat refinement converts straight to an Idea instead of first becoming a folder:

- `.agents/refinements/<slug>.md` → `.agents/ideas/<slug>.md`
- `.agents/refinements/<slug>.html` is deleted.

## The `.scratch/` tracker

Repos that adopted these skills before [ADR-0003](../../docs/adr/0003-tracker-under-agents.md) keep their issue tracker under `.scratch/` — `triage` issues at `.scratch/<slug>/issues/<NN>-<slug>.md`, `wayfinder` maps at `.scratch/<effort>/map.md`, and each feature's brief at `.scratch/<slug>/PRD.md`. The tracker now lives at `.agents/issues/<slug>/`, with the nested `issues/` subfolder flattened away: tickets sit directly in the per-slug directory, maps alongside them. The brief becomes a Spec, since `/doctor`'s Specs and Ideas pass can then delete it once it's built.

- `.scratch/<slug>/issues/<NN>-<slug>.md` → `.agents/issues/<slug>/<NN>-<slug>.md` (lift tickets up one level)
- `.scratch/<slug>/map.md` → `.agents/issues/<slug>/map.md`
- `.scratch/<slug>/PRD.md` → `.agents/specs/<slug>.md`

Remove the emptied `.scratch/` tree once the moves land.

## Flat architecture reviews

Architecture reviews were flat before [ADR-0008](../../docs/adr/0008-session-output-gets-a-folder.md):

- `.agents/architecture-reviews/<timestamp>.md` → `.agents/architecture-reviews/<timestamp>/report.md`
- `.agents/architecture-reviews/<timestamp>.html` → `.agents/architecture-reviews/<timestamp>/report.html`

## An app-first layout

A multi-context repo may have built its own layout before [ADR-0056](../../docs/adr/0056-a-multi-context-repo-files-work-documents-per-context.md) put the context subfolder after the kind folder: `.agents/<app>/specs/`, `.agents/<app>/ideas/`, `.agents/<app>/issues/`, `.agents/<app>/prototypes/`. Swap the two levels, mapping each `<app>` to the context subfolder in [domain-modeling/CONTEXT-PATHS.md](../domain-modeling/CONTEXT-PATHS.md) that names the same context:

- `.agents/<app>/<kind>/<rest>` → `.agents/<kind>/<context>/<rest>`
- `.agents/<app>/issues/<slug>.md`, an Issue with no folder of its own → `.agents/issues/<context>/<slug>/01-<slug>.md`

An `<app>` folder that names no context in the map, such as a `shared/` folder, is not mechanical: classify each document in it by [MULTI-CONTEXT.md](MULTI-CONTEXT.md) into the context that owns its code, or `common`. Remove each emptied `<app>` folder once the moves land.
