# Moving documents in a multi-context repo

- A context's folder is the folder holding a `CONTEXT.md` the map links to. An ADR found inside a context's folder moves to that context's own `docs/adr/`. Any other ADR moves to the root `docs/adr/`. Either way, [ADR numbers](SKILL.md#adr-numbers) apply in the folder it lands in.
- Every other document type — Spec, Idea, Issue, and the rest — moves to the one root `.agents/`, because every skill reads only that root.
