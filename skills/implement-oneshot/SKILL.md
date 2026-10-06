---
name: implement-oneshot
description: "Implement a spec as a single step, skipping the Planner. Still checks, reviews, and improves data structures after."
argument-hint: "Which Issue to implement, or what to build?"
disable-model-invocation: true
---

You are the **driving session**: you orchestrate, sub-agents implement. You hold the Step agent's and the Checker's three-line reports, any deviations, and the review findings for as long as step 4 takes to hand them on. Hand paths; the sub-agent that needs a document reads it. While a sub-agent runs, waiting is the work.

This is `/implement` with one Step and no Planner ([ADR-0054](../../docs/adr/0054-the-implement-commands-differ-only-in-planning-and-worktree.md)): you write that Step's file yourself, and the same `skills:implementer` and `skills:checker` run it. Both run on your model at reduced effort because the Spec was decided before they started, and so does the `skills:prover` that re-runs the Proof before the run lands. The Spec fixer, the Standards fixer, the data-structures pass, and the Proof fixer are `general-purpose` and run at your own model and effort — they carry judgement worth paying for. See [ADR-0049](../../docs/adr/0049-spec-bound-agents-keep-the-session-model.md) and [ADR-0031](../../docs/adr/0031-implement-oneshot-is-a-second-command.md).

Every sub-agent closes leftover gaps from the documents it was handed and the code. See [ADR-0026](../../docs/adr/0026-implement-agents-close-leftover-gaps.md).

The run never leaves a local checkout: nothing pushes, publishes, or changes a live system, and work that needs that **halts**. Its one Tracker write is the **claim** on its Issue, so concurrent runs skip that Issue. The closing reference its landing commit carries is how the Tracker learns the work is done. See [ADR-0028](../../docs/adr/0028-implement-claims-its-issue-and-stays-local.md) and [ADR-0001](../../docs/adr/0001-each-repo-describes-its-tracker.md).

## Process

### 1. Enter the worktree

Issues live in the repo's **Tracker**: carry out each operation on one — file, read, list, rewrite, set status, comment, link, claim, close — as `.agents/refs/tracker.md` says, or as [setup/LOCAL.md](../setup/LOCAL.md) says when the repo has no ref.

The argument is an Issue reference — normally an Issue in `ready-for-agent` — or a description of the change, which touches no Tracker; an issue outside this repo's Tracker is read as a description. Read the Issue. Derive `<slug>`: the Issue's run slug as the Tracker ref gives it, otherwise a kebab-case slug from the description.

`<base>` is the **base branch**: `git branch --show-current` in the original directory when this command starts, read again on a resume. The run branches from it, is reviewed and measured green against it, and lands back on it ([ADR-0055](../../docs/adr/0055-a-run-lands-on-the-branch-it-started-from.md)). If it is empty, **halt** — HEAD is detached. The main checkout's working tree is the user's and stays as you found it until step 6.

An Issue blocked by another Issue waits on it: while the blocker is open, stop before anything else and say it lands first — unless `<base>` already holds the blocker's closing reference, found as the Tracker ref says ([ADR-0047](../../docs/adr/0047-a-wayfinder-map-ends-in-one-or-more-specs.md)).

Then claim the Issue as the Tracker ref says. When the ref says another user holds it, stop and name them. A ref that gives no claim for Issues skips this.

Find linked worktrees with `git worktree list` (or the host's equivalent). Check first, because it decides which worktree you enter:

- **In flight** → `git worktree list` shows a worktree on branch `<slug>`, branch `<slug>` exists, or any linked worktree contains `.agents/steps/<slug>/`. A worktree whose lock names a live process is another session's run: stop and say so. Otherwise:
  - Put the session's working directory on that worktree's path. When the branch exists without a worktree, `git -c checkout.workers=0 worktree add` at `.agents/worktrees/<slug>` on branch `<slug>` first (ensure `.agents/worktrees/` is ignored; prefer a local ignore when the repo uses one).
  - `git reset --hard && git clean -fd` drops whatever the halted agent left uncommitted. If the host refuses the reset, `git stash push -u` and name the stash in the final report.
  - When `.agents/steps/<slug>/` holds Step files (`[0-9][0-9]-*.md`), resume at the lowest-numbered Step whose `Status:` is not `done` — at its Checker when it reads `built`, at its Step agent when it reads `pending` — or at step 4 when every Step reads `done`. Step files a Planner wrote resume the same way. Otherwise continue at step 2.
- **Fresh** → open a worktree for this run, put the session's working directory inside it, then `git reset --hard <base>` so the run starts from the `<base>` you actually have — the new branch has no commits of its own yet:
  - If this host has a tool that **creates the worktree and moves the session into it**, use that tool — even when its path is not the fallback below. Decide from the tool list you already have rather than searching the host's CLI or docs. Record the branch name it chose when that name is not `<slug>`.
  - Otherwise ensure the consuming repo ignores `.agents/worktrees/` (add the line if missing; prefer a local ignore when the repo uses one), then `git -c checkout.workers=0 worktree add` at `.agents/worktrees/<slug>` on branch `<slug>`, and change the session's working directory there.

The session must work *inside* the worktree for the rest of the run — creating a worktree alone is not enough. On a host whose shell starts every command in the original directory, resolve the worktree's absolute path once with `pwd` inside it, then begin every command with `cd <that path> &&` (or `git -C <that path>`), scope every search to it, and carry it into every sub-agent prompt as the only directory the agent works in. An `/implement-oneshot` prompt that explicitly waives the worktree takes the branch in [Worktree waived](#worktree-waived) instead.

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

Follow `/implement`'s [step 3](../implement/SKILL.md#3-run-each-step-in-nn-order) for the Step files in `.agents/steps/<slug>/` — the one you wrote, or a Planner's that step 1 resumed — with its [PROOF.md](../implement/PROOF.md) and `<base>` from step 1: the Step agent, its structural check, the Checker, its structural check, and the retry-then-halt rule, unchanged. Read only that step of that file. When there is no Spec, the argument text stands in for it and there is no Testing Decisions section.

Done when every Step file reads `Status: done`.

### 4. Review and improve

**Run `/code-review` yourself**, with `<base>` as the fixed point. Pass the Spec path, or that there is no Spec when the run started from a one-liner, and tell both axes that the Changelog is written in step 5 and that `.agents/steps/<slug>/` is run bookkeeping — its Outcome is evidence, not code under review. Hold what its two axes report, weighed on the reports alone.

Give the user a short paragraph per axis in your own words. That summary replaces the verbatim presentation `/code-review` asks its caller for. Then keep going without waiting; the run lands unattended.

Three sub-agents follow, in this order, each reporting in the same three lines and subject to the same retry-then-halt rule, each on its own retry. Hand each the Spec path (or that there is none), the Coding standards from step 3 — they bind every line it commits, comments and tests included — and that leftover choices are theirs to close from the findings, the Spec, and the code:

1. The Spec fixer fixes every finding of the Spec axis, which you paste into its prompt as the reviewers wrote them.
2. The Standards fixer fixes every finding of the Standards axis, pasted the same way. Tell it to skip a finding whose code is gone and name that finding on its deviations line.
3. The data-structures pass runs `/improve-data-structures` and applies what it finds, or skips it.

The Spec fixer goes first because a Spec fix can remove code that a Standards finding points at. For both fixers, where a finding and the Spec disagree, the Spec wins and the finding is left, named on the deviations line. When an axis reports no finding, skip its fixer and tell the user so. Retry-then-halt, and the Prover's pass in step 6, are the whole check on a fixer's work.

Each leaves the projects it touched green and commits its own work. A schema, migration, or ADR change any of the three makes goes to the user as a deviations line before you continue.

### 5. Document the change

Run `/document-changes` in **implement mode** while the Spec and the Step's Outcome are still on disk — after review/improve, before delete and land. It prepends product-facing **Changelog** entries beside each affected context's `CONTEXT.md` and commits when it wrote; when nothing is product-visible it reports that and leaves the tree clean.

### 6. Land the branch

Commit anything still uncommitted; `git rebase` refuses a dirty tree. Each remaining command runs where its branch is checked out, and that constraint fixes the order. `<branch>` is `<slug>`, or the name you recorded when a host tool chose another:

1. From the worktree, still on the branch: `git rebase <base>`. A conflict is `/resolving-merge-conflicts` (the branch lives here, so only the worktree can rebase it).
   - A `CHANGELOG.md` conflict is always keep both, this run's entry above.
   - When the rebase replayed the branch onto commits `<base>` gained during the run, green is not known any more: build and run the whole suite before going on. Before any fixer dispatch, re-run each failing project once, yourself. A failure that passes on the re-run is a flaky test and does not block landing: its test name goes on the deviations line and into the final report, the same way a failure `<base>` already has does under [ADR-0029](../../docs/adr/0029-green-is-measured-against-the-base-branch.md). A failure that fails again is red and gets one fixer dispatch under the retry-then-halt rule, and its commit lands before the fast-forward ([ADR-0046](../../docs/adr/0046-a-flaky-post-rebase-failure-is-not-a-fixer-dispatch.md)).
2. Still in the worktree: run `/implement`'s [Prover's pass](../implement/SKILL.md#the-provers-pass). Read only that section of that file.
3. Still in the worktree: hold `grep -h '^Safety fact:' .agents/steps/<slug>/[0-9][0-9]-*.md` for the final report, then delete the whole `.agents/steps/<slug>/` directory and the Spec with it, and commit the deletion. The Prototype folder the Spec points at stays ([ADR-0018](../../docs/adr/0018-prototypes-live-under-agents-prototypes.md)). When the run started from an Issue, that commit is its landing commit and carries the Issue's closing reference as the Tracker ref gives it; when it gives none, the final report names the Issue for the user to close.
4. Return the session to the original directory, keeping the branch and its commits — a host leave-worktree action when it does exactly that, otherwise change directory yourself.
5. From the original directory, on `<base>`: `git merge --ff-only <branch>`. (`<base>` lives here, so only the original directory can fast-forward it.) The rebase above makes this a fast-forward. This step is done when that merge has succeeded, `git worktree remove <path>` has run — never forced; a lock means another session still has it — `git branch -d <branch>` has run, and the Proof folder is deleted. When the merge errors, `<base>` moved: re-enter the worktree, drop the landing commit with `git reset --hard HEAD~1` — it holds only the deletion, so the Step file comes back for the Prover — then go through 1 to 4 again and retry this merge.

The final report carries the `Safety fact:` line as step 3 held it, and says the Prover re-ran the Proof on the code that lands. It names a Proof that passed only on its re-run, or that the Proof fixer restored, updated, or retired.

### 7. Retrospective

Run `/retro`.

## Worktree waived

There is nothing to enter, exit, or remove. Step 1 skips opening a worktree. Step 6 drops the return-to-original-directory step and `git worktree remove`: rebase on the branch, run the Prover's pass and make the landing commit there, check out `<base>` yourself, then fast-forward. That merge is done when it succeeds, `git branch -d` has run, and the Proof folder is deleted. When it errors, `<base>` moved: check out the branch, drop the landing commit as step 6 says, go through items 1 to 3 of step 6 again, check out `<base>` yourself, and retry the merge. A run in flight is branch `<slug>`, or `.agents/steps/<slug>/` in this checkout.

## Work in another repository

The worktree, the review diff, and the land cover this repository only. Work a Spec puts in another repository goes on a branch named `<slug>` there, committed by the Step agent and never pushed; the final report names the repository, the branch, and what sits on it.

## Halting

A halt is non-destructive and it is the end of the session. Leave the Spec, the Step file, the Proof folder, the branch, and the worktree exactly as they are — committed work is the resume. Report why it did not finish. Quote a test or environment failure. For a result that was not the report, say the agent did not finish.

Re-invoking `/implement-oneshot` with the same argument picks the run back up.
