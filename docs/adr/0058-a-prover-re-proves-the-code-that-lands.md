# A Prover re-proves the code that lands

Each Step's Checker re-runs that Step's Proof ([ADR-0053](0053-green-needs-a-proof.md)), but the code keeps moving afterwards. Later Steps, the final review's fixers, and the rebase onto a moved base branch all change it, and the fixers re-run only the tests of the projects they touched. A fixer that breaks a Safety fact while those tests stay green is the failure ADR-0053 exists for, so the code that lands now gets its own Proof pass. In all three implement commands, once the final fixers and, where the command rebases, the rebase have run, a fresh **Prover** (`skills:prover`) re-runs every Step's Proof on that code. It wrote none of those Proofs. It works from each Step's `Safety fact:` and `Proof:` lines and the Proof folder, so a Step leaves nothing new behind. It launches the app once for every rung-4 Proof and drives them in Step order. A failing Proof is re-run once under the flake rule; at rung 4 that re-run gets a fresh launch, so state an earlier drive left cannot fail it.

A Proof that fails twice goes to one **Proof fixer**, at the Driving session's model and effort. That fixer does one of three things. It restores the fact. It updates a Proof that only went stale, such as one calling something a later change renamed. Or, when the Spec asked a later Step to change that behaviour, it leaves the code alone and retires the fact as a Deviation. A fresh Prover then re-runs every Proof that is not retired, and a second failure halts the run. Runs get slightly longer. A run that is a little slower is better than bugs left to find after landing.

## Considered Options

- **Re-running the Proofs only once, at the end, in place of the Checker's re-run after every Step.** Rejected: it delays finding a broken Step until later Steps have already built on it, and it saves only the Proof minutes, which were 1–13% of Checker time in measured runs.
- **The Driving session re-runs the Proofs itself.** Rejected: the Driving session holds only reports and paths, which is what lets a run of any size land inside one session. Driving the app and reading every Proof's output would fill that context.
- **A Checker with a wider contract that also runs the end pass.** Rejected: it gives one agent two contracts to keep apart, the trap ADR-0054 already rejects for a Proof-only Checker mode.
- **Fixing only what the final fixers or the rebase broke.** The Prover would first re-run a failing Proof on the code from before them, and a fact that already failed there would only be flagged. Rejected: a later Step that broke an earlier fact would land with a flag and no fix, and the run would have to keep that older code reachable across the rebase and a resume.
- **Halting on any failure that survives the flake re-run.** Rejected: a run whose last Step retires an earlier fact on purpose, such as removing an old path a first Step kept working, would halt at the very end every time.
- **A fresh app launch for every rung-4 Proof.** Rejected: each launch adds time for every Step that changes a running surface, and the fresh launch on a re-run already stops leftover state from failing a Proof.

## Consequences

- In `/implement` and `/implement-oneshot`, the pass runs after the rebase and the post-rebase build. Deleting the Step files and the Spec in a commit on the run's branch, and building the landing commit from it, come after the pass. The Proof folder is deleted once the merge has succeeded. When the merge fails because the base branch moved, the run drops that deletion commit, rebases again, and runs the pass again before the next merge.
- In `/implement-yolo`, which has no rebase, the pass runs after `/document-changes` and before the landing commit.
- A halted run resumes at the final review once every Step is `done`, as before, so the pass is never skipped. A halt keeps the Step files and the Proof folder.
- The final report lists each Step's Safety fact as the pass left it. It names each flake, each Proof the Proof fixer restored or updated, and each fact it retired.
- A Step's **Green** does not wait on the pass, because the pass checks the whole run.
- In rare cases, state left by an earlier drive could hide a break from a later rung-4 Proof. That is the price of one launch.
- The Prover is Spec-bound and runs at `effort: medium` on the session's model ([ADR-0049](0049-spec-bound-agents-keep-the-session-model.md)).
