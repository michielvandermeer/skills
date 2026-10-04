# Codebase audits are not architecture reviews

`/improve-codebase-architecture` hunts deepening opportunities and writes an Architecture review, which ends by filing Issues ([ADR-0035](0035-architecture-reviews-end-in-issues.md)). `/improve-data-structures` reviews recent work and may implement. A whole-tree, read-only pass for organizing-model simplifications is a third question, so it gets its own skill and document type — a **Codebase audit** at `.agents/codebase-audits/<timestamp>/`. Folding it into architecture reviews would mix the deletion test with the invalid-states test, and folding it into `/improve-data-structures` would either edit the tree mid-audit or give up coverage.

## Consequences

- `/doctor` classifies the Codebase audit shape when it moves documents into the layout.
- Subsystem workers are `skills:explorer` (writes already disallowed). The driving session verifies every finding.
