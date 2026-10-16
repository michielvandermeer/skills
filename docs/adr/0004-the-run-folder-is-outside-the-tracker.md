# The run folder lives at `.agents/runs/`, outside the Tracker

An implement run keeps its copy of the Spec, and the Verifier's scratch folder, at `.agents/runs/<slug>/` in the repo, whatever Tracker it uses ([ADR-0001](0001-each-repo-describes-its-tracker.md)). Nothing in it is ever an Issue.

The folder describes work already approved and in flight inside one run. It carries no status a person acts on, and a maintainer has nothing to decide about it. Filed in the Tracker, it would sit in every list of Issues that a person or `/triage` reads. On GitHub or Jira the run would also write to an external system, which [ADR-0028](0028-implement-claims-its-issue-and-pushes-only-what-lands.md) forbids.

The folder is *ephemeral* in a way Issues are not. The run commits the Spec copy before any code, so a retry's or resume's `git reset --hard && git clean -fd` cannot delete it, and the run deletes the folder when it lands. Nothing outside the run reads it.

## Considered Options

- **Excluding the folder from the clean instead of committing the Spec copy.** Rejected: it leaves the copy at the mercy of whichever agent touches it next.

## Consequences

- `/code-review` treats `.agents/runs/` as run bookkeeping, not code under review.
- The scratch folder holds a `.gitignore` of `*`, so no commit sweeps in a throwaway script or screenshot.
- On the local Tracker, a repo mid-run can hold the run folder beside a Map's Decision tickets under `.agents/`. They are told apart by directory, so anything new that scans `.agents/` must pick its root deliberately.
- A halted run leaves the folder on its branch, and both implement commands resume from it ([ADR-0054](0054-the-implement-commands-differ-only-in-worktree.md)). Nothing surfaces it to the user unprompted.
