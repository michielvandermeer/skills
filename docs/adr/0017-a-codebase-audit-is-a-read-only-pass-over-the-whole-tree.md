# A codebase audit is a read-only pass over the whole tree

`/codebase-audit` looks for simplifications of the organizing model in every subsystem, and writes a **Codebase audit** at `.agents/codebase-audits/<timestamp>/`. It changes no other file, so the tree stays still while it is audited, and the person reading the report picks what to build.

## Considered Options

- **A skill that reviews only recent work for a better data structure, and may implement it.** Rejected: `/codebase-audit` asks the same question of the whole tree, and poteto-mode's [model-the-domain](../../skills/poteto-mode/principles/model-the-domain.md) asks it while the code is written. Editing during the review would also change the tree mid-audit.

## Consequences

- `/doctor` classifies the Codebase audit shape when it moves documents into the layout.
- Subsystem workers are `skills:explorer` (writes already disallowed). The driving session verifies every finding.
