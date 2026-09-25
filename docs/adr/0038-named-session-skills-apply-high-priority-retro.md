---
status: partially superseded by ADR-0040
---

# Named session skills start a retrospective that applies high-priority changes

A **Named session skill** starts a **Retrospective** when it finishes. The list is `/implement`, `/implement-oneshot`, `/implement-yolo`, `/grill-with-docs`, `/triage`, `/wayfinder`, `/refine`, `/codebase-audit`, `/improve-codebase-architecture`, and `/doctor`. You can also type `/retro`; that path is the same apply-and-summarise work.

**High-priority** suggestions are applied without asking, in the repo and in global agent files. That includes a judgement-call coding standard and a new check when the pain will recur every turn or every session and this session demonstrated it. A new check that would fail on current master still applies. The rest stay in the chat summary. Repo edits are one commit after the skill's own work — after land for `/implement` and `/implement-oneshot`. Global edits are written in place.

Waiting for confirmation was rejected: restoring the wrap-up only helps if the high-priority changes actually land. Leaving judgement-call standards out of auto-apply was rejected: those are the gains. Auto-apply of repo files only was rejected: global files load on every session. Mixing environment edits into the feature branch was rejected: they are not the Spec.

This restores auto-start, which [ADR-0034](0034-retro-is-a-typed-command.md) and [ADR-0024](0024-sessions-end-when-the-skill-you-typed-is-done.md) had banned, and goes further than [ADR-0021](0021-implement-ends-with-a-non-blocking-retrospective.md), which only presented.

## Consequences

- ADR-0034's auto-run ban is superseded. The typed command stays.
- ADR-0024's wrap-up ban is superseded for these skills. A session whose typed skill is on the list ends when the retrospective summary is in the chat.
- The wrap-up still has one home: `/retro`. Callers only invoke it.
- If a named session skill calls another, only the skill you typed starts a retrospective.
- A halt skips the retrospective. Resume first.
- A new skill stays off the list until a later decision.
