# `/implement` plans Steps, then loops implement, review, and verify

`/implement` starts with a **Planner** that walks the code and slices the Spec into **Steps**, each small enough for one fresh agent, and commits them as Step files. Most Specs are one Step. Then it runs one loop over the whole Spec: an **Implementer** per Step builds the change, `/code-review` judges it on the Standards axis alone — the repo's Coding standards and the **Design principles** — and a **Verifier** checks it does what the Spec asks, by reading the Spec against the diff, running the build and the whole test suite, and running the Spec's **Hand checks**. A **Hard violation** from Review, or a Verify finding, sends the run back to a single fresh Implementer with those findings, for at most three **Iterations**; the third that still fails halts the run. A **Judgement call** sends the run nowhere: it waits for the next Implementer when another Iteration runs anyway, and otherwise lands unfixed and is listed in the final report. From the second Iteration on, Review reads only that Iteration's fix, with the findings it was meant to fix. The run lands when one Iteration passes both.

`/to-spec` and `/grill-with-docs` aim for Specs one agent can build, but nothing guarantees it, and a Spec too large for one context fails late and expensively. The Planner is cheap on a small Spec, one walk whose Footprint the Implementer then starts from instead of walking again, and on a large one it is what keeps each Implementer inside one context.

The loop closes: every fix is reviewed and verified again before the run lands, so no Hard violation or Verify finding lands unchecked. A Judgement call is an opinion about the shape of correct code, and a fresh reviewer on the whole diff always has another, so a loop on every finding never settles. Reviewing only the fix, against the findings it answers, gives each later Review something to finish. Review lives in one place and verification in one place, each with one agent and one report, so there is nothing for several agents to keep in step.

Review judges how the code is written; Verify judges whether it does what was asked. Keeping them in separate agents stops one from masking the other, the same reason `/code-review` keeps its two axes apart. Review runs first because a Standards fix can change behaviour, and the Verifier should run on the code that would land.

## Considered Options

- **No Planner: one Implementer builds the whole Spec.** Tried, then reversed. It relied on every Spec fitting one agent's context, and a Spec that did not halted only after an Iteration's worth of cost.
- **Review and Verify each Step.** Rejected: a Step is not a change anyone ships, the per-Step reviews and verifications multiply the cost of a large Spec, and the Spec's Hand checks describe the whole change. Review and Verify judge all Steps together, once per Iteration.
- **Steps on every Iteration, fixing findings Step by Step.** Rejected: findings land across Steps, and one Iteration's fixes fit one agent.
- **A `Depends on:` line naming which earlier Outcomes a Step reads.** Rejected: an Outcome is a few lines, so every Step reads all earlier ones, and nothing can be left off by mistake.
- **Keep the Proof ladder and Safety fact inside Verify.** Rejected: the Spec's Hand checks and the whole suite already say what must hold, and a Safety fact per change was a second spec the agents wrote for themselves. A Hand check on a running surface drives the app through the repo's Verify skill ([ADR-0075](0075-setup-verify-writes-the-verify-skill-the-verifier-drives.md)).
- **Run Verify even when Review found a Hard violation.** Rejected: the Implementer's fixes would change the code Verify just checked, so the next Iteration's Verify repeats the work.
- **Review and Verify in one agent.** Rejected: one context then judges both, and a strong finding on one axis crowds out the other.
- **A Fixer after Review, separate from the Implementer.** Rejected: a fresh Implementer each Iteration is that Fixer, under the same contract, so one agent file covers both.
- **Any Review finding loops.** Tried, then reversed. In a benchmark smoke pass, Review findings drove a one-Step bug fix through three Iterations, 15 minutes and $4.40 against 9 minutes and $2.84 before the loop, with the Opus reviewer $1.03 of the gap; a six-file Spec halted after three Iterations of Review findings without Verify ever running. Each extra Iteration paid a fresh Implementer's orientation and a fresh Opus review for any finding, however small, though `/code-review` called every principle finding a judgement call.
- **Every Review reads the whole diff.** Rejected: a fresh reviewer on the whole change raises new judgement calls each time, and the cost of the Review grows with the change rather than with the fix.
- **One Implementer fixes the Judgement calls before Verify, with no Review after.** Rejected: it adds an Implementer to most runs, and a fix that rides an Iteration the run needs anyway costs nothing extra.
- **No limit on Iterations.** Rejected: a Review finding the Implementer keeps declining, or a test it cannot fix, would loop forever. Three leaves room for a fix and a fix of the fix.

## Consequences

- The Planner commits the Step files as `plan: <slug>` before any code, and each Step's Implementer commits its Outcome and `Status: done` with its code, so a resume starts at the first Step not done, or at Review when every Step is.
- A Step's Footprint is a guess. Where the code disagrees, the code wins, and the drift goes in that Step's Outcome, which every later Step reads.
- The Implementer reads the Design principles before it writes, since the Review judges by them. It may decline a Review finding with a reason, and the next Review raises it again only when that reason does not hold. It fixes every Verify finding.
- `/code-review` opens each Standards finding with `Hard violation:` or `Judgement call:`. A principle finding is a Hard violation only when it names a wrong result, a crash, or lost data.
- Only agents read an implement run's Review report, so its reviewer skips the `/technical-writing` bar.
- Judgement calls alone never halt a run.
- The whole test suite runs once per Iteration that reaches Verify, in the Verifier. Each Implementer builds the projects on its Footprint and runs only the tests closest to its change.
- A rebase at land that brings in code the last Verify did not check sends the run through one more Verify, and a failure there starts the next Iteration.
- A resume starts again at Iteration 1, with three Iterations, on top of the branch's commits.
- The landing commit's body lists each Step's title when the run had more than one ([ADR-0062](0062-an-implement-run-lands-as-one-commit.md)).
- A Spec that holds several changes is still a Spec to split, because the run lands it as one ([ADR-0073](0073-a-spec-is-held-to-the-planning-principles.md)).
- Merge risk is no longer recorded during the run. `/pr` works it out from the diff when it writes a description.
- The Planner, the Implementer, and the Verifier are Spec-bound and pinned to Sonnet at `effort: high` ([ADR-0049](0049-agents-are-pinned-in-their-agent-files.md)).
