# `/implement` steps live at `.agents/steps/`, outside the issue tracker

[ADR-0001](0001-fixed-local-issue-tracker.md) and [ADR-0003](0003-tracker-under-agents.md) fixed a single local-markdown tracker at `.agents/issues/<slug>/<NN>-<slug>.md`, shared by `/triage` and `/wayfinder`. `/implement` now splits a Spec into **Steps** — tracer-bullet slices executed one per sub-agent — and those Steps are numbered markdown files that look exactly like tracker tickets. We put them at `.agents/steps/<spec-slug>/<NN>-<slug>.md` instead of in the tracker.

The trade-off is between one location and one meaning. `/triage` scans `.agents/issues/*/*.md` for anything needing maintainer attention, and `/wayfinder` reads the same tree for open questions. Steps are neither: they describe work already approved and currently in flight inside a worktree, they carry no `Category:`, and a maintainer has nothing to decide about them. Filing them in the tracker would put transient in-flight work in front of every future triage session, and each Step would need a marker saying "not for you" — the cost of the shared root paid on every scan, for files that live and die inside a single `/implement` run.

Steps are also *ephemeral* in a way tracker files are not. They are created inside the run's worktree, committed alongside the code of the step they describe, and deleted with the Spec when the run lands. Nothing outside the run ever reads them.

## Consequences

- A repo mid-`/implement` has two numbered-markdown trees under `.agents/`. They are distinguished by directory, not by content shape, so anything new that scans `.agents/` must pick its root deliberately.
- `.agents/steps/` is not scanned by any skill. A halted run leaves Steps behind on its branch, visible only to a resumed `/implement` — nothing surfaces them to the user unprompted.
- The "one fixed tracker" decision from ADR-0001 still holds for Issues and Tickets. This is a carve-out for in-flight execution state, not a second tracker.
