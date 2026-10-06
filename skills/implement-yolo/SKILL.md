---
name: implement-yolo
description: "Implement a spec as a single step on this checkout and this branch. No worktree, no new branch, no merge."
argument-hint: "Which Issue to implement, or what to build?"
disable-model-invocation: true
---

You are the **driving session**: you orchestrate, sub-agents implement. You hold the Step agent's and the Checker's three-line reports, any deviations, and the review findings for as long as step 4 takes to hand them on. Hand paths; the sub-agent that needs a document reads it. While a sub-agent runs, waiting is the work.

This is `/implement` with one Step, no Planner, and no worktree ([ADR-0054](../../docs/adr/0054-the-implement-commands-differ-only-in-planning-and-worktree.md)): you write that Step's file yourself, and the same `skills:implementer` and `skills:checker` run it in this checkout. Both run on your model at reduced effort because the Spec was decided before they started, and so does the `skills:prover` that re-runs the Proof before cleanup. The Spec fixer, the Standards fixer, the data-structures pass, and the Proof fixer are `general-purpose` and run at your own model and effort — they carry judgement worth paying for. See [ADR-0049](../../docs/adr/0049-spec-bound-agents-keep-the-session-model.md) and [ADR-0042](../../docs/adr/0042-implement-yolo-is-a-third-command.md).

Every sub-agent closes leftover gaps from the documents it was handed and the code. See [ADR-0026](../../docs/adr/0026-implement-agents-close-leftover-gaps.md).

The run never leaves a local checkout: nothing pushes, publishes, or changes a live system, and work that needs that **halts**. Its one Tracker write is the **claim** on its Issue, so concurrent runs skip that Issue. The closing reference its landing commit carries is how the Tracker learns the work is done. See [ADR-0028](../../docs/adr/0028-implement-claims-its-issue-and-stays-local.md) and [ADR-0001](../../docs/adr/0001-each-repo-describes-its-tracker.md).

## Process

### 1. Stay on this checkout

Issues live in the repo's **Tracker**: carry out each operation on one — file, read, list, rewrite, set status, comment, link, claim, close — as `.agents/refs/tracker.md` says, or as [setup/LOCAL.md](../setup/LOCAL.md) says when the repo has no ref.

The argument is an Issue reference — normally an Issue in `ready-for-agent` — or a description of the change, which touches no Tracker; an issue outside this repo's Tracker is read as a description. Read the Issue. Derive `<slug>`: the Issue's run slug as the Tracker ref gives it, otherwise a kebab-case slug from the description.

If `git branch --show-current` is empty, **halt** — HEAD is detached.

An Issue blocked by another Issue waits on it: while the blocker is open, stop before anything else and say it lands first — unless this branch already holds the blocker's closing reference, found as the Tracker ref says ([ADR-0047](../../docs/adr/0047-a-wayfinder-map-ends-in-one-or-more-specs.md)).

Then claim the Issue as the Tracker ref says. When the ref says another user holds it, stop and name them. A ref that gives no claim for Issues skips this.

The session directory is this checkout, on that branch. Work at the git root (`git rev-parse --show-toplevel`). On a host whose shell starts every command in the original directory, resolve that root once, then begin every command with `cd <that path> &&` (or `git -C <that path>`), scope every search to it, and carry it into every sub-agent prompt as the only directory the agent works in. A host tool that creates a worktree is not this step.

Record `<start>`: `git rev-parse HEAD`. Commits this run adds are `git log <start>..HEAD`. `/code-review` uses `<start>` as the fixed point. Green is measured against `<start>`: this branch is the run's base branch, so its merge-base is `<start>` ([ADR-0055](../../docs/adr/0055-a-run-lands-on-the-branch-it-started-from.md)).

Find worktrees with `git worktree list` (or the host's equivalent):

- **In another worktree** → another worktree contains `.agents/steps/<slug>/` or is on branch `<slug>`, or branch `<slug>` exists and this checkout is on a different branch: stop and say that run is in flight there.
- **In this checkout** → `.agents/steps/<slug>/` holds Step files (`[0-9][0-9]-*.md`): resume at the lowest-numbered Step whose `Status:` is not `done` — at its Checker when it reads `built`, at its Step agent when it reads `pending` — or at step 4 when every Step reads `done`. Step files a Planner wrote resume the same way. `<start>` is then the parent of the commit that added those Step files.
- **Fresh** → neither: continue at step 2.

A dirty tree is the working copy, and the tree as it is is the resume.

Before leaving this step, when the argument is an Issue and `.agents/steps/<slug>/spec.md` is missing, write the Issue's title, as an H1, and its body to that file — nothing else. From here on **the Spec** is that copy: every sub-agent and `/document-changes` reads it, a resume reads it rather than the Issue, and step 2 commits it with the Step file.

### 2. Write the Step file

Write `.agents/steps/<slug>/01-<slug>.md` and commit it with the Spec as `plan: <slug>`:

```markdown
# 01 — <slug>

Status: pending
Depends on: none

## What to build

All of <the Spec's path, or the argument text when that is all there is>. This Step has no Footprint: its projects are the whole suite.
```

### 3. Run the Step

Follow `/implement`'s [step 3](../implement/SKILL.md#3-run-each-step-in-nn-order) for the Step files in `.agents/steps/<slug>/` — the one you wrote, or a Planner's that step 1 resumed — with its [PROOF.md](../implement/PROOF.md): the Step agent, its structural check, the Checker, its structural check, and the retry-then-halt rule. Read only that step of that file. When there is no Spec, the argument text stands in for it and there is no Testing Decisions section. Three things differ here:

- Green is measured against `<start>`. Tell both agents so.
- Tell both agents that `git status` is clean before they report, and that files already uncommitted may be in their commits.
- A retry never resets or cleans the tree: re-dispatch over the tree as it is.

Done when every Step file reads `Status: done`.

### 4. Review and improve

**Run `/code-review` yourself**, with `<start>` as the fixed point. Pass the Spec path, or that there is no Spec when the run started from a one-liner, and tell both axes that the Changelog is written in step 5 and that `.agents/steps/<slug>/` is run bookkeeping — its Outcome is evidence, not code under review. Hold what its two axes report, weighed on the reports alone.

Give the user a short paragraph per axis in your own words. That summary replaces the verbatim presentation `/code-review` asks its caller for. Then keep going without waiting; the run finishes unattended.

Three sub-agents follow, in this order, each reporting in the same three lines and subject to the same retry-then-halt rule, each on its own retry. Hand each the Spec path (or that there is none), the Coding standards from step 3 — they bind every line it commits, comments and tests included — and that leftover choices are theirs to close from the findings, the Spec, and the code:

1. The Spec fixer fixes every finding of the Spec axis, which you paste into its prompt as the reviewers wrote them.
2. The Standards fixer fixes every finding of the Standards axis, pasted the same way. Tell it to skip a finding whose code is gone and name that finding on its deviations line.
3. The data-structures pass runs `/improve-data-structures` and applies what it finds, or skips it.

The Spec fixer goes first because a Spec fix can remove code that a Standards finding points at. For both fixers, where a finding and the Spec disagree, the Spec wins and the finding is left, named on the deviations line. When an axis reports no finding, skip its fixer and tell the user so. Retry-then-halt, and the Prover's pass in step 6, are the whole check on a fixer's work.

Each leaves the projects it touched green and commits its own work. A schema, migration, or ADR change any of the three makes goes to the user as a deviations line before you continue.

### 5. Document the change

Run `/document-changes` in **implement mode** while the Spec and the Step's Outcome are still on disk — after review/improve, before delete. Name `<start>` as the fixed point. It prepends product-facing **Changelog** entries beside each affected context's `CONTEXT.md` and commits when it wrote; when nothing is product-visible it reports that and leaves the tree clean.

### 6. Clean up

First run `/implement`'s [Prover's pass](../implement/SKILL.md#the-provers-pass), reading only that section of that file. `<start>` stands in for `<base>`, and a retry never resets or cleans the tree, as in step 3.

Then hold `grep -h '^Safety fact:' .agents/steps/<slug>/[0-9][0-9]-*.md` for the final report, and delete the whole `.agents/steps/<slug>/` directory, the Spec with it, and the Proof folder. The Prototype folder the Spec points at stays ([ADR-0018](../../docs/adr/0018-prototypes-live-under-agents-prototypes.md)). Commit the deletion with anything still uncommitted. When the run started from an Issue, that commit is its landing commit and carries the Issue's closing reference as the Tracker ref gives it; when it gives none, the final report names the Issue for the user to close. This step is done when `git status` is clean.

The final report carries the `Safety fact:` line as this step held it, and says the Prover re-ran the Proof on the code the run leaves. It names a Proof that passed only on its re-run, or that the Proof fixer restored, updated, or retired.

### 7. Retrospective

Run `/retro`.

## Work in another repository

The review diff and the cleanup cover this repository only. Work a Spec puts in another repository goes on a branch named `<slug>` there, committed by the Step agent and never pushed; the final report names the repository, the branch, and what sits on it.

## Halting

A halt is non-destructive and it is the end of the session. Leave the Spec, the Step file, the Proof folder, and this checkout exactly as they are — committed work is the resume. Report why it did not finish. Quote a test or environment failure. For a result that was not the report, say the agent did not finish.

Re-invoking `/implement-yolo` with the same argument picks the run back up.
