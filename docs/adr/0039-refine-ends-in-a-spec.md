# Refine ends in a Spec

`/refine` starts from an Issue, grills one person (often a non-developer who knows the product), asks for a Prototype, and writes the Spec in the same session. The Spec becomes that Issue's body. Its first three sections — Problem Statement, Solution, User Stories — serve as the plain-language summary. How it is built is declared from the codebase. There is no Session document, no Complete document, and no `.agents/refinements/` folder to resume from.

Stopping at a Scope briefing so a later `/grill-with-docs` could write the Spec was rejected: the people who could answer how it is built had usually left by then, and the session must finish. A mixed Product/QA/Development room was rejected: one person answers, and the questions stay functional so that person can. Writing a separate summary back to the Issue was rejected: the Spec's first three sections already carry the problem, the solution, and the user stories, and leave out implementation and testing. Asking for a yes before the Spec is written was rejected: the confirmed Read-back already approves it.

## Consequences

- [ADR-0018](0018-prototypes-live-under-agents-prototypes.md) holds for every Prototype, including one `/refine` asked for. `/refine` names `.agents/prototypes/<slug>/`.
- `/grill-with-docs` stays for a developer who wants to grill implementation. `/refine` does not chain to it.
- `/refine` does not write `.agents/refinements/`. `/doctor` turns an existing Refinement into an Issue and moves its demo to `.agents/prototypes/<slug>/`.
- `/refine` updates the glossary as product terms settle. It writes ADRs at Spec time when the three-part test passes, and does not ask the person to judge an ADR.
- The rounds and the Spec run at `/plain-language` ([ADR-0009](0009-plain-language-for-output-not-source.md)).
