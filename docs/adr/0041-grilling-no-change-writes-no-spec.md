# A grilling session that settles on no change writes no Spec

A Spec is the input to `/implement`, and work we will not do is not a Spec ([ADR-0032](0032-triage-parks-or-specs.md)). After a confirmed Read-back that nothing will be built, `/grill-with-docs` writes no Spec. It closes the Issue it started from, when there is one, as not planned, and it runs the Retrospective as usual.

Writing a Spec after every confirmed Read-back was rejected so a no does not become an Issue `/implement` could pick up. Recording the no as `wontfix` is rejected in ADR-0032.

## Consequences

- When the Read-back is a change to implement, `/grill-with-docs` runs `/to-spec`, which rewrites the Issue the session started from into the Spec.
- `/to-spec` typed on its own always writes a Spec: the user asked for one.
- `/refine` and `/wayfinder` end in a Spec. `/prototype` ends in a Spec except where [ADR-0016](0016-a-prototype-session-runs-in-a-worktree.md) says it writes none: no verdict yet, a killed idea, or a session that serves a larger effort.
- ADRs that wait for Spec time are not written when there is no Spec.
- In this skills repo, steering that skips `/to-spec` to edit skills in place still skips both when the settled design is no change.
