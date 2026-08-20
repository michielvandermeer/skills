# Refine determines Scope and briefs grill-with-docs

`/refine` used to grill a full functional picture — intent, use cases, and the delta — and leave the room to pick `/grill-with-docs` or `/to-spec` later. The room finds textual grilling hard and a visual easy, so the session now does minimal grilling to a first Prototype, then steers from the demo until Scope is named: what is part of this project and what is not. The Complete document is a briefing a developer uses to start `/grill-with-docs`. It stays terminal and silent on implementation.

Use cases and work items were rejected: those are what `/grill-with-docs` settles, and putting them in the briefing invites the room to design the solution. Mid-session HTML was rejected: the Prototype is the picture during the session. Chaining into `/to-spec` from refine was rejected: the people who would answer the technical rounds have usually left.

## Consequences

- [ADR-0005](0005-refinement-is-terminal-and-functional-only.md) is superseded. Terminal and silent-on-implementation stand here.
- The Complete document's six sections are Intent, How it works today, In scope, Out of scope, Prototype, Open Questions.
- `/prototype` invoked from refine writes no Spec. The Refinement names `.agents/prototypes/<slug>/`.
- A developer, not the refine session, starts `/grill-with-docs`.
