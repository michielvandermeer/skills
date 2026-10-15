---
extends: feature, bug-fix, refactoring, perf-issue, visual-parity
when: An /implement run builds a Spec to landing with no person in the loop.
---

# Implement overlay

`scripts/open-todo.mjs` applies these changes to whichever bundled playbook the Spec routed to, after the consuming repo's own `.agents/playbooks/`. Each change anchors on the bundled step's own words and points at the `/implement` section that holds the rule, so no rule lives here. The three gates are items `open-todo.mjs` adds on every route, after the playbook's steps. `check-playbooks.mjs` proves every anchor before the run starts.

- **Before** "1. `how` over the affected subsystem." Decide the design-skip rule (`/implement` step 3) for this step and the `architect` step.
- **In** "Give every file-writing delegate its own worktree" The run worktree is the only worktree, and writers go one at a time (`/implement` step 5, One writer).
- **In** "Parallelize across worktrees, one owner per component" The run worktree is the only worktree, and writers go one at a time (`/implement` step 5, One writer).
- **In** "Reproduce it yourself on the matching surface" The red output goes where the Design gate reads it (`/implement` step 6); a symptom that never goes red is a halt (`/implement`, Halts and flags).
- **In** "Ask the user only with a stated, specific reason the control surface cannot reach the target, and only after driving it as far as it goes." Nobody is there to ask: that reason is a halt reason (`/implement`, Halts and flags).
- **In** "If the baseline looks wrong, stop and ask, don't edit it." The stop is a halt (`/implement`, Halts and flags).
- **In** "Stack follow-ups." A follow-up is a new Tracker Issue (`/implement` step 5, Follow-ups).
- **Replace** "Rebase into small, ordered commits." Units already commit in order with `Unit:` trailers, and the landing folds them (`/implement` step 5, Unit commits).
- **Replace** "Rebase into small ordered commits." Units already commit in order with `Unit:` trailers, and the landing folds them (`/implement` step 5, Unit commits).
- **Replace** "If the design is contested, `interrogate` before shipping." `interrogate` runs on every run, in the Review gate (`/implement` step 6).
- **Replace** "Cite the measurement in the PR." Cite the baseline and post-fix numbers in the landing commit's body (LANDING.md, The landing commit).
- **Replace** "Run **Opening a PR**" No pull request is opened: the gates below, then LANDING.md, one landing for the run
- **Replace** "per component or per safe batch" and every component
