# Work-document paths in a multi-context repo

A repo with a root `CONTEXT-MAP.md` files every work document one folder deeper: a context subfolder sits right after the kind folder ([ADR-0056](../../docs/adr/0056-a-multi-context-repo-files-work-documents-per-context.md)). A repo without one keeps the paths each skill names.

| Document | Without a map | With a map |
|---|---|---|
| Prototype | `.agents/prototypes/<slug>/` | `.agents/prototypes/<context>/<slug>/` |
| Hillclimb folder | `.agents/hillclimbs/<slug>/` | `.agents/hillclimbs/<context>/<slug>/` |

Issues follow the repo's Tracker ref, or [setup/LOCAL.md](../setup/LOCAL.md) when it has none; the local Tracker picks its context subfolder by the rules below. Run folders (`.agents/runs/<run-slug>/`), worktrees (`.agents/worktrees/`), and refs (`.agents/refs/`) take no context subfolder.

## The context subfolder

`<context>` is the kebab-case of the context's name as `CONTEXT-MAP.md` lists it, with any bracketed text dropped: `TranslationTools` → `translation-tools`, `Libraries (shared)` → `libraries`. Create it on first use.

`common` takes its place when the work belongs to no single context: it changes code in two or more contexts, or code no context owns, such as repo tooling, CI, or deploy.

## Picking the context

A document goes to the context that owns the code its work would change. Infer that from the document. When it is unclear, ask; a skill that runs without asking, such as `/doctor`, uses `common`. A Hillclimb folder goes to the context whose code produces the number.

## Finding a document

A lookup by slug and a scan of a kind folder cover every context subfolder of that kind, such as `.agents/prototypes/*/<slug>/`. Before writing a new slug, check that no other context subfolder of that kind holds it, so a lookup by slug finds one document. A run folder keys on its slug alone for this reason.
