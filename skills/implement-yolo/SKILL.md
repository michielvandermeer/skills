---
name: implement-yolo
description: "Implement a spec as a single step in this checkout, on a branch of its own that takes your uncommitted files along. No worktree."
argument-hint: "Which spec, issue, or idea to implement?"
disable-model-invocation: true
---

You are the **driving session**: you orchestrate, sub-agents implement. You hold the Step agent's and the Checker's three-line reports, any deviations, and the review findings for as long as step 4 takes to hand them on. Hand paths; the sub-agent that needs a document reads it. While a sub-agent runs, waiting is the work.

This is `/implement` with one Step, no Planner, and no worktree ([ADR-0054](../../docs/adr/0054-the-implement-commands-differ-only-in-planning-and-worktree.md)): you write that Step's file yourself, and the same `skills:implementer` and `skills:checker` run it in this checkout, on the run's own branch. Both run on your model at reduced effort because the Spec was decided before they started. The Spec fixer, the Standards fixer, and the data-structures pass are `general-purpose` and run at your own model and effort — they carry judgement worth paying for. See [ADR-0049](../../docs/adr/0049-spec-bound-agents-keep-the-session-model.md) and [ADR-0042](../../docs/adr/0042-implement-yolo-is-a-third-command.md).

Every sub-agent closes leftover gaps from the documents it was handed and the code. See [ADR-0026](../../docs/adr/0026-implement-agents-close-leftover-gaps.md).

The run never leaves a local checkout: nothing pushes, publishes, or changes a live system, and work that needs that **halts**. A Spec on a GitHub issue is the one exception: the run pushes its branch and opens its pull request ([PULL-REQUEST.md](../implement/PULL-REQUEST.md)). See [ADR-0028](../../docs/adr/0028-an-implement-run-leaves-the-repository-only-for-its-pull-request.md).

## Process

### 1. Branch in this checkout

Derive `<slug>`: the spec's filename without its extension when the argument names one, otherwise a kebab-case slug from the argument.

An argument that is a **GitHub issue** — a link, or a bare number for this checkout's own repository — holds its Spec in the issue body: read [PULL-REQUEST.md](../implement/PULL-REQUEST.md) now. Its Start runs first and settles `<slug>`, the Spec path, `<base>`, and `<branch>` for the rest of this step, and its land replaces step 6's land. Otherwise `<branch>` is `<slug>`.

A Spec carrying `Blocked by: <spec-slug>` waits on that Spec: while `.agents/specs/<spec-slug>.md` exists in this checkout, stop before anything else and say that Spec lands first ([ADR-0047](../../docs/adr/0047-a-wayfinder-map-ends-in-one-or-more-specs.md)).

In a repo with a `CONTEXT-MAP.md`, every `.agents/<kind>/` path in this skill gains a context subfolder — follow [domain-modeling/CONTEXT-PATHS.md](../domain-modeling/CONTEXT-PATHS.md).

If `git branch --show-current` is empty, **halt** — HEAD is detached. Otherwise it is the branch the session started on, unless it is `<branch>` itself: then this is a resume, and the branch the session started on is `<branch>`'s upstream (`git rev-parse --abbrev-ref <branch>@{upstream}`). For a Spec in the repo, the branch the session started on is `<base>`, the **base branch** the run lands back on ([ADR-0055](../../docs/adr/0055-a-run-lands-on-the-branch-it-started-from-or-opens-a-pull-request.md)).

The session directory is this checkout. Work at the git root (`git rev-parse --show-toplevel`). On a host whose shell starts every command in the original directory, resolve that root once, then begin every command with `cd <that path> &&` (or `git -C <that path>`), scope every search to it, and carry it into every sub-agent prompt as the only directory the agent works in. A host tool that creates a worktree is not this step.

Find linked worktrees with `git worktree list` (or the host's equivalent):

- **In a linked worktree** → a linked worktree contains `.agents/steps/<slug>/` or is on `<branch>`: stop and say that run is in flight there.
- **On its branch** → `<branch>` exists in this checkout: switch to it when it is not checked out. When `.agents/steps/<slug>/` holds Step files, resume at the lowest-numbered Step whose `Status:` is not `done` — at its Checker when it reads `built`, at its Step agent when it reads `pending` — or at step 4 when every Step reads `done`. Step files a Planner wrote resume the same way. `<start>` is then the parent of the commit that added those Step files. Without Step files, continue at step 2.
- **Fresh** → neither: create `<branch>` and switch to it. For a Spec in the repo it starts at the commit you are on; for a GitHub issue, where PULL-REQUEST.md's Start puts it. Continue at step 2.

Every switch to `<branch>` carries the tree as it is; git refusing to carry it **halts**. Whenever this step moves the session onto `<branch>`, set `<branch>`'s upstream to the branch the session started on (`git branch -u <that branch> <branch>`), so a resume on `<branch>` reads it back. A dirty tree is the working copy, and the tree as it is is the resume.

Record `<start>` on `<branch>`, unless a resume set it above: `git rev-parse HEAD`. Commits this run adds are `git log <start>..HEAD`. `/code-review` uses `<start>` as the fixed point, and Green is measured against it.

### 2. Write the Step file

Write `.agents/steps/<slug>/01-<slug>.md` and commit it as `plan: <slug>`:

```markdown
# 01 — <slug>

Status: pending
Depends on: none

## What to build

All of <the spec path, or the argument text when that is all there is>. This Step has no Footprint: its projects are the whole suite.
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

The Spec fixer goes first because a Spec fix can remove code that a Standards finding points at. For both fixers, where a finding and the Spec disagree, the Spec wins and the finding is left, named on the deviations line. When an axis reports no finding, skip its fixer and tell the user so. Retry-then-halt is the whole check on a fixer's work.

Each leaves the projects it touched green and commits its own work. A schema, migration, or ADR change any of the three makes goes to the user as a deviations line before you continue.

### 5. Document the change

Run `/document-changes` in **implement mode** while the Spec and the Step's Outcome are still on disk — after review/improve, before delete and land. Name `<start>` as the fixed point. It prepends product-facing **Changelog** entries beside each affected context's `CONTEXT.md` and commits when it wrote; when nothing is product-visible it reports that and leaves the tree clean.

### 6. Clean up and land

For a Spec on a GitHub issue, this step is [In place of the land](../implement/PULL-REQUEST.md#in-place-of-the-land).

Hold `grep -h '^Safety fact:' .agents/steps/<slug>/*.md` for the final report, then delete the Spec, the whole `.agents/steps/<slug>/` directory, the Proof folder, and the Idea or Issue document the Spec came from — unless the Spec says that document outlives it, in which case leave it and say so in the final report. Repoint or remove links to the deleted files from other `.agents/` documents. Remove every `Blocked by: <spec-slug>` line in another Spec that names the deleted Spec — it has landed. The Prototype folder the Spec points at stays ([ADR-0018](../../docs/adr/0018-prototypes-live-under-agents-prototypes.md)). Commit anything still uncommitted; `git rebase` refuses a dirty tree.

Then land `<branch>` on `<base>`:

1. On `<branch>`: `git rebase <base>`. A conflict is `/resolving-merge-conflicts`, and a `CHANGELOG.md` conflict is always keep both, this run's entry above. When the rebase replayed the branch onto commits `<base>` gained during the run, green is not known any more: build and run the whole suite before going on, with the flaky re-run and the one fixer of [`/implement-oneshot`'s land](../implement-oneshot/SKILL.md#6-land-the-branch).
2. `git switch <base>`, then `git merge --ff-only <branch>`. When the merge errors, `<base>` moved: switch back to `<branch>`, rebase again under 1, and retry.
3. `git branch -d <branch>`.

This step is done when `<base>` holds the run's commits, `<branch>` is gone, and `git status` is clean.

The final report carries the `Safety fact:` line. When the rebase replayed the branch onto new commits, it says the Proof predates the rebase; it is not re-run.

### 7. Retrospective

Run `/retro`.

## Work in another repository

The review diff, the cleanup, and the land cover this repository only. Work a Spec puts in another repository goes on a branch named `<slug>` there, committed by the Step agent and never pushed; the final report names the repository, the branch, and what sits on it.

## Halting

A halt is non-destructive and it is the end of the session. Leave the Spec, the Step file, the Proof folder, and this checkout on `<branch>` exactly as they are — committed work is the resume. Report why it did not finish. Quote a test or environment failure. For a result that was not the report, say the agent did not finish.

Re-invoking `/implement-yolo` with the same argument picks the run back up.
