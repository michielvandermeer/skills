# A Spec is held to the planning principles

A Spec is the whole input to an `/implement` run, and that run has no one to ask ([ADR-0072](0072-implement-is-a-loop-of-implement-review-verify.md)). The judgement calls a good Spec needs are one list, the **Planning principles** in `skills/to-spec/PRINCIPLES.md`: leave the implementer nothing to ask, fit one run, experience first, exhaust the design space, sequence verifiable units, explain the number, attack the premise, build the lever, and converge on the end state. Each says when it applies, what it looks like in a Spec, and the fix. `/grilling` recommends options by them, `/to-spec` writes to them, and the Validator applies them as one checklist item. A miss is an open question in the Validator's report, as a width gap is under [ADR-0065](0065-a-spec-takes-the-smallest-change-that-does-the-job.md).

Since a single Implementer now builds the whole Spec, a Spec that one session cannot read and build is too big. The Validator reports it, and a person splits it or moves the change to `/wayfinder`.

## Considered Options

- **Spreading each principle into the skill step where it applies.** Rejected: the same rule would live in three or four skills, and nothing would check the finished Spec against all of them. Every route to a Spec — `/triage`, `/grill-with-docs`, `/wayfinder`, `/prototype` — ends in `/to-spec` and its Validator, so one list checked there covers them all, as `/code-review`'s Design principles do for code.
- **Letting `/to-spec` split a Spec that is too big.** Rejected: a split decides what ships when, and `/triage` would make it with no person watching.
- **Letting the Iteration limit catch a Spec that is too big.** Rejected: the run would halt after three Iterations' worth of cost.
- **Also stopping `/implement` to question the premise when two Iterations fail the same check.** Deferred: this decision covers planning only.

## Consequences

- `/triage` looks for earlier failed fixes of a bug, measures a number a report claims, and hands the reproduction to the Spec as the test that fails on today's code.
- `/grilling` treats a design with no precedent in the codebase as a `/prototype` question, and a logic prototype then builds two or three competing models.
- A Validator finding on a principle does not stop the Spec from being written, as with any open question under [ADR-0052](0052-a-fresh-validator-checks-a-new-spec.md).
- A `/validate-spec` someone types, and `/review-spec`, apply the same principles, because they use the same checklist.
