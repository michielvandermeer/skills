# Architecture reviews end by writing chosen Ideas and Specs

`/improve-codebase-architecture` used to ask which one candidate to explore, then grill that one in the same session. A review holds several suggestions, and the user may want to take more than one forward — some as Ideas to grill later, some as Specs when the Solution is Buildable. The skill now labels which candidates are Buildable, asks which files to write, writes those Ideas and Specs, and stops.

Grilling in-session was rejected so one pick does not consume the session. Writing a Spec for a Solution that still needs grilling was rejected: that is `/triage`'s split. `/implement` would otherwise fill design the card did not settle. Starting `/grill-with-docs` or `/implement` from this skill was rejected: those stay one document per typed run.

## Consequences

- ADR-0016's "then grills" is superseded; the rest of 0016 stands.
- `CONTEXT.md`'s Architecture review no longer ends "grilled into a Spec with `/grill-with-docs`".
