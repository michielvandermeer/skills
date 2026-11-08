# The run folder lives at `.agents/runs/`, outside the Tracker

An implement run keeps its copy of the Spec, the Planner's Step files, and the Verifier's scratch folder at `.agents/runs/<slug>/` in the repo, whatever Tracker it uses ([ADR-0001](0001-each-repo-describes-its-tracker.md)). Nothing in it is ever an Issue.

The folder describes work already approved and in flight inside one run. It carries no status a person acts on, and a maintainer has nothing to decide about it. Filed in the Tracker, it would sit in every list of Issues that a person or `/triage` reads. On GitHub or Jira the run would also write to an external system, which [ADR-0028](0028-implement-claims-its-issue-and-pushes-only-what-lands.md) forbids.

The folder is *ephemeral* in a way Issues are not. The run commits the Spec copy and the Step files before any code, so a retry's or resume's `git reset --hard && git clean -fd` cannot delete them, and the run deletes the folder when it lands. Nothing outside the run reads it.

## Considered Options

- **Excluding the folder from the clean instead of committing the Spec copy.** Rejected: it leaves the copy at the mercy of whichever agent touches it next.
- **Committing run-folder files with `git commit --no-verify`.** Rejected: it skips a repo's hooks on purpose, and the repo owner decides what a hook guards. A hook that scans for secrets matters on every commit, whether or not it lands. A repo whose hook should not judge run bookkeeping says so in the hook, by exempting `.agents/runs/`.
- **Splitting the Spec copy into files under a size limit.** Rejected: every agent in the run would read the Spec a new way, for a limit meant for other files.
- **Rewriting the Spec copy from the Issue on a resume.** Rejected: the Step files were cut from the old copy, so the next Implementer would build against two different documents.
- **Stopping a resume to ask when the Issue's body has changed.** Rejected: the run lands unattended ([ADR-0028](0028-implement-claims-its-issue-and-pushes-only-what-lands.md)), the answer is always to build the copy, and a stop that waits on a person is a halt by another name.

## Consequences

- `/code-review` treats `.agents/runs/` as run bookkeeping, not code under review.
- Every commit a run makes runs the repo's hooks, run-folder commits included: the Spec copy, the Step files, the Halt record, and the deletion before landing. No agent in a run passes `--no-verify`. A repo whose hook would refuse run bookkeeping, such as a file-size limit a long Spec breaks, exempts `.agents/runs/` in the hook itself.
- When a hook refuses a run-folder commit, the run halts and quotes the hook's output. The user exempts the folder in the hook, then runs `/implement` again.
- A run writes its Spec copy once and never rewrites it. A changed Issue reaches no run already started. A resume that finds the Issue's body different from its Spec copy says so in one line, with how to build the new text, and carries on without asking. To build the change, the user deletes the run's branch and worktree and runs `/implement` again.
- The scratch folder holds a `.gitignore` of `*`, so no commit sweeps in a throwaway script or screenshot.
- On the local Tracker, a repo mid-run can hold the run folder beside a Map's Decision tickets under `.agents/`. They are told apart by directory, so anything new that scans `.agents/` must pick its root deliberately.
- A halted run leaves the folder on its branch, and `/implement` resumes from it: at the first Step not marked done, or at Review when every Step is. Nothing surfaces it to the user unprompted.
