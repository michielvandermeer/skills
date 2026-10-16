---
name: implement-yolo
description: "Implement a spec on this checkout and this branch, in a loop of implement, review, and verify. No worktree, no new branch, no merge. Use only when the user or a /goal names /implement-yolo."
argument-hint: "Which Issue to implement, or what to build?"
model: sonnet
effort: high
---

You are the **driving session**: you orchestrate, sub-agents implement, review, and verify. You hold each sub-agent's short report, the findings that go back to the next Iteration, and any deviations. Hand paths; the sub-agent that needs a document reads it. While a sub-agent runs, waiting is the work.

This is `/implement` without a worktree ([ADR-0054](../../docs/adr/0054-the-implement-commands-differ-only-in-worktree.md)): the same loop of Implement, Review, and Verify, with the same `skills:implementer`, `/code-review`, and `skills:verifier`, run in this checkout on this branch. See [ADR-0042](../../docs/adr/0042-implement-yolo-is-a-second-command.md).

Every sub-agent closes leftover gaps from the documents it was handed and the code. See [ADR-0026](../../docs/adr/0026-implement-agents-close-leftover-gaps.md).

No sub-agent pushes, publishes, or changes a live system; work that needs that **halts**. The run reaches outside the local checkout twice: the **claim** on its Issue, so concurrent runs skip that Issue, and the push of this branch once the run has cleaned up. The closing reference its landing commit carries is how the Tracker learns the work is done. See [ADR-0028](../../docs/adr/0028-implement-claims-its-issue-and-pushes-only-what-lands.md) and [ADR-0001](../../docs/adr/0001-each-repo-describes-its-tracker.md).

## Process

### 1. Stay on this checkout

Issues live in the repo's **Tracker**: carry out each operation on one — file, read, list, rewrite, set status, comment, link, claim, close — as `.agents/refs/tracker.md` says, or as [setup/LOCAL.md](../setup/LOCAL.md) says when the repo has no ref.

The argument is an Issue reference — normally an Issue in `ready-for-agent` — or a description of the change, which touches no Tracker; an issue outside this repo's Tracker is read as a description. A description is the Spec: it gets no interview, and the user who wants one runs `/grill-with-docs` first. Read the Issue. Derive `<slug>`: the Issue's run slug as the Tracker ref gives it, otherwise a kebab-case slug from the description.

When this session already drives the run for `<slug>` and a sub-agent it dispatched for that run has not reported yet, this invocation is a repeat and the run is still going: say so, and keep waiting for that report. A repeat claims, resets, and dispatches nothing ([ADR-0064](../../docs/adr/0064-a-repeated-implement-command-waits-for-its-run.md)).

If `git branch --show-current` is empty, **halt** — HEAD is detached.

An Issue blocked by another Issue waits on it: while the blocker is open, stop before anything else and say it lands first — unless this branch already holds the blocker's closing reference, found as the Tracker ref says ([ADR-0047](../../docs/adr/0047-a-wayfinder-map-ends-in-one-or-more-specs.md)).

Then claim the Issue as the Tracker ref says. When the ref says another user holds it, stop and name them. A ref that gives no claim for Issues skips this.

The session directory is this checkout, on that branch. Work at the git root (`git rev-parse --show-toplevel`). Run every command from there as a **plain** command: every argument spelled out, and files written with the host's file tools. A host that isolates the session in its worktree refuses a command it cannot prove stays inside, such as one with a `cd` or `git -C`, a shell variable, `$(…)`, or a heredoc, and says how to split it. Scope every search to the git root, and name it in every sub-agent prompt as the only directory the agent works in. On a host whose shell starts every command in the original directory, resolve that root once and begin every command with `cd <that path> &&`. A host tool that creates a worktree is not this step.

Find worktrees with `git worktree list` (or the host's equivalent):

- **In another worktree** → another worktree contains `.agents/runs/<slug>/` or is on branch `<slug>`, or branch `<slug>` exists and this checkout is on a different branch: stop and say that run is in flight there.
- **In this checkout** → `.agents/runs/<slug>/spec.md` exists: resume at Iteration 1 of step 2. `<start>` is the parent of the commit that added that file, `git log --diff-filter=A --format=%H -- .agents/runs/<slug>/spec.md`.
- **Fresh** → neither: record `<start>` as `git rev-parse HEAD`, write **the Spec** to `.agents/runs/<slug>/spec.md` — the Issue's title as an H1 and its body, or the description as the argument gave it — and nothing else, then commit it as `spec: <slug>`. Files already uncommitted stay out of that commit.

Commits this run adds are `git log <start>..HEAD`. `/code-review` uses `<start>` as the fixed point, and the Verifier measures against `<start>`: this branch is the run's base branch, so its merge-base is `<start>` ([ADR-0055](../../docs/adr/0055-a-run-lands-on-the-branch-it-started-from.md)). A dirty tree is the working copy, and the tree as it is is the resume.

Create `<scratch>`, `.agents/runs/<slug>/scratch/`, as `/implement`'s step 1 says.

### 2. Loop

Follow `/implement`'s [step 2](../implement/SKILL.md#2-loop), reading only that step of that file: Implement, Review, and Verify, at most three Iterations, with the same reports, structural check, and retry-then-halt rule. Three things differ here:

- `<start>` stands in for `<base>` everywhere: in every prompt, and as `/code-review`'s fixed point.
- Tell the Implementer that files already uncommitted may go in its commits, and that `git status` is clean before it reports.
- A retry never resets or cleans the tree: re-dispatch over the tree as it is.

Done when an Iteration passes both Review and Verify.

### 3. Clean up

Write the landing commit's message as `/implement`'s [landing commit](../implement/SKILL.md#the-landing-commit) section says, reading only that section of that file. Delete the whole `.agents/runs/<slug>/` directory, the Spec and `<scratch>` with it. The Prototype folder the Spec points at stays ([ADR-0018](../../docs/adr/0018-prototypes-live-under-agents-prototypes.md)). Fold the run into the landing commit: `git reset --soft <start>`, `git add -A`, then commit with that message. Anything still uncommitted goes in with it. This step is done when `git status` is clean and `git rev-list --count <start>..HEAD` prints `1`.

The final report says how many Iterations the run took, quotes every `declined:` line that was not `none` and every deviations line, and names each Hand check the Verifier skipped and what it needs.

### 4. Push

Run `/implement`'s [push](../implement/SKILL.md#the-push), reading only that section of that file. `<base>` is this branch, and this checkout is the original directory.

### 5. Retrospective

Run `/retro`. When it committed and step 4's push went out, run that push again.

## Work in another repository

The review diff, the cleanup, and the push cover this repository only. Work a Spec puts in another repository goes on a branch named `<slug>` there, committed by the Implementer and never pushed; the final report names the repository, the branch, and what sits on it.

## Halting

A halt is non-destructive and it is the end of the session. Leave the Spec, `<scratch>`, and this checkout exactly as they are — committed work is the resume. Report why it did not finish: the Iteration, the part — Implement, Review, or Verify — and why. Quote a test or environment failure, and the findings an Iteration 3 left. For a result that was not the report, say the agent did not finish.

Re-invoking `/implement-yolo` with the same argument picks the run back up at Iteration 1, with three Iterations again.
