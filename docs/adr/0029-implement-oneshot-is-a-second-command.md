# `/implement-oneshot` is a second command

`/implement` slices a Spec into Steps so a large change fits one Driving session. Some Specs fit one agent context, and forcing a Planner onto them is ceremony. We added `/implement-oneshot` as its own user-invoked skill: one Oneshot agent implements the whole Spec, then the Driving session runs the same review, improve, document, and land sequence. `/implement` is unchanged.

A flag on `/implement` was rejected: only the human can tell whether this Spec fits one session, and a flag hides that choice inside a command that already means "slice and run". Replacing `/implement` was rejected: the Planner path has ADRs behind it and is how a large Spec still lands inside one session.

## Consequences

- Other skills do not start `/implement-oneshot`.
- Both commands share the worktree and branch named `<slug>`. `/implement-oneshot` stops when Step files are present. `/implement` does not learn about a oneshot run; a leftover oneshot worktree fails worktree add the way any duplicate already does.
- The Oneshot agent is Spec-bound and uses the same model pin as the Step agent ([ADR-0007](0007-pinned-subagent-model-tiers.md)). Leftover gaps, local-only runs, and green-against-master apply as they do to `/implement` ([ADR-0024](0024-implement-agents-close-leftover-gaps.md), [ADR-0026](0026-implement-never-leaves-the-repository.md), [ADR-0027](0027-green-is-measured-against-master.md)).
