---
extends: feature, bug-fix, refactoring, perf-issue, visual-parity
when: An /implement run builds a Spec to landing with no person in the loop.
---

# Implement overlay

`scripts/open-todo.mjs` applies these changes to whichever bundled playbook the Spec routed to, after the consuming repo's own `.agents/playbooks/`. Each change anchors on the bundled step's own words and points at the `/implement` section that holds the rule, so no rule lives here. The three gates are items `open-todo.mjs` adds on every route, after the playbook's steps. `check-playbooks.mjs` proves every anchor before the run starts.

- **In** "`architect` for parallel design exploration." Its candidates write under the Run directory, never the worktree (`/implement` step 5, One writer).
- **In** "If it crosses a function boundary, `architect` first." Its candidates write under the Run directory, never the worktree (`/implement` step 5, One writer).
- **In** "run the **architect** skill for parallel design exploration of the shape before the move." Its candidates write under the Run directory, never the worktree (`/implement` step 5, One writer).
- **In** "delegate via the **arena** skill instead" Arena candidates write under the Run directory, and a fresh `Build:` delegate applies the graft (`/implement` step 5, One writer).
- **Replace** "**Give every file-writing delegate its own worktree** (spawn it with `isolation: \"worktree\"`, or hand it an exclusive branch), and do not write files or run a suite in a worktree a delegate still holds. On Claude Code, `isolation: \"worktree\"` branches from the remote default branch unless the `worktree.baseRef` setting is `\"head\"`. When the delegate builds on commits the default branch lacks, commit them, create its worktree with `git worktree add <path> -b <delegate-branch> HEAD`, and name that base commit in the brief." The run worktree is the only worktree, and writers go one at a time (`/implement` step 5, One writer).
- **In** "Parallelize across worktrees, one owner per component" The run worktree is the only worktree, and writers go one at a time (`/implement` step 5, One writer).
- **In** "Reproduce it yourself on the matching surface" The red output goes where the Design gate reads it (`/implement` step 6); a symptom that never goes red is a halt (`/implement`, Halts and flags).
- **In** "Ask the user only with a stated, specific reason the control surface cannot reach the target, and only after driving it as far as it goes." Nobody is there to ask: that reason is a halt reason (`/implement`, Halts and flags).
- **In** "If the baseline looks wrong, stop and ask, don't edit it." The stop is a halt (`/implement`, Halts and flags).
- **In** "Stack follow-ups." A follow-up is an item of the report, never an Issue the run files (`/implement` step 5, Follow-ups).
- **Replace** "Rebase into small, ordered commits." Units already commit in order with `Unit:` trailers, and the landing folds them (`/implement` step 5, Unit commits).
- **Replace** "Rebase into small ordered commits." Units already commit in order with `Unit:` trailers, and the landing folds them (`/implement` step 5, Unit commits).
- **Replace** "If the design is contested, `interrogate` before shipping." `interrogate` runs on every run, in the Review gate (`/implement` step 6).
- **Replace** "Cite the measurement in the PR." Cite the baseline and post-fix numbers in the landing commit's body (LANDING.md, The landing commit).
- **Replace** "Run **Opening a PR**." No pull request is opened: the gates below, then LANDING.md, one landing for the run.
- **Replace** "Run **Opening a PR** per component or per safe batch." No pull request is opened: the gates below, then LANDING.md, one landing for the run and every component.
