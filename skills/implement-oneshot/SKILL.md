---
name: implement-oneshot
description: "Implement a spec in one sub-agent session, skipping the Planner. Still reviews and improves data structures after."
argument-hint: "Which spec, issue, or idea to implement?"
disable-model-invocation: true
---

You are the **driving session**: you orchestrate, the Oneshot agent implements. You hold one three-line report, any deviations, and the review findings for as long as step 3 takes to hand them on. Hand paths; the sub-agent that needs a document reads it. While a sub-agent runs, waiting is the work.

The Oneshot agent is `skills:oneshot` (`agents/oneshot.md` at the plugin root), pinned to a cheaper tier because the Spec was decided before it started; a host without that tier uses its cheapest model that edits code. The fixer and the data-structures pass are `general-purpose` and run at your own model and effort — they carry judgement worth paying for. See [ADR-0007](../../docs/adr/0007-pinned-subagent-model-tiers.md) and [ADR-0031](../../docs/adr/0031-implement-oneshot-is-a-second-command.md).

Every sub-agent closes leftover gaps from the documents it was handed and the code. See [ADR-0026](../../docs/adr/0026-implement-agents-close-leftover-gaps.md).

The run never leaves a local checkout: nothing pushes, publishes, or changes a live system, and work that needs that **halts**. See [ADR-0028](../../docs/adr/0028-implement-never-leaves-the-repository.md).

## Process

### 1. Enter the worktree

Derive `<slug>`: the spec's filename without its extension when the argument names one, otherwise a kebab-case slug from the argument.

`master` here and below means the repository's default branch — `main` where that is what the repo uses. The main checkout's working tree is the user's and stays as you found it until step 5.

Find linked worktrees with `git worktree list` (or the host's equivalent). Check first, because it decides which worktree you enter:

- **`/implement` in flight** → `.agents/steps/<slug>/` exists in this checkout or in any linked worktree: stop and say `/implement` is already in flight.
- **This skill in flight** → no Step files, and `git worktree list` shows a worktree on branch `<slug>`, or branch `<slug>` exists. A worktree whose lock names a live process is another session's run: stop and say so. Otherwise:
  - Put the session's working directory on that worktree's path. When the branch exists without a worktree, `git -c checkout.workers=0 worktree add` at `.agents/worktrees/<slug>` on branch `<slug>` first (ensure `.agents/worktrees/` is ignored; prefer a local ignore when the repo uses one).
  - `git reset --hard && git clean -fd` drops whatever the halted agent left uncommitted. If the host refuses the reset, `git stash push -u` and name the stash in the final report.
  - Skip to step 2.
- **Fresh** → open a worktree for this run, put the session's working directory inside it, then `git rebase master` so the run sits on the master you actually have:
  - If this host has a tool that **creates the worktree and moves the session into it**, use that tool — even when its path is not the fallback below. Decide from the tool list you already have rather than searching the host's CLI or docs. Record the branch name it chose when that name is not `<slug>`.
  - Otherwise ensure the consuming repo ignores `.agents/worktrees/` (add the line if missing; prefer a local ignore when the repo uses one), then `git -c checkout.workers=0 worktree add` at `.agents/worktrees/<slug>` on branch `<slug>`, and change the session's working directory there.

The session must work *inside* the worktree for the rest of the run — creating a worktree alone is not enough. On a host whose shell starts every command in the original directory, resolve the worktree's absolute path once with `pwd` inside it, then begin every command with `cd <that path> &&` (or `git -C <that path>`), scope every search to it, and carry it into every sub-agent prompt as the only directory the agent works in. An `/implement-oneshot` prompt that explicitly waives the worktree takes the branch in [Worktree waived](#worktree-waived) instead.

### 2. Run the Oneshot agent

Dispatch `skills:oneshot` with a prompt made of paths and section names — it reads what is behind them:

- the spec, or the argument text when that is all there is
- `CONTEXT.md` and any ADR covering the area it touches, for vocabulary
- the coding-standards sources found the same way `/code-review` finds them — `.agents/refs/` first, then a root-level coding-standards or contributing file when that is what the repo has; only documents that say how code should be written — when those exist
- the spec's Testing Decisions section when a Spec exists, which governs what it tests
- the deviations from a prior attempt, verbatim, when there are any
- the report format below
- that leftover choices are its to close from the Spec, the code, and existing patterns
- that it finds the projects to leave Green from the codebase, then greens those and the whole suite
- that Green is measured against `master` ([ADR-0029](../../docs/adr/0029-green-is-measured-against-master.md)): a failure that also fails on `master` at the merge-base goes on the deviations line and does not block landing; every other failure is red until fixed
- that a verification the repo's own conventions demand for the surface touched — a browser pass, a smoke run — counts toward green, run from the worktree
- that `CHANGELOG.md` stays untouched whatever the repo's docs rules say; step 4 writes it

Require of it: **green before it finishes**, and its code committed before it returns.

Its entire response is three lines:

```
status: done | blocked
built: <one sentence on what now works>
deviations: <what contradicts the Spec, or "none">
```

Then **check structurally** — the report reads `status: done` and `git status` is clean. That is the whole check. Step 3's review covers the rest.

Report one line to the user after the check — `Oneshot — done` — plus the deviations line when it is not `none`.

A `blocked` report, a dirty tree, or any result that is not the three-line report — a question, a progress note, a pause to wait on a background run — earns exactly one retry. When the host can resume the same agent, resume it once with one line: the work is still yours to finish; return the report. Otherwise `git reset --hard && git clean -fd`, then re-dispatch, appending a test or environment failure in its own words, or that the previous run returned something other than the report and the gap is still its to close. The failure is the Oneshot agent's to diagnose. A second failure **halts** the run.

### 3. Review and improve

**Run `/code-review` yourself**, with `master` as the fixed point. Pass the Spec path, or that there is no Spec when the run started from a one-liner, and tell both axes that the Changelog is written in step 4. Hold what its two axes report, weighed on the reports alone.

Give the user a short paragraph per axis in your own words. That summary replaces the verbatim presentation `/code-review` asks its caller for. Then keep going without waiting; the run lands unattended.

Two sub-agents follow, in this order, each reporting in the same three lines and subject to the same retry-then-halt rule. Hand each the Spec path (or that there is none) and that leftover choices are theirs to close from the findings, the Spec, and the code:

1. **Fixes every finding**, both axes, from the findings you paste into its prompt as the reviewers wrote them. Where a finding and the Spec disagree, the Spec wins and the finding is left, named on the deviations line. When neither axis reports a finding, skip this agent and say so. Retry-then-halt is the whole check on its work.
2. Runs `/improve-data-structures` and applies what it finds, or skips it.

Each leaves the projects it touched green and commits its own work. A schema, migration, or ADR change either one makes goes to the user as a deviations line before you continue.

### 4. Document the change

Run `/document-changes` in **implement mode** while the Spec is still on disk — after review/improve, before delete and land. It prepends product-facing **Changelog** entries beside each affected context's `CONTEXT.md` and commits when it wrote; when nothing is product-visible it reports that and leaves the tree clean.

### 5. Land the branch

Delete the Spec and the Idea or Issue document the Spec came from — unless the Spec says that document outlives it, in which case leave it and say so in the final report. Repoint or remove links to the deleted files from other `.agents/` documents. The Prototype folder the Spec points at stays ([ADR-0018](../../docs/adr/0018-prototypes-live-under-agents-prototypes.md)). Commit anything still uncommitted; `git rebase` refuses a dirty tree, so the branch cannot land until this is clean.

Each remaining command runs where its branch is checked out, and that constraint fixes the order. `<branch>` is `<slug>`, or the name you recorded when a host tool chose another:

1. From the worktree, still on the branch: `git rebase master`. A conflict is `/resolving-merge-conflicts` (the branch lives here, so only the worktree can rebase it).
   - A `CHANGELOG.md` conflict is always keep both, this run's entry above.
   - When the rebase replayed the branch onto commits master gained during the run, green is not known any more: build and run the whole suite before going on. A red run gets one fixer dispatch under the retry-then-halt rule, and its commit lands before the fast-forward.
2. Return the session to the original directory, keeping the branch and its commits — a host leave-worktree action when it does exactly that, otherwise change directory yourself.
3. From the original directory, on `master`: `git merge --ff-only <branch>`. (master lives here, so only the original directory can fast-forward it.) The rebase above makes this a fast-forward; if it errors, master moved during the session — re-enter the worktree, rebase again, and retry.
4. `git worktree remove <path>` — never forced; a lock means another session still has it — and `git branch -d <branch>`.

### 6. Retrospective

Run `/retro`.

## Worktree waived

There is nothing to enter, exit, or remove. Step 1 skips opening a worktree. Step 5 drops the return-to-original-directory step and `git worktree remove`: rebase on the branch, check out master yourself, fast-forward, then delete the branch. `/implement` in flight is `.agents/steps/<slug>/` in this checkout. This skill in flight is branch `<slug>` with no Step files.

## Work in another repository

The worktree, the review diff, and the land cover this repository only. Work a Spec puts in another repository goes on a branch named `<slug>` there, committed by the Oneshot agent and never pushed; the final report names the repository, the branch, and what sits on it.

## Halting

A halt is non-destructive and it is the end of the session. Leave the Spec, the branch, and the worktree exactly as they are — committed work is the resume. Report why it did not finish. Quote a test or environment failure. For a result that was not the report, say the agent did not finish.

Re-invoking `/implement-oneshot` with the same argument picks the run back up.
