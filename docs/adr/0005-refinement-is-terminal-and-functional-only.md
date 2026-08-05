# Refinement is terminal and functional-only

`grill-with-docs` chains into `/to-spec`, so a session ends with an implementable Spec. `/refine` deliberately does not: it runs with Product, QA, and Development in the room, and the people who would answer the technical rounds have usually left by the time the functional picture is agreed. A Refinement therefore stops at intent, use cases, and the delta against current behaviour, carries no `Status:` line, and is consumed by nothing automatically — the user chooses whether to follow it with `/grill-with-docs` or `/to-spec`, days later if that is when the technical session happens.

Constraints and implications the Code walk read out of the code still travel with the Complete document, but they land in `Notes` rather than a dedicated technical section — "this area has no audit trail today, so a change here is invisible to support." That describes the ground a developer will stand on. It never carries a decision about what to build on it. The test is whether a room without Development present could have signed the note off: a constraint of today passes, a chosen approach does not. The full read-from-code walkthrough stays in the Session document only, for resume ([ADR-0010](0010-refine-user-facing-surfaces.md)).

## Consequences

- A Refinement is not a Spec with empty sections. `/implement` never sees one, and `validate-spec`'s template rules do not apply to it.
- The functional half of a change can be settled and shipped to Jira without any implementation decision existing yet.
- The Complete document has six fixed sections, not seven — no `Technical details` heading.
