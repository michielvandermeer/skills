---
status: partially superseded by ADR-0038
---

# `/retro` is a typed command; sessions still end when their own work is done

[ADR-0024](0024-sessions-end-when-the-skill-you-typed-is-done.md) removed both the wrap-up that named session skills ran and the typed `/retrospective` command. The wrap-up stays gone: a session ends when the skill that was typed has reached its own done condition, and no skill starts a retrospective on the user's behalf. The typed command returns as `/retro`. You ask for environment suggestions; they are not a closing step.

Keeping the old name was rejected so the command matches the leading word people already type. Wiring `/retro` back into `/implement` or the other named session skills was rejected: that is the wrap-up ADR-0024 already judged a mistake.

## Consequences

- The typed command stays. Auto-run and auto-apply are restored by [ADR-0038](0038-named-session-skills-apply-high-priority-retro.md).
- `/retro` looks at repo and global always-loaded agent files, as [ADR-0022](0022-retrospective-includes-global-agent-files.md) did.
