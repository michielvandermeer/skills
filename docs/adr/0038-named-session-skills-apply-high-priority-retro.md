# Named session skills start a retrospective that applies high-priority changes

A **Named session skill** starts a **Retrospective** when it finishes. The list is `/implement`, `/implement-oneshot`, `/implement-yolo`, `/grill-with-docs`, `/triage`, `/wayfinder`, `/refine`, `/codebase-audit`, `/improve-codebase-architecture`, `/brainstorm`, and `/doctor`. You can also type `/retro`; that path is the same apply-and-summarise work. The command is `/retro`, not `/retrospective`, so the name matches the word people already type.

**High-priority** suggestions are applied without asking. That includes a judgement-call coding standard and a new check when the pain will recur every turn or every session and this session demonstrated it. A new check that would fail on the current branch still applies. The rest stay in the chat summary. Where the edits land is [ADR-0040](0040-retro-writes-only-owned-files.md). What the retrospective looks at, including global agent files, is [ADR-0022](0022-retrospective-includes-global-agent-files.md). Repo edits are one commit after the skill's own work — after land for `/implement` and `/implement-oneshot`.

Waiting for confirmation was rejected: the wrap-up only helps if the high-priority changes actually land. Leaving judgement-call standards out of auto-apply was rejected: those are the gains. Mixing environment edits into the feature branch was rejected: they are not the Spec. Keeping the command name `/retrospective` was rejected so it matches the word people type.

## Consequences

- A session whose typed skill is on the list ends when the retrospective summary is in the chat.
- The wrap-up has one home: `/retro`. Callers only invoke it.
- If a named session skill calls another, only the skill you typed starts a retrospective.
- A halt, or a wait for the user to continue, skips the retrospective. Resume first.
- A new skill stays off the list until a later decision.
- `/brainstorm` is on the list because, like `/improve-codebase-architecture`, it is a typed session that ends by filing Issues in `needs-grilling`.
