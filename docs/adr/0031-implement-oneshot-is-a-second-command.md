# `/implement-oneshot` is a second command

`/implement` slices a Spec into Steps so a large change fits one Driving session. Some Specs fit one agent context, and forcing a Planner onto them is ceremony. `/implement-oneshot` is its own user-invoked skill. Its Driving session writes one Step file for the whole Spec, and the same Step agent and Checker run that Step. It then runs the same review, improve, document and land sequence. It differs from `/implement` only in skipping the Planner ([ADR-0054](0054-the-implement-commands-differ-only-in-planning-and-worktree.md)).

A flag on `/implement` was rejected: only the human can tell whether this Spec fits one session, and a flag hides that choice inside a command that already means "slice and run". Replacing `/implement` was rejected: the Planner path has ADRs behind it and is how a large Spec still lands inside one session.

## Consequences

- Other skills do not start `/implement-oneshot`.
- Both commands share the worktree and branch named `<slug>` and the Step files in `.agents/steps/<slug>/`, so either command resumes a run the other started.
- The Step agent and Checker run on the session's model at reduced effort ([ADR-0049](0049-spec-bound-agents-keep-the-session-model.md)). Leftover gaps, local-only runs, and green against the base branch apply as they do to `/implement` ([ADR-0026](0026-implement-agents-close-leftover-gaps.md), [ADR-0028](0028-implement-claims-its-issue-and-stays-local.md), [ADR-0029](0029-green-is-measured-against-the-base-branch.md)).
