# Codebase audits are not architecture reviews

`/improve-codebase-architecture` hunts deepening opportunities and writes an Architecture review, which ends by filing Issues ([ADR-0035](0035-architecture-reviews-end-in-issues.md)). A whole-tree, read-only pass for organizing-model simplifications is a second question, so it gets its own skill and document type — a **Codebase audit** at `.agents/codebase-audits/<timestamp>/`. Folding it into architecture reviews would mix the deletion test with the invalid-states test.

## Considered Options

- **A skill that reviews only recent work for a better data structure, and may implement it.** Rejected: `/codebase-audit` asks the same question of the whole tree, and poteto-mode's **principle-model-the-domain** asks it while the code is written. Editing during the review would also change the tree mid-audit.

## Consequences

- `/doctor` classifies the Codebase audit shape when it moves documents into the layout.
- Subsystem workers are `skills:explorer` (writes already disallowed). The driving session verifies every finding.
