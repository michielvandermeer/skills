# `/implement` stays sequential on a confined host

This amends [ADR-0033](0033-implement-runs-ready-steps-in-parallel.md). ADR-0033 runs Ready Steps in parallel, each in its own Step worktree opened from the main checkout, because that gives two editors two trees, and keeps a waived worktree sequential because there is only one checkout. Some hosts confine a session to the worktree it started in and refuse a git command aimed at the main checkout, so that session can never open a Step worktree. This happened in another repository: the Step agent had no Step worktree to work in, so it committed straight to the run branch — the skill had no path for that, and the run only continued because the agent improvised.

`/implement` now detects this from the host's own behaviour, not from its name. The first **refusal** — a permission or sandbox block on a git command aimed outside the run worktree, or a Step agent reporting it cannot work in its Step worktree — makes the run a **confined host** for the rest of the session. An ordinary git error, such as a branch that already exists, is not a refusal and stays on the parallel path. From the first refusal on, Ready Steps run one at a time in the run worktree — no Step worktree, no Step branch, no rebase — the same as a waived worktree, because both have one checkout to work in. The structural check and the retry reset move to the run worktree with it.

A refusal can arrive after some Step worktrees exist: siblings already in flight, or the Step whose agent could not use its worktree. Those siblings finish, and a done one lands on the run branch by cherry-pick from the run worktree, because the host may refuse a rebase in the Step worktree. The refused Step runs again in the run worktree without spending its one retry, since the failure was the host's, not the Step's. Each leftover Step worktree and Step branch is removed from the run worktree; one the host will not let the session remove is named in the final report.

Treating every host-created run worktree as confined, rather than waiting for a refusal, was rejected: most hosts that create a run worktree still allow Step worktrees off it, and that path drops parallel Steps everywhere for a problem only some hosts have.

## Consequences

- ADR-0033's parallel path is unchanged for a host that allows Step worktrees.
- Only step 3 changes. A confined run keeps its run worktree, so resume and land take the normal step 1 and step 6 — unlike a waived worktree, which has no run worktree and takes the changed step 6.
- A future host-detected refusal on a different git command falls under the same rule: it is still a permission or sandbox block, not an ordinary git error.
