# Steps live at `.agents/steps/`, outside the Tracker

`/implement` splits a Spec into **Steps**, tracer-bullet slices executed one per sub-agent. Steps are numbered Markdown files at `.agents/steps/<slug>/<NN>-<slug>.md`, in the repo, whatever Tracker it uses ([ADR-0001](0001-each-repo-describes-its-tracker.md)). They are never Issues.

The trade-off is between one location and one meaning. Steps describe work already approved and in flight inside one run. They carry no status a person acts on, and a maintainer has nothing to decide about them. Filed in the Tracker, they would sit in every list of Issues that a person or `/triage` reads, and each would need a marker saying "not for you". On GitHub or Jira the run would also write to an external system, which [ADR-0028](0028-implement-claims-its-issue-and-pushes-only-what-lands.md) forbids.

Steps are also *ephemeral* in a way Issues are not. They are created inside the run's working tree. The Planner commits them in one commit before any Step's code ([ADR-0030](0030-planner-commits-the-step-files.md)), so a retry cannot delete them, and the run deletes the folder when it lands. Nothing outside the run ever reads them.

## Consequences

- The Step folder also holds the run's copy of its Spec, which is deleted with the Steps.
- On the local Tracker, a repo mid-`/implement` can hold two numbered-Markdown trees under `.agents/`: Steps, and a Map's Decision tickets. They are distinguished by directory, not by content shape, so anything new that scans `.agents/` must pick its root deliberately.
- `.agents/steps/` is not scanned by any skill. A halted run leaves Steps behind on its branch. `/implement`, `/implement-oneshot`, and `/implement-yolo` resume them, including Step files another of those commands wrote, because only the planning differs ([ADR-0054](0054-the-implement-commands-differ-only-in-planning-and-worktree.md)). Nothing surfaces them to the user unprompted.
- Steps are in-flight execution state, not a second tracker.
