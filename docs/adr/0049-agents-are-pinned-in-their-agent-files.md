# Agents are pinned in their agent files, and implement delegates follow the operator's sheet

Each skill you type and each plugin agent sets `model:` and `effort:` in its own header, so a run starts at the setting its work needs and not at your session's most expensive one. Three parallel implement runs on Opus at xhigh burned about 16% of a weekly limit in five hours. Nothing is pinned above `high`.

- **Skills you type**, the ones marked `disable-model-invocation: true` except `/review-spec`, plus the two implement commands, which a `/goal` can also start ([ADR-0067](0067-the-implement-commands-are-model-invoked-so-a-goal-can-start-them.md)): Opus at high for the interview and design skills (`/grill-with-docs`, `/brainstorm`, `/improve-codebase-architecture`, `/wayfinder`) and for `/implement` and `/implement-yolo`, whose Driving session owns the design and verification judgement of a poteto-mode run ([ADR-0069](0069-an-implement-run-is-a-poteto-mode-playbook.md)); Sonnet at high for the rest.
- **Agents** are pinned as follows:

  | Agent | Model | Effort |
  |---|---|---|
  | Validator, Researcher | Sonnet | medium |
  | Explorer | Haiku | high |
  | Both `/thermo-nuclear-review` passes | Opus | high |

- **Implement delegates** have no agent file of their own. Every role an implement run dispatches, the `skills:poteto-agent` builders and fixers, the Verifier, the `how` explorers, the `architect` runners, and the `interrogate` reviewers, takes its model from the role line in the operator's `~/.claude/pstack-models.md`, as the `poteto-mode` skill's Subagents and Models sections say, so cost has one control surface the operator already edits with `/setup models`. A sheet with no line keeps the role's default.
- **Everything else** runs on the setting of the skill that starts it: the `/brainstorm` and `/codebase-design` fan-outs.

A skill's pin lasts for the rest of the turn. A skill that another skill loads would swap its caller's model, so only skills that no other skill loads are pinned. `/review-spec` stays on the session because [ADR-0036](0036-review-spec-uses-the-session-model.md) says you choose its model by opening the session.

The thermo-nuclear passes are Opus because review is the one stage where a stronger model than the author's pays for itself.

## Considered Options

A per-repo `.agents/refs/models.md` was rejected. A skill cannot read a repo file before the host has chosen its model, so the file could set only the sub-agents and never the skills that burn the most.

Passing `model` and `effort` on each Agent call from the skill text was rejected as the main way to pin a repo agent. An agent header is the one place a pin cannot be forgotten. The call arguments remain the way a caller overrides a pin, and the way poteto-mode's roles pass the sheet's model.

Pinning the implement delegates in agent files of their own, as the per-slice agents of the old run were, was rejected. The operator's sheet already decides every poteto-mode role, and a second place for the same decision is the drift ADR-0069 removes.

Keeping the implement Driving session on Sonnet was rejected. It now reads the design, the Verifier's verdicts, and the review, and decides every operator call the grant covers; that is the judgement this ADR already assigns to Opus.

## Consequences

- A repo cannot change a pin. It forks the plugin, or sets its session model by hand. A repo cannot change a sheet line either; the sheet is the operator's.
- `CLAUDE_CODE_EFFORT_LEVEL`, when set, beats an effort pin.
- A model name in a header is a Claude alias. When a host rejects one, that model pin is dropped and the effort pins stay.
- The Claude Code docs do not say that a skill's pin reaches the unpinned agents it starts, or that it lasts through a long run. Where it does not carry, the skill text passes `model` and `effort` on those calls.
