# `skills:explorer` loads the host context the built-in Explore skips

`skills:explorer` replaces the host's built-in Explore agent. Explore and Plan are the only sub-agents that skip the CLAUDE.md hierarchy and the parent session's git status. `skills:explorer` pays both on every dispatch. A skill may dispatch more than one: a second pass scoped to shortlisted candidates, so a card can say what that code does; one per subsystem, so each audit lane stays bounded; or a batch of ADRs, so `/doctor` can compare them with the code. The cost is paid per walk, and it inverts in a repo with a very large CLAUDE.md hierarchy.

## Consequences

- Spec-bound agents are pinned in their agent files, the explorer to Haiku at `effort: high` ([ADR-0049](0049-agents-are-pinned-in-their-agent-files.md)). That pin is separate from this cost.
