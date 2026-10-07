# A fresh Checker finishes each Step

In all three implement commands, the Step agent does not review its own work. Once it has committed its Step with its build and the tests closest to its change passing, the Driving session sends a fresh **Checker** (`skills:checker`). The Checker re-runs the Step's Proof ([ADR-0053](0053-green-needs-a-proof.md)), reviews the Step's commit on both axes, fixes what it finds, runs the Step's full set of tests, and puts the fixes and the status flip in a new commit — never an amend, because auto mode can refuse amending. In 48 hours of transcripts (2026-09-24 to 2026-09-26), review-and-fix inside the Step agent took 29% of Step agent spend, because by then its context had grown to 300–400k tokens and every turn re-reads the whole context. A Checker starts from the Step file and the Step's changes, at a small fraction of that.

The trade: the Checker does not know the code the way the Step agent does, and it re-reads what it needs to fix. Review findings name the place they are about, so that re-reading is narrow.

The Checker is the only agent that runs a Step's full set of tests: the tests of the Footprint's projects, or the whole suite on the last Step and on a Step with no Footprint. The Step agent builds those projects and runs only the tests it wrote or changed and those covering the code it changed. The Checker runs the full set once, after its fixes, and when that run is red it fixes the failures and re-runs only the projects that failed and those its new fixes touched. A full run in both agents cost about 11% of run time on measured Claude Code runs (147 of 1,382 minutes over 14 sessions, 2026-10-06). The Step agent's run is the one that goes: 19 of 22 Checkers in a second sample changed code, mostly on review findings, so only the Checker's run sees the code the Step lands with. Keeping the full run in the Checker also keeps a second agent watching every test pass.

## Considered Options

The Step agent starting the Checker itself was rejected. The Step agent would wait at peak context while the Checker worked, and the Checker's reviewers would sit three agents deep. Every other `/implement` sub-agent is sent by the Driving session.

Moving only the Proof re-run, and keeping the review-and-fix loop in the Step agent, was rejected. Both run at peak context, and the loop is the larger part.

Dropping the per-Step Standards review and leaving it to the final review was rejected. Once the review runs at a small context, the saving left is small, and it would move more work onto the final fixers, which were already the longest agents in a run.

The Step agent keeping the full test run, with the Checker re-running only the projects its fixes touched, was rejected. The projects the Checker leaves alone would count as passing on the Step agent's word, and nothing records that run.

Adding a whole-suite run to the Prover's end-of-run pass, to catch such a false pass before landing, was rejected. Every run would gain a whole-suite run, which cancels the saving on single-Step runs, where the repeat cost most.

The Checker skipping its test run when it changed nothing but the Step file was rejected. Too few Checkers change nothing for the rule to pay.

Amending the Step agent's commit with the Checker's fixes and status flip was rejected. Auto mode can refuse an amend, which leaves the Step stuck at `built` with no way for the Checker to land the status flip.

## Consequences

- A Step has two states after `pending`. The Step agent sets `Status: built`, and the Checker sets `done`. A resumed run restarts a `built` Step at its Checker, so a check is never skipped, and that Checker does the Step's full test run.
- A `built` Step can be red in a Footprint project that its Step agent's tests did not reach. The Checker's full run finds it, and the Checker fixes it as it fixes a review finding.
- Before its fix phase, the Checker runs the Proof and no other tests, so the full run happens on fixed code.
- A Step is **Green** only on the Checker's own test run and its Proof re-run.
- The Checker is Spec-bound and runs at `effort: medium`, the effort the review-and-fix loop already ran at inside the Step agent ([ADR-0049](0049-spec-bound-agents-keep-the-session-model.md)).
