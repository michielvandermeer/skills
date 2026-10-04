# The local Tracker lives under `.agents/issues/`

A repo on the local Markdown Tracker keeps its Issues under `.agents/issues/` ([ADR-0001](0001-each-repo-describes-its-tracker.md)), in the same `.agents/` tree as every other document agents read and write ([ADR-0002](0002-agents-doc-layout.md)). A repo has one tree for agent documents. The local Tracker template, [setup/LOCAL.md](../../skills/setup/LOCAL.md), sets out the files inside it.

## Considered Options

- A separate top-level `.scratch/` root for the tracker, which the skills these were derived from use. Rejected: agent documents would sit in two roots for no gain.

## Consequences

- In a repo with no Tracker ref, `/doctor` moves an existing `.scratch/<slug>/` tracker into `.agents/issues/` and turns each feature's `PRD.md` into an Issue carrying a Spec. Nothing reads `.scratch/`.
