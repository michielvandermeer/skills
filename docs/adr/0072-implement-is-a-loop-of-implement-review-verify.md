# `/implement` is a loop of implement, review, and verify

`/implement` runs one loop over the whole Spec: an **Implementer** makes the change, `/code-review` judges it on the Standards axis alone — the repo's Coding standards and the **Design principles** — and a **Verifier** checks it does what the Spec asks, by reading the Spec against the diff, running the build and the whole test suite, and running the Spec's **Hand checks**. A Review or Verify finding sends the run back to a fresh Implementer with those findings, for at most three **Iterations**; the third that still fails halts the run. The run lands when one Iteration passes both.

The loop closes: every fix is reviewed and verified again before the run lands, so no finding lands unchecked. Review lives in one place and verification in one place, each with one agent and one report, so there is nothing for several agents to keep in step.

Review judges how the code is written; Verify judges whether it does what was asked. Keeping them in separate agents stops one from masking the other, the same reason `/code-review` keeps its two axes apart. Review runs first because a Standards fix can change behaviour, and the Verifier should run on the code that would land.

## Considered Options

- **Keep the Planner and loop per Step.** Rejected: slicing paid off only on Specs too large for one agent, and it brought Footprints, Outcomes, Depends-on lines, and a resume per Step. A Spec too large for one Implementer is a Spec to split into several Issues.
- **Keep the Proof ladder and Safety fact inside Verify.** Rejected: the Spec's Hand checks and the whole suite already say what must hold, and a Safety fact per change was a second spec the agents wrote for themselves. The Run recipe stays, because a Hand check on a running surface needs it.
- **Run Verify even when Review found something.** Rejected: the Implementer's fixes would change the code Verify just checked, so the next Iteration's Verify repeats the work.
- **Review and Verify in one agent.** Rejected: one context then judges both, and a strong finding on one axis crowds out the other.
- **A Fixer after Review, separate from the Implementer.** Rejected: a fresh Implementer each Iteration is that Fixer, under the same contract, so one agent file covers both.
- **No limit on Iterations.** Rejected: a Review finding the Implementer keeps declining, or a test it cannot fix, would loop forever. Three leaves room for a fix and a fix of the fix.

## Consequences

- The Implementer reads the Design principles before it writes, since the Review judges by them. It may decline a Review finding with a reason, and the next Review raises it again only when that reason does not hold. It fixes every Verify finding.
- The whole test suite runs once per Iteration that reaches Verify, in the Verifier. The Implementer runs only the tests closest to its change.
- A rebase at land that brings in code the last Verify did not check sends the run through one more Verify, and a failure there starts the next Iteration.
- A resume starts again at Iteration 1, with three Iterations, on top of the branch's commits.
- Merge risk is no longer recorded during the run. `/pr` works it out from the diff when it writes a description.
- The Implementer and the Verifier are Spec-bound and pinned to Sonnet at `effort: high` ([ADR-0049](0049-agents-are-pinned-in-their-agent-files.md)).
