---
name: grill-with-docs
description: A relentless round-by-round interview to sharpen a plan or design, which also creates docs (ADRs and glossary) as we go.
disable-model-invocation: true
---

Bring the checkout up to date first — pull, with submodules — so the facts you declare and the files you edit are current.

Run a `/grilling` session, using the `/domain-modeling` skill. The glossary entries and ADRs that session produces are yours to write, in this session: `/domain-modeling` times the glossary entries and states an ADR as a declaration, and an ADR that waits for Spec time is written in the same turn as the Spec.

When the request asks for a `/prototype`, or a question turns out to need one, run it after the Frontier is empty and before the ending below; its verdict is the last set of declarations, and only a Spec that is written names its folder.

Issues live in the repo's **Tracker**: carry out each operation on one — file, read, list, rewrite, set status, comment, link, close — as `.agents/refs/tracker.md` says, or as [setup/LOCAL.md](../setup/LOCAL.md) says when the repo has no ref.

Once the Read-back is confirmed, take exactly one ending. The confirmed Read-back is the only test — a forecast in an earlier Round is not confirmation.

**Change to implement** — the settled design still names a change. Run `/to-spec`, then `/learn-habits`, then `/retro`. `/to-spec` rewrites the Issue this session started from into the Spec. A mixed Read-back ("do not build X, do build Y") takes this ending for Y; X is Out of Scope on that Spec.

**Work we will not do** — the whole settled design names no change. Skip `/to-spec`. Close the Issue this session started from as not planned, when there is one; Issues filed during the session for branches still wanted stay open. Glossary entries already written stay; write no ADR that was waiting for Spec time. Say that you wrote no Spec because nothing will be built. Then run `/learn-habits`, then `/retro`.
