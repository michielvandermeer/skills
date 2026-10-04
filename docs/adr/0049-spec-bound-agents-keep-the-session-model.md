# Spec-bound agents keep the session model

Spec-bound agents run on the session's model, and only their effort is lowered, to `effort: medium`. Lowering effort cuts spend while the code is still written by the model you chose for the session.

## Considered Options

Pinning `skills:implementer` to a cheaper model was rejected: the code would then be written by a model other than the one chosen for the session.

The request was effort one level below the session's. Claude Code cannot express that. `effort:` frontmatter takes only fixed levels, and the Agent tool takes a `model` argument but no effort argument. One agent file per effort level was rejected. The Driving session would have to pick the file one level below its own effort, and it has no reliable way to know that level. A relative model pin was rejected for the same reason: neither `model:` frontmatter nor the Agent tool accepts a value relative to the session, so the downgrade would be advice rather than a pin. The pin stays at the fixed `medium`, which is one or two levels below the `high` or `xhigh` sessions these skills are run in.

## Consequences

- A session at `low` effort gets `medium` agents and spends more than it chose.
- A host with no cheaper-model tier needs no fallback, because nothing names a model.
- The saving comes from effort alone, not from a cheaper model.
