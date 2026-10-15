# Implement delegates close leftover gaps themselves

Every delegate of an implement run, the `skills:poteto-agent` that builds a unit, the Verifier, and a fixer, closes leftover gaps from the Spec, the design, the code, and existing patterns, and keeps going. The user did not write the Spec, so a question about something it left unnamed has no useful answer, and the run lands unattended. A choice that contradicts the Spec is a Deviation: it goes in `design.md`'s Implementation reconciliation section and the trail, and the report names it.

Stopping the run so the user could decide was rejected: they still would not have the answer. Asking the Driving session was rejected: there is no channel that would keep the question off the user's screen, and the Driving session decides reversible calls itself under its full-autonomy grant, so a delegate's question would only route the same decision through a second context.

## Consequences

- A result that is a question is a failed delegate. A fresh delegate with consolidated scope takes the work; a second failure of the same kind triggers the premise census before a third, and a third halts the run.
- The Driving session's own calls follow the same rule: a call the grant covers is decided, logged in the trail, and reported; a call only the operator can make gets a default, a full explanation in the report, and what the operator could say instead.
