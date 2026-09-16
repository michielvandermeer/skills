# Refine ends in a Spec

`/refine` used to stop at a Scope briefing in `.agents/refinements/` so a later `/grill-with-docs` could write the Spec. The people who could answer how it is built had usually left ([ADR-0019](0019-refine-determines-scope-via-prototype.md)). It now starts from an Idea or a Jira ticket, grills one person (often a non-developer who knows the product), asks for a Prototype, writes the Spec in the same session, and overwrites that Idea or ticket with a plain-language summary of the Spec. How it is built is declared from the codebase. There is no Session document, no Complete document, and no `.agents/refinements/` folder to resume from.

Keeping a terminal briefing was rejected: the session must finish, and the durable records are the Spec and the updated Idea or ticket. A mixed Product/QA/Development room was rejected: one person answers, and the questions stay functional so that person can. Writing the summary from the read-back was rejected: the summary is of the Spec, after `/to-spec`, and it carries the problem, the solution, and the user stories — not implementation or testing.

## Consequences

- [ADR-0019](0019-refine-determines-scope-via-prototype.md), [ADR-0025](0025-refine-prototype-lives-in-the-refinement-folder.md), and [ADR-0012](0012-refine-user-facing-surfaces.md) are superseded.
- [ADR-0018](0018-prototypes-live-under-agents-prototypes.md) holds for every Prototype, including one `/refine` asked for. `/refine` names `.agents/prototypes/<slug>/`.
- `/grill-with-docs` stays for a developer who wants to grill implementation. `/refine` does not chain to it.
- `migrate-doc-layout` still recognises `.agents/refinements/` so existing repos can move. `/refine` does not write that shape.
- `/refine` updates the glossary as product terms settle. It writes ADRs at Spec time when the three-part test passes, and does not ask the person to judge an ADR.
- The refine-specific consequences in [ADR-0009](0009-plain-language-for-output-not-source.md) (the room bar, `complete.md`, the Session document) no longer apply. Rounds and the write-back still run at `/plain-language`.
