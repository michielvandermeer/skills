# The implement commands differ only in planning and worktree

All three implement commands run the same flow: Step agent, Checker, review and fixers, document, then land or clean up. Green needs a Proof that a fresh agent re-runs ([ADR-0053](0053-green-needs-a-proof.md)), so `/implement-oneshot` and `/implement-yolo` use that flow too. `/implement-oneshot` skips only the Planner. Its Driving session writes one Step file for the whole Spec, with no Footprint, so the whole suite runs. `/implement-yolo` also skips the worktree. Both send `skills:implementer` and `skills:checker` to that Step. There is no `skills:oneshot` dispatch.

## Considered Options

- **The Driving session re-runs the Proof itself.** Rejected: the run would then have no per-Step review, and the oneshot flow would still differ from `/implement` in more than planning.
- **A Proof-only Checker mode for oneshot runs.** Rejected: it gives one agent two contracts to keep apart.
- **Keeping `skills:oneshot` and teaching it the Step file.** Rejected: two agent files would carry the same contract and drift apart.
- **The build agent writes its Outcome into the Spec.** Rejected: the Spec would become something agents write into mid-run, and a resumed run could not tell `built` from `done`.

## Consequences

- Every command resumes at the lowest Step that is not `done`, including Step files another command wrote, because only the planning differs.
- `/implement-yolo` commits the Step file on your branch and removes it in its cleanup commit. A retry there never resets the tree.
- `/document-changes` reads the Step's Outcome in every command.
