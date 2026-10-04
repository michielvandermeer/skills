# Moving documents in a multi-context repo

- A context's folder is the folder holding a `CONTEXT.md` the map links to. An ADR found inside a context's folder moves to that context's own `docs/adr/`. Any other ADR moves to the root `docs/adr/`. Either way, [ADR numbers](SKILL.md#adr-numbers) apply in the folder it lands in.
- Coding standards stay at the root `.agents/refs/`.
- Every other document type — an Issue on the local Tracker, a Prototype, and the rest — moves under its kind folder into a context subfolder, by [domain-modeling/CONTEXT-PATHS.md](../domain-modeling/CONTEXT-PATHS.md). A document already in a context subfolder keeps that context; one at the root of its kind folder moves to the context that file's Picking the context rule names.
