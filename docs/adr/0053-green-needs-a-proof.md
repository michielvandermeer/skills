# Green needs a Proof

A Step counted as **Green** once its tests passed, plus whatever verification the repo's conventions asked for. A repo with no such convention got no verification at all. Small but risky changes, such as cache eviction, teardown order, wire formats and flags, landed on passing tests that never touched the risky path. So Green now also needs a **Proof**. The Step agent names the Step's **Safety fact**, the one fact the change is safe because of, which must name what breaks if it is false. The Checker re-runs the Proof for that fact itself, from a fresh context, and refuses Green without it. Re-running is also what stops an agent from quoting output it never produced.

The **Proof ladder** has four rungs: stated or read in the code, which is not Proof; the existing tests pass; a test or throwaway script calls the real code on the risky path; reproduced in the running app. Every Step that changes code that runs needs rung 3. A Step that changes a web page, a command-line tool or an HTTP service needs rung 4. A library tops out at rung 3. When the app cannot start locally without a live system, rung 3 stands and the run reports a Deviation. A docs-only Step needs no Safety fact.

Rung 4 runs through a **Run recipe**, kept in the consuming repo at `.agents/refs/run-recipe.md`. A repo with a `CONTEXT-MAP.md` keeps one recipe per context with a running surface. The first agent that has to drive the app writes the recipe. Later agents follow it, and edit it only where it steered them wrong. Every section is a plain shell command, so the recipe works on every host. Proof files live in `<git common dir>/proof/<slug>/`, outside every working tree, so no commit can sweep them in. The rules are in `skills/implement/PROOF.md`.

## Considered Options

- **Three rungs, as in pstack** ("said so", "ran real code", "reproduced in the app"). Rejected: it puts "the suite passed" and "a check aimed at the fact" on one rung, and that gap is the failure this ADR exists for.
- **The Spec sets the rung.** Rejected: it adds a field that `/to-spec` and the Planner must fill in, and the field is easy to set too low.
- **Rung 4 recorded but never required.** Rejected: a feature that is broken in the app would still land.
- **Halting when rung 4 is out of reach.** Rejected: every web Step would stop in exactly the repos that cannot run locally. A Deviation keeps the gap visible.
- **The recipe as a host project skill under `.claude/skills/`, or whatever a host's own run or verify command writes.** Rejected: the rule has to work on every host the plugin supports, and those files are tied to one host and have no fixed format.
- **Proofs written before the code and kept as a regression suite.** Rejected: it adds a second test suite to maintain beside the repo's real one, and that suite risks becoming slow and flaky.
- **A Safety-fact check in `/code-review`.** Rejected: its reviewers see only the diff, and the Checker already refuses a fact that names nothing that could break.
- **Re-running every Proof after the rebase at land.** Rejected: a run with many web Steps would drive the app again for each one, and the tests still run after the rebase. The final report says the Proofs predate the rebase instead.

## Consequences

- The final report lists each Step's Safety fact and its rung, and names the Proof folder. The folder is kept after the run.
- A Proof that fails on the Checker's re-run gets one more try. If it passes, the flake is a Deviation. A flake the recipe caused is fixed in the recipe.
- `/retro` counts an edit to an existing Run recipe as a Correction. When a command could have caught the problem, `/retro` adds that command to the recipe's Check section.
