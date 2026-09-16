# `/implement` worktrees are host-agnostic

`/implement` used to name Claude Code's `EnterWorktree` / `ExitWorktree` tools and the default root `.claude/worktrees/<slug>/`. Those exist on one host only, so agents on other hosts could not follow the skill. The skill now states outcomes: one shared worktree for the run, session working directory inside it, land returns to the original directory with the branch kept, then fast-forward and remove.

When no host enter-tool applies, the create path is `.agents/worktrees/<slug>/` — under the agents tree, not a product-specific directory. A host tool that both creates the worktree *and* moves the session into it still wins, even when its root differs; resume does not depend on that choice. A run is in flight when any linked git worktree contains `.agents/steps/<slug>/` (`git worktree list` or the host equivalent), so discovery is by step content rather than a hardcoded product path.

Hardcoding the Claude tools and path was rejected because it couples a portable process to one product. Forcing every host through `.agents/worktrees/` even when a native enter-tool cannot place there was rejected so hosts with a full enter-tool keep using it. Dual-path resume that named `.claude/worktrees/` explicitly was rejected as sediment of the old coupling.

## Consequences

- Fresh manual creates ensure the consuming repo ignores `.agents/worktrees/` before `git worktree add` (prefer a local ignore when the repo uses one). Host-owned roots stay the host's concern.
- Land still orders rebase → return to the original directory keeping the branch → fast-forward merge → `git worktree remove` and branch delete; only the enter/leave levers are host-shaped.
- The **Worktree waived** branch is unchanged in behaviour.
