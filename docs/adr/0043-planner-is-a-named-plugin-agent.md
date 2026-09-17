# The Planner is a named plugin agent

`/implement` said "dispatch a planner" and did not name a type. Hosts ship a built-in planning agent (`plan` / `Plan`) that only reads and whose job is a design document. The Driving session picks that type because the names match, so the Planner cannot write Step files and the run halts. We dispatch `skills:planner` (`agents/planner.md`) instead, at the session's own model and effort, the same shape as `skills:explorer` replacing the host Explore type.

Pinning `general-purpose` alone was rejected: the host type is still the attractive match for the word "planner", and a generic agent has no identity that writes Step files and returns only the index. Keeping the host type and having the Driving session write the files from its output was already rejected — the Planner owns those files ([ADR-0030](0030-planner-commits-the-step-files.md)). Folding the slicing rules into the agent file was rejected: the Driving session already hands that path, and copying it would duplicate the rules.

## Consequences

- The Planner is not spec-bound in the [ADR-0007](0007-pinned-subagent-model-tiers.md) cost sense: no `model:` or `effort:` pin. README's "every shipped agent is medium effort" no longer covers it.
- A host without the plugin agent falls back to `general-purpose`, never to `plan` / `Plan`.
- The host planning type still exists for other uses. `/implement` never uses it.
