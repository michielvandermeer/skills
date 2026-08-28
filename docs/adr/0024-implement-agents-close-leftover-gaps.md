# `/implement` sub-agents close leftover gaps themselves

`/implement` sub-agents used to ask the user when the Spec or a Step left something unnamed. The user did not write those documents, so the questions had no useful answer. Every `/implement` sub-agent now closes leftover gaps from the documents it was handed, the code, and existing patterns, and keeps going. A choice that contradicts the Spec or changes a later Step is a Deviation on the progress line.

Stopping the run so the user could decide was rejected: they still would not have the answer. Asking the Driving session was rejected: there is no channel that would keep the question off the user's screen. Promoting the Step agent to the expensive tier was rejected: closing a gap is still work inside a Step whose scope was already settled.

## Consequences

- A result that is a question is a failed step, retried once. A second failure stops the run without quoting the question.
- The Planner fills only silence in the Spec. When a Step file and the Spec disagree, the Spec wins.
- Step agents stay on the cheaper tier.
