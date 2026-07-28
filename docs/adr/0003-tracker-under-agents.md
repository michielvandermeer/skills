# Relocate the issue tracker from `.scratch/` to `.agents/issues/`

[ADR-0001](0001-fixed-local-issue-tracker.md) placed the local-markdown issue tracker at `.scratch/<feature-slug>/`, a separate top-level root from the durable document layout ([ADR-0002](0002-agents-doc-layout.md)) that lives under `.agents/`. We consolidated the two: the tracker now lives at `.agents/issues/<slug>/`, so a repo has a single `.agents/` tree for everything agents read and write and no `.scratch/` root at all. Because the root is now literally `issues/`, the redundant nested `issues/` subdirectory was dropped — tickets sit directly in the per-slug directory as `<NN>-<slug>.md`, and each `wayfinder` effort keeps its `map.md` alongside its tickets.

Only the *location* changes; the "fixed local-markdown tracker, no per-repo configuration" decision from ADR-0001 stands.

## Consequences

- `triage` and `wayfinder` scan `.agents/issues/*/*.md`, both skipping each effort's `map.md` — which now shares the directory with its tickets, so a name-based skip replaces the structural separation the old nested `issues/` folder gave for free.
- Triage features and wayfinder efforts continue to share one root, exactly as they did under `.scratch/`.
- A consuming repo with an existing `.scratch/<slug>/` tracker needs to move it to `.agents/issues/<slug>/` and flatten the nested `issues/` subfolder; `/migrate-doc-layout` now handles this. Nothing reads `.scratch/` anymore.
