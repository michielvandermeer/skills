# A prototype session runs in a worktree and hands over a Spec

A `/prototype` session runs inside a git worktree on a `prototype/<slug>` branch, the way `/implement` runs inside one, and ends by writing a Spec in the original checkout and then removing the worktree and force-deleting the branch. The playable artifact is kept separately ([ADR-0018](0018-prototypes-live-under-agents-prototypes.md)). The Spec names the question the prototype was built to answer and what playing with it settled. `/prototype` folds nothing into real code, so the Spec is the handover to `/implement`.

Keeping the branch after removing the worktree was rejected: it costs nothing in git and everything in housekeeping, and a repo that accumulates `prototype/*` branches nobody prunes is worse than one that trusts its Specs. Folding the decision into real code at the tail of the session was rejected because a throwaway branch that merges is not throwaway, and the fold is real work that deserves a Spec. Writing the Spec inside the worktree was rejected because it would be deleted along with it.

## Consequences

- A session that hands the prototype over and gets no verdict commits the prototype and stops, leaving the worktree and branch in place. Re-entry finds the run by its `prototype/<slug>` branch and resets nothing — a `git reset --hard && git clean -fd` resume would destroy the prototype it came back for.
- A `/prototype` invoked from a session already inside a worktree serves that larger effort: it returns its verdict, writes no Spec, and removes nothing, so one effort never produces two Specs. It does write the folder the parent names ([ADR-0018](0018-prototypes-live-under-agents-prototypes.md)).
- A verdict that kills the idea ends with no Spec and no folder. The session reports what was learned, removes the worktree and branch the same way, and writes an ADR only where the three-part test passes.
- A prompt that explicitly waives the worktree builds in the checkout, as `/implement`'s waiver does: the folder is written there, and the in-app prototype files that are not the folder are removed.
- The worktree levers are host-shaped exactly as [ADR-0015](0015-implement-worktree-host-agnostic.md) sets them, and the fallback path is `.agents/worktrees/prototype/<slug>`. A fresh worktree carries no installed dependencies, so a UI prototype installs the project's before rule 2's one command works.
