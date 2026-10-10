# Green needs a Proof

A Step counted as **Green** once its tests passed, plus whatever verification the repo's conventions asked for. A repo with no such convention got no verification at all. Small but risky changes, such as cache eviction, teardown order, wire formats and flags, landed on passing tests that never touched the risky path. So Green now also needs a **Proof**. The Step agent names the Step's **Safety fact**, the one fact the change is safe because of, which must name what breaks if it is false. The Checker re-runs the Proof for that fact itself, from a fresh context, and refuses Green without it. Re-running is also what stops an agent from quoting output it never produced.

The **Proof ladder** has four rungs: stated or read in the code, which is not Proof; the existing tests pass; a test or throwaway script calls the real code on the risky path; reproduced in the running app. Every Step that changes code that runs needs rung 3. A Step that changes a web page, a command-line tool or an HTTP service needs rung 4. A library tops out at rung 3. When rung 4 is out of reach — the app cannot start locally without a live system, credentials, or a paid account, or how to launch it cannot be worked out — rung 3 stands and the run reports a Deviation. A docs-only Step needs no Safety fact.

Rung 4 runs through a **Run recipe**, kept in the consuming repo at `.agents/refs/run-recipe.md`. A repo with a `CONTEXT-MAP.md` keeps one recipe per context with a running surface. The first agent that has to drive the app writes the recipe. Later agents follow it, and edit it only where it steered them wrong. Every section is a plain shell command, so the recipe works on every host. Proof files live in `.agents/proof/<slug>/` inside the run's working tree, where every agent of the run can write and a resumed run finds them. A `.gitignore` in that folder holding `*` keeps them out of git, so no commit can sweep them in. They are agent artifacts that no person reads, so the run deletes the folder when it finishes and keeps it only through a halt, for the resume. The rules are in `skills/implement/PROOF.md`.

## Considered Options

- **Three rungs, as in pstack** ("said so", "ran real code", "reproduced in the app"). Rejected: it puts "the suite passed" and "a check aimed at the fact" on one rung, and that gap is the failure this ADR exists for.
- **The Spec sets the rung.** Rejected: it adds a field that `/to-spec` and the Planner must fill in, and the field is easy to set too low.
- **Rung 4 recorded but never required.** Rejected: a feature that is broken in the app would still land.
- **Halting when rung 4 is out of reach.** Rejected: every web Step would stop in exactly the repos that cannot run locally. A Deviation keeps the gap visible.
- **The recipe as a host project skill under `.claude/skills/`, or whatever a host's own run or verify command writes.** Rejected: the rule has to work on every host the plugin supports, and those files are tied to one host and have no fixed format.
- **Proofs written before the code and kept as a regression suite.** Rejected: it adds a second test suite to maintain beside the repo's real one, and that suite risks becoming slow and flaky.
- **A Safety-fact check in `/code-review`.** Rejected: its reviewers see only the diff, and the Checker already refuses a fact that names nothing that could break.
- **Keeping the Proof folder after the run so the user can look through it.** Rejected: nobody reads Proofs once the Checker has re-run them, and kept folders pile up.
- **Proof files in a system temp directory.** Rejected: a run resumed from a new session cannot find it.
- **Proof files in the git common directory, at `<git common dir>/proof/<slug>/`, outside every working tree.** Rejected: a host that isolates a session in its worktree refuses writes there. Claude Code refuses both file writes to that path and shell commands that name `.git`, so agents could not save their Proofs.
- **Ignoring the folder through the repo's `.gitignore` or `.git/info/exclude`.** Rejected: the first changes a file the user's repo tracks, and the second sits in the git common directory, where the same isolation refuses writes.

## Consequences

- The final report lists each Step's Safety fact and its rung. Before the run lands, a Prover re-runs every Proof on the code that lands ([ADR-0058](0058-a-prover-re-proves-the-code-that-lands.md)). The Proof folder is deleted once the run has landed; a halted run keeps it.
- A Proof that fails on the Checker's re-run gets one more try. If it passes, the flake is a Deviation. A flake the recipe caused is fixed in the recipe.
- `/retro` counts an edit to an existing Run recipe as a Correction. When a command could have caught the problem, `/retro` adds that command to the recipe's Check section; otherwise the edited recipe holds the lesson.
