# Agents are pinned in their agent files

Each skill you type and each plugin agent sets `model:` and `effort:` in its own header, so a run starts at the setting its work needs and not at your session's most expensive one. Three parallel implement runs on Opus at xhigh burned about 16% of a weekly limit in five hours. Nothing is pinned above `high`.

- **Skills you type**, the ones marked `disable-model-invocation: true`, plus `/implement`, which a `/goal` can also start ([ADR-0067](0067-implement-is-model-invoked-so-a-goal-can-start-it.md)): Opus at high for the interview and design skills (`/grill-with-docs`, `/brainstorm`, `/wayfinder`), Sonnet at high for the rest.
- **Agents** are pinned as follows:

  | Agent | Model | Effort |
  |---|---|---|
  | Planner, Implementer, Verifier | Sonnet | high |
  | Climber, Validator, Researcher | Sonnet | medium |
  | Explorer | Haiku | high |
  | Reviewer | Opus | high |

- **Everything else** runs on the setting of the skill that starts it: a Hillclimb's Fixers, the `/brainstorm` fan-out, and the `/simulate-first-users` First users.

A skill's pin lasts for the rest of the turn, so a model-invoked skill that other skills load carries none: it would swap its caller's model. A user-invoked skill that other skills need is followed by path ([ADR-0074](0074-skills-that-other-skills-start-are-user-invoked.md)), which skips its pin, so it is pinned for when you type it.

The Reviewer is Opus because review is the one stage where a stronger model than the author's pays for itself.

A repo may override an agent's pin in its **Models ref**, `.agents/refs/models.md`, which `/setup models` writes. Each row names an agent's model and effort, and a pointer line in the repo's `CLAUDE.md` or `AGENTS.md` has the session pass them as `model` and `effort` on every dispatch of that agent. A plain `/setup` writes the file with every agent at its pin when it is missing, so the repo's choices sit in one place to edit.

## Considered Options

A Models ref that also sets the skills' pins was rejected: the host chooses a skill's model before the skill can read a repo file. The Models ref covers the agents only.

Keeping the Models ref in the user's global Claude Code config, as pstack does, was rejected. The choice belongs to the repo and travels with it in git.

Passing `model` and `effort` on each Agent call from the skill text was rejected as the main way to pin. The `effort` argument needs Claude Code 2.1.292 or later, and Grok's `spawn_subagent` has none. An agent header works on both, which is why the reviewers became an agent. The call arguments remain the way a caller, or the Models ref, overrides a pin.

Retrying a failed Implementer at higher effort was rejected. The retry fires on a `blocked` report, a malformed report, or a question in place of a result, and more thinking rarely fixes those.

## Consequences

- A repo changes an agent's pin in its Models ref. It cannot change a skill's pin; it forks the plugin, or sets its session model by hand.
- A row copied from a default does not follow a later change to that agent's pin. `/setup models` marks each row that differs from the current pin.
- On a host whose dispatch takes no effort, a row sets the model only.
- `CLAUDE_CODE_EFFORT_LEVEL`, when set, beats an effort pin.
- A model name in a header is a Claude alias. When a host rejects one, that model pin is dropped and the effort pins stay.
- The Claude Code docs do not say that a skill's pin reaches the unpinned agents it starts, or that it lasts through a long run. Where it does not carry to the Fixers, the skill text passes `model` and `effort` on those calls.
