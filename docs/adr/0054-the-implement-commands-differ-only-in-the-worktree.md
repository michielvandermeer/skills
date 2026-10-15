# The implement commands differ only in the worktree

`/implement` and `/implement-yolo` run one flow: the poteto-mode playbook the Spec routes to, with the implement Overlay applied, then the verification and review gates, then the landing ([ADR-0069](0069-an-implement-run-is-a-poteto-mode-playbook.md)). `/implement-yolo` waives the worktree and the run branch, and folds the run into one commit on the branch it started on. Its `SKILL.md` names only that difference and runs `/implement`'s file for everything else, so the flow has one body ([ADR-0042](0042-implement-yolo-is-a-second-command.md)).

`/implement-oneshot` is gone. Its one difference was skipping the Planner, and a poteto-mode run has no Planner to skip: the throughput checkpoint decides whether one delegate or several build the change. What the oneshot bought, no design fan-out for a Spec that already fixes the shape, is the Overlay's design-skip rule: `how` and `architect` are skipped with a reason when the Spec's Implementation Decisions name the data shape and the change touches one or two files.

## Considered Options

- **Keeping `/implement-oneshot` as an alias of `/implement`.** Rejected: a third description on every turn for a command that would do exactly what `/implement` does, and a `/goal` that names it keeps working only until the alias drifts. Goals that name it move to `/implement`.
- **A flag that turns design off.** Rejected: whether the Spec fixes the shape is readable from the Spec, so the run decides it and logs the decision; a flag would ask the human for a fact the Spec already states.
- **A full skill body for `/implement-yolo`.** Rejected: a fix to a shared rule reached two of three sibling bodies and missed the third once already.

## Consequences

- An edit to the flow is one edit, in `skills/implement/`. `/implement-yolo`'s file changes only when the waived path changes.
- Both commands resume from the same Run directory shape, so a run one started the other can finish, apart from the worktree.
- Benchmark mode exists only in `/implement` ([ADR-0066](0066-a-benchmark-run-writes-nothing-outside-its-checkout.md)).
