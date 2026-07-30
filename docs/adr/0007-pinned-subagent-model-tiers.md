# Pinned sub-agent model tiers

The skills in this plugin dispatch sub-agents that all inherited the session's model and effort, so a `/implement` run spent Opus-tier tokens on work whose scope was already fully decided. We now pin the cost knobs on **absolute** tiers in `agents/` frontmatter — `skills:implementer` is fixed at Sonnet, and every spec-bound dispatch runs at `effort: medium` — rather than expressing them relative to the session's own model.

## Considered Options

A relative policy was the first choice: never dispatch above whatever model the session is already on, so a skill can only ever ratchet spend *down*. It was rejected because neither `model:` frontmatter nor the `Agent` tool's `model` argument accepts a relative value — there is no "one tier below the session". Expressing it would have meant prose instructing the driving session to compute the downgrade itself at dispatch time, which is advisory rather than enforced. We chose determinism over that.

Effort pins avoid the problem entirely, because `medium` is below Claude Code's `xhigh` default under every session configuration. That is why `medium` and nothing lower or higher appears in these agents, and why the judgement-carrying roles have no `effort` field at all rather than an explicit `high`.

## Consequences

**These skills assume a session on Opus or above.** A `model: sonnet` pin is an *upgrade* for anyone who deliberately started a Haiku session, and they get it silently — the skill spends more than they chose. That is the accepted cost of the absolute pin.

Replacing the built-in `Explore` with `skills:explorer` also gives up a property of the built-in: `Explore` and `Plan` are the only sub-agents that skip the CLAUDE.md hierarchy and the parent session's git status. `skills:explorer` pays both on every dispatch. The trade holds because each skill dispatches one explorer per run, so that cost is fixed while the effort reduction applies across a whole codebase walk — but it inverts in a repo with a very large CLAUDE.md hierarchy.

The saving is bounded and modest: Sonnet is 40% cheaper per token than Opus, and the pin covers implementation steps only. One retried Sonnet step costs more than the Opus run it replaced.
