# Work-document paths in a multi-context repo

A repo with a root `CONTEXT-MAP.md` files every work document one folder deeper: a context subfolder sits right after the kind folder ([ADR-0056](../../docs/adr/0056-a-multi-context-repo-files-work-documents-per-context.md)). A repo without one keeps the paths each skill names.

| Document | Without a map | With a map |
|---|---|---|
| Spec | `.agents/specs/<slug>.md` | `.agents/specs/<context>/<slug>.md` |
| Idea | `.agents/ideas/<slug>.md` | `.agents/ideas/<context>/<slug>.md` |
| Issue, Decision ticket, Map | `.agents/issues/<effort>/` | `.agents/issues/<context>/<effort>/` |
| Prototype | `.agents/prototypes/<slug>/` | `.agents/prototypes/<context>/<slug>/` |
| Architecture review | `.agents/architecture-reviews/<timestamp>/` | `.agents/architecture-reviews/<context>/<timestamp>/` |
| Codebase audit | `.agents/codebase-audits/<timestamp>/` | `.agents/codebase-audits/<context>/<timestamp>/` |

Steps (`.agents/steps/<spec-slug>/`), worktrees (`.agents/worktrees/`), and refs (`.agents/refs/`) take no context subfolder.

## The context subfolder

`<context>` is the kebab-case of the context's name as `CONTEXT-MAP.md` lists it, with any bracketed text dropped: `TranslationTools` → `translation-tools`, `Libraries (shared)` → `libraries`. Create it on first use.

`common` takes its place when the work belongs to no single context: it changes code in two or more contexts, or code no context owns, such as repo tooling, CI, or deploy.

## Picking the context

A document goes to the context that owns the code its work would change. Infer that from the document. When it is unclear, ask; a skill that runs without asking, such as `/doctor`, uses `common`. An Architecture review or Codebase audit goes to the one context it covered, and to `common` when it covered more.

## Finding a document

A lookup by slug and a scan of a kind folder ("the newest file under `.agents/specs/`") cover every context subfolder of that kind, such as `.agents/specs/*/<slug>.md`. Before writing a new slug, check that no other context subfolder of that kind holds it, so a lookup by slug finds one file. Steps key on the Spec slug alone for this reason.
