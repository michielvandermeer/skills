# A session that produces several files gets a folder

A session producing several files that belong together gets a folder per session, named for what a flat file would have been named, with the files inside named for their role rather than repeating the slug. Codebase audits live at `.agents/codebase-audits/<timestamp>/`. An implement run's files sit in a run directory per run.

The rule covers the documents the repo keeps outside its Tracker. References are single files, so the rule does not reach them ([ADR-0002](0002-references-and-adrs-layout.md)). Issues follow the Tracker ([ADR-0001](0001-each-repo-describes-its-tracker.md)): on the local Tracker an Issue is one file, and a Map keeps its Decision tickets in a folder beside it.

## Consequences

- Filenames inside a folder are the skill's own vocabulary, not a shared one. `/codebase-audit` writes `report.md`.
- No skill writes a Refinement any more, so `/doctor` turns an old flat or foldered Refinement into an Issue.
- A future skill that grows a second output file moves to a folder rather than adding a second flat sibling.
