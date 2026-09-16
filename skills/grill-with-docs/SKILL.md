---
name: grill-with-docs
description: A relentless round-by-round interview to sharpen a plan or design, which also creates docs (ADRs and glossary) as we go.
disable-model-invocation: true
---

Bring the checkout up to date first — pull, with submodules — so the facts you declare and the files you edit are current.

Run a `/grilling` session, using the `/domain-modeling` skill. The glossary entries and ADRs that session produces are yours to write, in this session: `/domain-modeling` times the glossary entries and states an ADR as a declaration, and an ADR that waits for Spec time is written in the same turn as the Spec.

When the request asks for a `/prototype`, or a question turns out to need one, run it after the frontier is empty and before the ending below; its verdict is the last set of declarations, and only a Spec that is written names its folder.

Once the read-back is confirmed, take exactly one ending. The confirmed read-back is the only test — a forecast in an earlier round is not it.

**Change to implement** — the settled design still names a change. Run `/to-spec`, then `/retro`. Leave an originating Issue or Idea in place so `/to-spec` can point it at the Spec. A mixed read-back ("do not build X, do build Y") takes this ending for Y; X is Out of Scope on that Spec.

**Nothing will be built** — the whole settled design is that the product and the skills stay as they are. Write no Spec. Skip `/to-spec`. Delete an Issue or Idea this session started from when one exists; Ideas filed during the session for branches still wanted stay. Glossary entries already written stay; write no ADR that was waiting for Spec time. Say that you wrote no Spec because nothing will be built. Then run `/retro`.
