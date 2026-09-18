---
status: superseded by ADR-0039
---

# A Refine Prototype lives in the Refinement folder

`/refine` used to name `.agents/prototypes/<slug>/` for the playable demo, the same root a Spec uses. A Refinement already has a folder for the files that belong to that session, and a second folder for the demo splits the briefing from the thing the room clicked. A Prototype built during Refine now lives at `.agents/refinements/<slug>/prototype/`. Spec-bound Prototypes stay at `.agents/prototypes/<slug>/`, because a Spec is a single file and has no folder to put them in.

Keeping Refine demos under `.agents/prototypes/` was rejected: two folders for one session is what [ADR-0008](0008-session-output-gets-a-folder.md) already ruled out for documents. Mixing Prototype files with `session.md` and `complete.md` was rejected: a UI Prototype is several files, and the two documents should stay easy to find.

## Consequences

- [ADR-0018](0018-prototypes-live-under-agents-prototypes.md) still holds for Specs. Its line that a Refinement names the same path is superseded here.
- [ADR-0019](0019-refine-determines-scope-via-prototype.md) still holds for how Refine uses a Prototype. The path it names does not.
- `/prototype` serving Refine writes to the path the parent names, and Refine names `.agents/refinements/<slug>/prototype/`.
