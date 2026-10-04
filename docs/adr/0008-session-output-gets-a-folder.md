# A session that produces several files gets a folder

A session producing several files that belong together gets a folder per session, named for what a flat file would have been named, with the files inside named for their role rather than repeating the slug. Architecture reviews live at `.agents/architecture-reviews/<timestamp>/`. `/implement` Steps sit in a folder per run.

The rule covers the documents the repo keeps outside its Tracker. References are single files, so the rule does not reach them ([ADR-0002](0002-references-and-adrs-layout.md)). Issues follow the Tracker ([ADR-0001](0001-each-repo-describes-its-tracker.md)): on the local Tracker an Issue is one file, and a Map keeps its Decision tickets in a folder beside it.

## Consequences

- Filenames inside a folder are the skill's own vocabulary, not a shared one. `/improve-codebase-architecture` writes `report.*`.
- `/doctor` moves flat architecture reviews into folders as a mechanical directory move. `/refine` writes no Refinement ([ADR-0039](0039-refine-ends-in-a-spec.md)), so `/doctor` turns an old flat or foldered Refinement into an Issue instead.
- A future skill that grows a second output file moves to a folder rather than adding a second flat sibling.
