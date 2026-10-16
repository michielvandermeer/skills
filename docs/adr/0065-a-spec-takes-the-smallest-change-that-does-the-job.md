# A Spec takes the smallest change that does the job

`/to-spec` holds every implementation choice it makes itself to the smallest change that does the job, using what the code already does. A choice a person settled keeps its width: an answer in a grilling round, a declaration that stood through its round, or a line the Issue or brief states outright. A choice the agent reasoned out earlier in the same conversation is not settled, so the rule applies to it. When a decision builds a new mechanism and the code already does the same job another way, the Spec says why that way falls short. When a decision guards against a failure, the Spec names that failure and how it would realistically happen. The Validator's checklist flags either gap as an open question.

The rule binds how the change is built, never what the person who uses it meets. Where the smallest build leaves that person a worse experience than a wider one — no error message, a clumsy extra step — `/grilling` asks, and `/to-spec`, with no one to ask, builds the wider one and says why ([Experience first](../../skills/to-spec/PRINCIPLES.md#experience-first)).

`/grilling` and `/wayfinder` already recommend the smallest change. But `/to-spec` also writes Specs where no grilling ran: after `/triage`, `/prototype`, and `/improve-codebase-architecture`, and when someone types it. In one triaged security fix, `/to-spec` moved an ownership check into a single SQL statement in a shared library. That took a new repository method, a statement built from CTEs, and new integration tests against a real database. The extra width guarded only against a race nobody named. About five lines in the handler did the same job, using the call the page's other handlers already made, and the Spec itself named that pattern.

## Considered Options

- **Pointing `/to-spec` at `/grilling`'s rule.** Rejected: the pointer would load grilling's whole round format for one rule. `/wayfinder` keeps its own copy of the rule for the same reason.
- **Leaving the rule to the session that drafts the Spec.** Rejected: that session shares its own blind spots. In the case above, the Spec named the existing pattern and still built past it. A Validator reading the draft cold asks whether the code already does the job.
- **Letting the Validator narrow a decision in place.** Rejected: how wide a Spec builds is a decision, and the Validator has no user ([ADR-0052](0052-a-fresh-validator-checks-a-new-spec.md)).
- **Treating a choice the agent made earlier in the conversation as settled.** Rejected: in a `/triage` run, no person sees that choice before the Spec is written.
- **Sending an explorer from `/to-spec` before drafting.** Rejected: in the case above the facts were already there. The judgement was missing.
- **Letting the smallest change decide the experience too.** Rejected: rough edges would ship by default, and the case above was about width in the mechanism, not in what the person sees.

## Consequences

- A `/validate-spec` someone types, and `/review-spec`, run the same width check, because they use the same checklist. A `needs-` Issue is not checked, because it holds no implementation decisions.
- A width flag does not stop the Spec from being written, as with any open question under ADR-0052.
- `/triage` is unchanged. `/grilling` asks, rather than declares, when the smallest build and the better experience differ.
