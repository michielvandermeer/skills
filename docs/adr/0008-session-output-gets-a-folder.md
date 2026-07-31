# A session that produces several files gets a folder

[ADR-0002](0002-agents-doc-layout.md) fixed a flat file per document under `.agents/`, which works while a skill produces one document and breaks once it produces several: `.agents/refinements/` held a `<slug>.md` and a `<slug>.html` per change, and `/refine` gaining a session document alongside its signed-off one would have made three. The rule is now that a session producing several files that belong together gets a folder per session, named for what a flat file would have been named — `.agents/refinements/<slug>/`, `.agents/architecture-reviews/<timestamp>/` — with the files inside named for their role rather than repeating the slug.

This is mostly a convention the repo already followed. `/triage` issues, `/wayfinder` maps, and `/implement` Steps all sit in per-effort folders; Specs, Ideas, and references are single files, so the rule does not reach them. Refinements and architecture reviews were the only two places out of step, and both moved.

## Consequences

- ADR-0002's layout table is superseded for these two document types and stands for the rest.
- Filenames inside a folder are the skill's own vocabulary, not a shared one: `/refine` writes `session.*` and `complete.*` because it has an incomplete state worth naming, and `/improve-codebase-architecture` writes `report.*` because it does not. Making the two match would imply `/improve-codebase-architecture` has a session document it does not have.
- Repos holding the flat shape need `/migrate-doc-layout`, which handles both as mechanical directory moves.
- A future skill that grows a second output file moves to a folder rather than adding a second flat sibling.
