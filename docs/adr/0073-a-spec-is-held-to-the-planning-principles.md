# A Spec is held to the planning principles

A Spec is the whole input to an `/implement` run, and that run has no one to ask ([ADR-0072](0072-implement-plans-steps-then-loops-implement-review-verify.md)). The judgement calls a good Spec needs are one list, the **Planning principles** in `skills/to-spec/PRINCIPLES.md`: leave the implementer nothing to ask, fit one run, experience first, exhaust the design space, sequence verifiable units, check from outside, explain the number, attack the premise, build the lever, and converge on the end state. Each says when it applies, what it looks like in a Spec, and the fix. `/grilling` recommends options by them, `/to-spec` writes to them, and the Validator applies them as one checklist item. A miss is an open question in the Validator's report, as a width gap is under [ADR-0065](0065-a-spec-takes-the-smallest-change-that-does-the-job.md).

Before it chooses the change, `/to-spec` sharpens the task, as pstack's `/sharpen` does: how a top expert would approach it, what the person is really after, and which constraints serve that. Check from outside is the part of that pass the Validator can see in the finished Spec.

The Planner slices a Spec into Steps that each fit one session, but the run reviews, verifies, and lands the whole Spec as one change. So a Spec that holds several changes, each of which could ship alone, is too big. The Validator reports it, and a person splits it or moves the change to `/wayfinder`.

## Considered Options

- **Spreading each principle into the skill step where it applies.** Rejected: the same rule would live in three or four skills, and nothing would check the finished Spec against all of them. Every route to a Spec — `/triage`, `/grill-with-docs`, `/wayfinder`, `/prototype` — ends in `/to-spec` and its Validator, so one list checked there covers them all, as `/code-review`'s Design principles do for code.
- **Sharpening inside `/implement`.** Rejected: the Spec already leaves the implementer nothing to ask, and re-framing the task there would undo the plan a person agreed to.
- **A standalone `/sharpen` skill.** Rejected: it would run only when someone typed it, while every route to a Spec already passes through `/to-spec`.
- **Letting `/to-spec` split a Spec that is too big.** Rejected: a split decides what ships when, and `/triage` would make it with no person watching.
- **Letting the Iteration limit catch a Spec that is too big.** Rejected: the run would halt after three Iterations' worth of cost.
- **Also stopping `/implement` to question the premise when two Iterations fail the same check.** Deferred: this decision covers planning only.

## Consequences

- `/triage` looks for earlier failed fixes of a bug, measures a number a report claims, and hands the reproduction to the Spec as the test that fails on today's code.
- `/grilling` treats a design with no precedent in the codebase as a `/prototype` question, and a logic prototype then builds two or three competing models.
- A Validator finding on a principle does not stop the Spec from being written, as with any open question under [ADR-0052](0052-a-fresh-validator-checks-a-new-spec.md).
