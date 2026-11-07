# The run folder lives at `.agents/runs/`, outside the Tracker

An implement run keeps its copy of the Spec, the Planner's Step files, and the Verifier's scratch folder at `.agents/runs/<slug>/` in the repo, whatever Tracker it uses ([ADR-0001](0001-each-repo-describes-its-tracker.md)). Nothing in it is ever an Issue.

The folder describes work already approved and in flight inside one run. It carries no status a person acts on, and a maintainer has nothing to decide about it. Filed in the Tracker, it would sit in every list of Issues that a person or `/triage` reads. On GitHub or Jira the run would also write to an external system, which [ADR-0028](0028-implement-claims-its-issue-and-pushes-only-what-lands.md) forbids.

The folder is *ephemeral* in a way Issues are not. The run commits the Spec copy and the Step files before any code, so a retry's or resume's `git reset --hard && git clean -fd` cannot delete them, and the run deletes the folder when it lands. Nothing outside the run reads it.

## Considered Options

- **Excluding the folder from the clean instead of committing the Spec copy.** Rejected: it leaves the copy at the mercy of whichever agent touches it next.
- **Running the repo's hooks on run-folder commits, and halting when one refuses.** Rejected: in a repo with a file-size hook, a Spec longer than the limit could never run. The hook guards code that lands, and these files never land.
- **Splitting the Spec copy into files under a size limit.** Rejected: every agent in the run would read the Spec a new way, for a limit meant for other files.
- **Rewriting the Spec copy from the Issue on a resume.** Rejected: the Step files were cut from the old copy, so the next Implementer would build against two different documents.

## Consequences

- `/code-review` treats `.agents/runs/` as run bookkeeping, not code under review.
- A commit that changes only the run folder skips the repo's hooks with `--no-verify`, every time: the Spec copy, the Step files, the Halt record, and the deletion before landing. None of those commits reaches the Base branch, because the landing commit holds no run folder. Every commit that carries code still runs hooks.
- A run writes its Spec copy once and never rewrites it. A changed Issue reaches no run already started. To build the change, the user deletes the run's branch and worktree and runs `/implement` again.
- The scratch folder holds a `.gitignore` of `*`, so no commit sweeps in a throwaway script or screenshot.
- On the local Tracker, a repo mid-run can hold the run folder beside a Map's Decision tickets under `.agents/`. They are told apart by directory, so anything new that scans `.agents/` must pick its root deliberately.
- A halted run leaves the folder on its branch, and `/implement` resumes from it: at the first Step not marked done, or at Review when every Step is. Nothing surfaces it to the user unprompted.
