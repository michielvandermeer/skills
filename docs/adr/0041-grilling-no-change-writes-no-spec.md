# A grilling session that settles on no change writes no Spec

`/grill-with-docs` used to run `/to-spec` after every confirmed Read-back. A session that settled on not building anything therefore left a Spec. A Spec is the input to `/implement`; work we will not do is not kept as a document ([ADR-0032](0032-triage-parks-or-specs.md)). After a confirmed Read-back that nothing will be built, the session writes no Spec, deletes an Issue or Idea it started from, and still runs the Retrospective.

Always writing a Spec was rejected so a no does not become a file `/implement` could pick up. Recording the no as `wontfix` was already rejected in ADR-0032.

## Consequences

- `/grill-with-docs` still runs `/to-spec` when the Read-back is a change to implement.
- `/to-spec` typed on its own is unchanged: the user asked for a Spec.
- `/refine`, `/wayfinder`, and `/prototype` still end in a Spec. Those sessions exist to produce one.
- ADRs that wait for Spec time are not written when there is no Spec.
