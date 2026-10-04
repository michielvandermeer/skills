# Architecture reviews end by filing the chosen candidates as Issues

A review holds several suggestions, and the user may want to take more than one forward. After the report, `/improve-codebase-architecture` labels which candidates are Buildable and asks which to take forward. Each picked candidate becomes an Issue in `needs-grilling` to grill later, or a Spec when its Solution is Buildable. Then the skill stops.

Grilling one picked candidate in the same session was rejected so one pick does not consume the session. Writing a Spec for a Solution that still needs grilling was rejected: that is `/triage`'s split. `/implement` would otherwise fill design the card did not settle. Starting `/grill-with-docs` or `/implement` from this skill was rejected: those stay one Issue per typed run.

## Consequences

- ADR-0017's "then grills" is superseded; the rest of 0017 stands.
- `CONTEXT.md`'s Architecture review ends with the picked candidates becoming Issues, not with a grilling session.
