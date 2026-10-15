# An implement run is a poteto-mode playbook

`/implement` and `/implement-yolo` run a Spec as the `poteto-mode` skill's lead would. The Driving session reads poteto-mode in full, routes the Spec to one bundled playbook (Feature, Bug fix, Refactoring, Perf issue, Visual parity, or the `figure-it-out` skill for work too large for one owner), copies its steps verbatim into the run's `todo.md`, and runs them under a full-autonomy grant. Delegates are `skills:poteto-agent` on the model the operator's `pstack-models.md` names for the playbook's role. What a landing needs and poteto-mode lacks, the Tracker claim, the Run directory, the Verifier, an `interrogate` that always runs, the landing on the Base branch, the push, benchmark mode, and `/retro`, is the implement **Overlay** in poteto-mode's own project-playbook grammar, proved by poteto-mode's `check-playbooks.mjs` before every run, plus the skill's own steps around the playbook. The old run had a method of its own, a Planner slicing Steps, a Checker and a Prover proving each slice up a Proof ladder, fixers after a final `/code-review`, with poteto-mode's principles at most paraphrased; a run then followed two methods, and an edit to one drifted from the other.

## Considered Options

- **Depend on the separate `pstack` plugin and route through it.** Rejected: pstack is imported into this plugin, so the playbooks and principles are in-repo, a plugin dependency would load every pstack skill twice, and the Overlay check guards the operator's own edits rather than upstream drift.
- **A `Workflow:` line per Step with a WORKFLOWS.md, keeping the Step, Checker, and Proof machinery (pull request #32).** Rejected: two methods stay alive, the principles are paraphrased and drift, and nothing new is hidden from delegates.
- **Keep the Checker and the Prover under the playbook.** Rejected: the Checker proved a slice a Planner chose, so design happened per slice; the Prover re-proved after fixers that ran unverified. Under the playbook, design happens once, every fix round gets a fresh delegate, and one Verifier that wrote no code checks the whole change on the matching surface, with LANDING.md's post-rebase re-check for a moved base.
- **A Judge per unit, each delegate in a nested worktree.** Rejected: worktrees opened inside a worktree are refused by hosts that confine a session, and a verdict per slice re-creates the Checker. One Verifier per run checks the code that lands.
- **Land the run branch's commits instead of one landing commit.** Rejected: ADR-0062 holds; the unit commits stay on the branch for the review and fold at the land.
- **An unpinned driver on the session's model.** Rejected: the driver owns the design and verification judgement, which is Opus work, and a run started by a `/goal` on a cheaper session would starve it; delegates still take their models from the sheet, so cost has one control surface ([ADR-0049](0049-agents-are-pinned-in-their-agent-files.md)).

## Consequences

- `/implement-oneshot` is deleted ([ADR-0054](0054-the-implement-commands-differ-only-in-the-worktree.md)). Its one difference was skipping the Planner, and the Planner is gone. Its job, skipping design when the Spec already fixes the shape, is the Overlay's design-skip rule.
- `todo.md` in the Run directory is the run's only todolist, read by `check-run.mjs` at the landing gate and by a resume; session task tools stay unused, against poteto-mode's default.
- The run makes no bookkeeping commit: the Run directory is ignored by git from inside, and a resume that lost it rebuilds from the Issue and the branch's `Unit:` trailers.
- `/code-review` is no longer a gate of the run; `interrogate` with the Spec as its intent judges conformance and quality at once. `/code-review` stays a skill of its own.
- A run costs more than the old one, with four `architect` runners and four `interrogate` reviewers on the default sheet; the number is unmeasured until `benchmark/` runs on both sides.
- The trail reviewer's "different model family" is unreachable on an all-Claude sheet; the report names the reviewer's model and says the families match.
