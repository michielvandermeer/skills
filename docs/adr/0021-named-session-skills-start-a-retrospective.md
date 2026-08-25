---
status: superseded by ADR-0022
---

# Named session skills start a retrospective when the skill you typed finishes

A **Retrospective** runs when the skill the user typed is one of `/implement`, `/grill-with-docs`, `/triage`, `wayfinder`, `refine`, `/codebase-audit`, or `improve-codebase-architecture`, and that skill has reached its own done condition. A nested caller that reaches `/retrospective` first returns without presenting, so the skill you typed still presents one list. A halt or a wait for the user to continue is not done.

A rule that every user-invoked skill inherits was rejected so listing and library skills stay out; a new skill joins by a later decision. Each named skill presenting was rejected because nested `/grill-with-docs` would hide `/triage`. Presenting at a wait was rejected because it would fire before the work those skills are for, and trip the already-presented stop.
