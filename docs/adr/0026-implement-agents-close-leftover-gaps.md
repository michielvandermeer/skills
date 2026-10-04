# `/implement` sub-agents close leftover gaps themselves

Every `/implement` sub-agent closes leftover gaps from the documents it was handed, the code, and existing patterns, and keeps going. The user did not write the Spec or the Step, so a question about something those left unnamed has no useful answer. A choice that contradicts the Spec or changes a later Step is a Deviation on the `deviations:` line of the agent's report, which the Driving session relays with the Step's progress line.

Stopping the run so the user could decide was rejected: they still would not have the answer. Asking the Driving session was rejected: there is no channel that would keep the question off the user's screen. Raising the Step agent's effort to close a gap was rejected: closing a gap is still work inside a Step whose scope was already settled.

## Consequences

- A result that is a question is a failed step, retried once. A second failure stops the run without quoting the question.
- The Planner fills only silence in the Spec. When a Step file and the Spec disagree, the Spec wins.
- Step agents stay on the session's model at `effort: medium` ([ADR-0049](0049-spec-bound-agents-keep-the-session-model.md)).
