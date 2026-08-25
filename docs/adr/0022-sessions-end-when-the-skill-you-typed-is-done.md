# Sessions end when the skill you typed is done

We shipped `/retrospective` so named session skills would suggest environment changes after they finished, and so you could type the same command by hand ([ADR-0019](0019-implement-ends-with-a-non-blocking-retrospective.md), [ADR-0020](0020-retrospective-includes-global-agent-files.md), [ADR-0021](0021-named-session-skills-start-a-retrospective.md)). That wrap-up and the typed command are gone. A session ends when the skill that was typed has reached its own done condition.

Copying the wrap-up into each caller was rejected: that is the same work without a home. Keeping only the typed command was rejected: it still ships a skill judged a mistake.

## Consequences

- [ADR-0019](0019-implement-ends-with-a-non-blocking-retrospective.md), [ADR-0020](0020-retrospective-includes-global-agent-files.md), and [ADR-0021](0021-named-session-skills-start-a-retrospective.md) are superseded.
- `/implement` lands as its last step.
- `CONTEXT.md` no longer names this wrap-up.
