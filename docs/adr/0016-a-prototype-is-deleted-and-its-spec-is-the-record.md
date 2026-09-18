---
status: superseded by ADR-0018
---

# A prototype is deleted, and its Spec is the record

`/prototype` used to build in the working checkout, fold the validated decision into real code itself, and park the prototype on a lasting `prototype/<name>` branch as a primary source. A `/prototype` session now runs inside a git worktree on that branch, the way `/implement` runs inside one, and ends by writing a Spec in the original checkout and then removing the worktree and force-deleting the branch. The prototype does not survive its own session. Because nothing else is left, the Spec must name the question the prototype was built to answer and what playing with it settled; a snippet that encodes a decision better than prose — a reducer, a state machine, a schema — is inlined under `/to-spec`'s existing rule. `/prototype` folds nothing into real code, so the Spec is the handover to `/implement`, and `/prototype` joins `/triage` ([ADR-0014](0014-triage-ends-in-a-spec.md)) and `/wayfinder` ([ADR-0011](0011-every-wayfinder-map-ends-in-a-spec.md)) as an effort that ends in one.

Keeping the branch after removing the worktree was rejected: it costs nothing in git and everything in housekeeping, and a repo that accumulates `prototype/*` branches nobody prunes is worse than one that trusts its Specs. Folding the decision into real code at the tail of the session was rejected because a throwaway branch that merges is not throwaway, and the fold is real work that deserves a Spec. Writing the Spec inside the worktree was rejected because it would be deleted along with it.

## Consequences

- The demo is gone once the Spec is written. A designer who wants to click through the variants again next month cannot, which is what makes the question-and-verdict requirement on the Spec load-bearing rather than decorative.
- A session that hands the prototype over and gets no verdict commits the prototype and stops, leaving the worktree and branch in place. Re-entry finds the run by its `prototype/<slug>` branch and resets nothing — `/implement`'s `git reset --hard && git clean -fd` resume would destroy the prototype it came back for.
- A `/prototype` invoked from a session already inside a worktree serves that larger effort: it returns its verdict, writes no Spec, and removes nothing, so one effort never produces two Specs.
- A verdict that kills the idea ends with no Spec. The session reports what was learned, cleans up the same way, and writes an ADR only where the three-part test passes.
- The worktree levers are host-shaped exactly as [ADR-0015](0015-implement-worktree-host-agnostic.md) sets them, and the fallback path is `.agents/worktrees/prototype/<slug>`. A fresh worktree carries no installed dependencies, so a UI prototype installs the project's before rule 2's one command works.
