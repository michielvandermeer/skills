# `/implement` worktrees are host-agnostic

`/implement` states outcomes: one shared worktree for the run, the session's working directory inside it, and a land that returns to the original directory with the branch kept, then a successful fast-forward, then remove. A host tool is a lever for those outcomes. The skill does not name one product's tools or default path.

When no host enter-tool applies, the create path is `.agents/worktrees/<slug>/` — under the agents tree, not a product-specific directory. A host tool that both creates the worktree *and* moves the session into it still wins, even when its root differs; resume does not depend on that choice. A run is in flight when a worktree is on branch `<slug>`, branch `<slug>` exists, or any linked git worktree contains `.agents/steps/<slug>/` (`git worktree list` or the host equivalent), so discovery is by branch and step content rather than a hardcoded product path. A branch with no worktree gets one at `.agents/worktrees/<slug>/` and resumes there, since the run's Step files are committed on it.

Hardcoding one host's tools and path was rejected because it couples a portable process to one product. Forcing every host through `.agents/worktrees/` even when a native enter-tool cannot place there was rejected so hosts with a full enter-tool keep using it. Dual-path resume that named one product's worktree root explicitly was rejected as sediment of that coupling.

## Consequences

- Fresh manual creates ensure the consuming repo ignores `.agents/worktrees/` before `git worktree add` (prefer a local ignore when the repo uses one). Host-owned roots stay the host's concern.
- Land still orders rebase → return to the original directory keeping the branch → fast-forward merge; `git worktree remove` and branch delete follow a successful fast-forward. Only the enter/leave levers are host-shaped.
- The **Worktree waived** branch is unchanged in behaviour.
