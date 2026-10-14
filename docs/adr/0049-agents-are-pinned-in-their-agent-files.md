# Agents are pinned in their agent files

Each skill you type and each plugin agent sets `model:` and `effort:` in its own header, so a run starts at the setting its work needs and not at your session's most expensive one. Three parallel implement runs on Opus at xhigh burned about 16% of a weekly limit in five hours. Nothing is pinned above `high`.

- **Skills you type**, the ones marked `disable-model-invocation: true` except `/review-spec`, plus the three implement commands, which a `/goal` can also start ([ADR-0067](0067-the-implement-commands-are-model-invoked-so-a-goal-can-start-them.md)): Opus at high for the interview and design skills (`/grill-with-docs`, `/grill-me`, `/brainstorm`, `/improve-codebase-architecture`, `/refine`, `/wayfinder`), Sonnet at high for the rest.
- **Agents** are pinned as follows:

  | Agent | Model | Effort |
  |---|---|---|
  | Step agent, Checker, Planner | Sonnet | high |
  | Prover, Climber, Validator, Researcher | Sonnet | medium |
  | Explorer | Haiku | high |
  | Reviewer | Opus | high |

- **Everything else** runs on the setting of the skill that starts it: the Fixers, the `/improve-data-structures` pass, and the `/brainstorm` and `/codebase-design` fan-outs.

A skill's pin lasts for the rest of the turn. A skill that another skill loads would swap its caller's model, so only skills that no other skill loads are pinned. `/review-spec` stays on the session because [ADR-0036](0036-review-spec-uses-the-session-model.md) says you choose its model by opening the session.

The Reviewer is Opus because review is the one stage where a stronger model than the author's pays for itself. The Checker's review of a single Step is the exception. It asks `/code-review` to run its reviewers on Sonnet at high, because the run's final review covers the whole diff on Opus.

## Considered Options

A per-repo `.agents/refs/models.md` was rejected. A skill cannot read a repo file before the host has chosen its model, so the file could set only the sub-agents and never the skills that burn the most.

Passing `model` and `effort` on each Agent call from the skill text was rejected as the main way to pin. The `effort` argument needs Claude Code 2.1.292 or later, and Grok's `spawn_subagent` has none. An agent header works on both, which is why the reviewers became an agent. The call arguments remain the way a caller overrides a pin.

Retrying a failed Step at higher effort was rejected. The retry fires on a `blocked` report, a malformed report, or a question in place of a result, and more thinking rarely fixes those.

## Consequences

- A repo cannot change a pin. It forks the plugin, or sets its session model by hand.
- `CLAUDE_CODE_EFFORT_LEVEL`, when set, beats an effort pin.
- A model name in a header is a Claude alias. When a host rejects one, that model pin is dropped and the effort pins stay.
- The Claude Code docs do not say that a skill's pin reaches the unpinned agents it starts, or that it lasts through a long run. Where it does not carry to the Fixers, the skill text passes `model` and `effort` on those calls.
