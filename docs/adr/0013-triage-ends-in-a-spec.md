# Triage ends in a Spec, not an agent brief

`/triage` used to park buildable work as `ready-for-agent` on the issue file with an appended agent brief. Specs already own that handoff for `/implement`, and two contracts for the same job drift. Buildable triage now runs `/to-spec` when the issue is clear, or `/grill-with-docs` (which ends in `/to-spec`) when it is not, then deletes the issue file. Agent briefs and the issue `ready-for-agent` status are gone. Open issues keep only `needs-triage`, `needs-info`, `ready-for-human`, and `wontfix`.

Leaving the issue with a link was rejected so the tracker does not retain a second live card next to the Spec. `/implement` may still try to delete an issue it came from; if triage already removed it, that step is a no-op.

## Consequences

- `/triage` no longer writes agent briefs; `AGENT-BRIEF.md` is removed.
- Specs remain the only agent-ready documents; their `Status: ready-for-agent` is unchanged.
- `ready-for-human` is a short why-person note on the surviving issue, not a brief-shaped contract.
