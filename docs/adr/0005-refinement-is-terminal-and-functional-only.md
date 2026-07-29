# Refinement is terminal and functional-only

`grill-with-docs` chains into `/to-spec`, so a session ends with an implementable Spec. `/refine` deliberately does not: it runs with Product, QA, and Development in the room, and the people who would answer the technical rounds have usually left by the time the functional picture is agreed. A Refinement therefore stops at intent, use cases, and the delta against current behaviour, carries no `Status:` line, and is consumed by nothing automatically — the user chooses whether to follow it with `/grill-with-docs` or `/to-spec`, days later if that is when the technical session happens.

## Consequences

- A Refinement is not a Spec with empty sections. `/implement` never sees one, and `validate-spec`'s template rules do not apply to it.
- The functional half of a change can be settled and shipped to Jira without any implementation decision existing yet.
