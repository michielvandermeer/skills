# `/implement` sub-agents close leftover gaps themselves

Every `/implement` sub-agent closes leftover gaps from the documents it was handed, the code, and existing patterns, and keeps going. A question about something the Spec left unnamed has no useful answer from the user, who did not write it with that question in mind. A choice that contradicts the Spec is a Deviation on the `deviations:` line of the agent's report, which the Driving session relays with the Iteration's progress line.

Stopping the run so the user could decide was rejected: they still would not have the answer. Asking the Driving session was rejected: there is no channel that would keep the question off the user's screen. Raising the Implementer's effort to close a gap was rejected: closing a gap is still work inside a Spec whose scope was already settled.

## Consequences

- A result that is a question is a failed dispatch, retried once. A second failure stops the run without quoting the question.
- Where a Review finding and the Spec disagree, the Spec wins, and the Implementer declines the finding.
- The Planner writes its reading of what the Spec left silent into the Step that needs it, so every Implementer after it shares one reading.
- The Planner, the Implementer, and the Verifier are pinned to Sonnet at `effort: high` ([ADR-0049](0049-agents-are-pinned-in-their-agent-files.md)).
