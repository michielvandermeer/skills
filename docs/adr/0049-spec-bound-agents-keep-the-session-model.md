# Spec-bound agents keep the session model

[ADR-0007](0007-pinned-subagent-model-tiers.md) pinned `skills:implementer` and `skills:oneshot` to Sonnet and to `effort: medium`. We drop the Sonnet pin. Both agents now run on the session's model, and only their effort is lowered. Lowering effort cuts spend while the code is still written by the model you chose for the session.

## Considered Options

The request was effort one level below the session's. Claude Code cannot express that. `effort:` frontmatter takes only fixed levels, and the Agent tool takes a `model` argument but no effort argument. One agent file per effort level was rejected. The Driving session would have to pick the file one level below its own effort, and it has no reliable way to know that level. That is the advice-only rule ADR-0007 already rejected for models. So the pin stays at the fixed `medium`, which is one or two levels below the `high` or `xhigh` sessions these skills are run in.

## Consequences

- A session at `low` effort gets `medium` agents and spends more than it chose. This replaces ADR-0007's warning that a Haiku session gets Sonnet agents.
- A host with no Sonnet tier needs no fallback, because nothing names a model.
- The saving is smaller than before. It now comes from effort alone, not from a cheaper model.
