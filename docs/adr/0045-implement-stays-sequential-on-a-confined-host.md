# `/implement` stays sequential on a confined host

[ADR-0033](0033-implement-runs-ready-steps-in-parallel.md) runs Ready Steps in parallel, each in its own Step worktree opened from the main checkout, because that gives two editors two trees. Some hosts confine a session to the worktree it started in and refuse a git command aimed at the main checkout, so that session can never open a Step worktree. This happened in another repository: the Step agent had no Step worktree to work in, so it committed straight to the run branch — the skill had no path for that, and the run only continued because the agent improvised.

`/implement` now detects this from the host's own behaviour, not from its name: the first refusal of a git command aimed at the main checkout, or a Step agent reporting it cannot reach its own Step worktree, makes the run a **confined host** for the rest of the session. From that point on, Ready Steps run one at a time in the run worktree — no Step worktree, no Step branch, no rebase — the same as a waived worktree already does, because both share one checkout to work in. The structural check and the retry reset both move to the run worktree in step with it.

Treating every host-created run worktree as confined, rather than waiting for a refusal, was rejected: most hosts that create a run worktree still allow Step worktrees off it, and that path drops parallel Steps everywhere for a problem only some hosts have.

## Consequences

- ADR-0033's parallel path is unchanged for a host that allows Step worktrees.
- A confined host never creates a Step worktree or a Step branch, so land and resume see the same shape they already handle for a waived worktree.
- A future host-detected refusal on a different git command falls under the same rule: it is still a permission or sandbox block, not an ordinary git error.
