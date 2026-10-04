# Legacy layouts and their mechanical moves

Each layout below predates a decision that changed where documents live. All of them are **mechanical moves**: the destination follows from the source path, so relocate the tree rather than classifying file by file. A document bound for `.agents/issues/` converts as [Converting to the local Tracker](SKILL.md#converting-to-the-local-tracker) sets out, and only in a repo with no Tracker ref; in a repo with one it stays where it is. Move, then fix references; a collision follows [Moving](SKILL.md#moving).

## A flat refinement

A flat refinement predates [ADR-0008](../../docs/adr/0008-session-output-gets-a-folder.md), which gave a multi-file session its own folder. `/refine` writes nothing under `.agents/refinements/` ([ADR-0039](../../docs/adr/0039-refine-ends-in-a-spec.md)), so a flat refinement converts straight to an Issue, as an Idea, instead of first becoming a folder:

- `.agents/refinements/<slug>.md` → `.agents/issues/<slug>.md`
- `.agents/refinements/<slug>.html` is deleted.

## The `.scratch/` tracker

Repos that adopted these skills before [ADR-0003](../../docs/adr/0003-local-tracker-under-agents.md) keep their tracker under `.scratch/` — `triage` issues and `wayfinder` tickets at `.scratch/<slug>/issues/<NN>-<name>.md`, `wayfinder` maps at `.scratch/<slug>/map.md`, and each feature's brief at `.scratch/<slug>/PRD.md`. Each goes straight onto the local Tracker. The brief converts as a Spec, so the Implemented Issues pass can close it once it's built.

- `.scratch/<slug>/PRD.md` → `.agents/issues/<slug>.md`, as a Spec
- `.scratch/<slug>/map.md` → `.agents/issues/<slug>.md`, as a Map
- `.scratch/<slug>/issues/<NN>-<name>.md` with a `Type:` line → `.agents/issues/<slug>/<NN>-<name>.md`, a Decision ticket of that Map
- `.scratch/<slug>/issues/<NN>-<name>.md` without one → `.agents/issues/<name>.md`, as an Issue

Remove the emptied `.scratch/` tree once the moves land.

## Flat architecture reviews

Architecture reviews were flat before [ADR-0008](../../docs/adr/0008-session-output-gets-a-folder.md):

- `.agents/architecture-reviews/<timestamp>.md` → `.agents/architecture-reviews/<timestamp>/report.md`
- `.agents/architecture-reviews/<timestamp>.html` → `.agents/architecture-reviews/<timestamp>/report.html`

## An app-first layout

A multi-context repo may have built its own layout before [ADR-0056](../../docs/adr/0056-a-multi-context-repo-files-work-documents-per-context.md) put the context subfolder after the kind folder: `.agents/<app>/specs/`, `.agents/<app>/ideas/`, `.agents/<app>/issues/`, `.agents/<app>/prototypes/`. Swap the two levels, mapping each `<app>` to the context subfolder in [domain-modeling/CONTEXT-PATHS.md](../domain-modeling/CONTEXT-PATHS.md) that names the same context:

- `.agents/<app>/<kind>/<rest>` → `.agents/<kind>/<context>/<rest>` for Prototypes, Architecture reviews, and Codebase audits
- `.agents/<app>/specs/<slug>.md` → `.agents/issues/<context>/<slug>.md`, as a Spec
- `.agents/<app>/ideas/<slug>.md` → `.agents/issues/<context>/<slug>.md`, as an Idea
- `.agents/<app>/issues/` → `.agents/issues/<context>/`, each document in it converting by its kind

An `<app>` folder that names no context in the map, such as a `shared/` folder, is not mechanical: classify each document in it by [MULTI-CONTEXT.md](MULTI-CONTEXT.md) into the context that owns its code, or `common`. Remove each emptied `<app>` folder once the moves land.
