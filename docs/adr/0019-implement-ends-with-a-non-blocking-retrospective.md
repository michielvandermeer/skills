# `/implement` ends with a retrospective that does not block land

Every `/implement` run gathers a **Retrospective** before it deletes the Spec and Steps, lands the branch without waiting, then presents the suggestions in chat. You can still type `/retrospective` on the current session or a session you name. Other named session skills start one too; that list lives in [ADR-0021](0021-named-session-skills-start-a-retrospective.md).

Waiting for you to accept suggestions was rejected because `/implement` already lands without waiting after review, and environment changes help the next run rather than this branch. Writing a file was rejected because unused retrospective files become sediment; the session transcript is the record. Skipping the run when there is nothing to suggest was rejected so you can tell the step ran.

## Consequences

- A halt skips the retrospective. Resume first.
- The skill ends when the list is presented. Applying is a new request, on master.
- Suggestions are only what this session demonstrated, ranked by how often the pain will recur and how much it costs.
