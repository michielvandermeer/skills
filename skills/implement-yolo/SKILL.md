---
name: implement-yolo
description: "Implement a spec in one sub-agent session on this checkout and this branch. No worktree, no new branch, no merge onto master."
argument-hint: "Which spec, issue, or idea to implement?"
disable-model-invocation: true
---

You are the **driving session**: you orchestrate, the Oneshot agent implements. You hold one three-line report, any deviations, and the review findings for as long as step 3 takes to hand them on. Hand paths; the sub-agent that needs a document reads it. While a sub-agent runs, waiting is the work.

The Oneshot agent is `skills:oneshot` (`agents/oneshot.md` at the plugin root), which runs on your model at reduced effort because the Spec was decided before it started. The fixer and the data-structures pass are `general-purpose` and run at your own model and effort — they carry judgement worth paying for. See [ADR-0049](../../docs/adr/0049-spec-bound-agents-keep-the-session-model.md) and [ADR-0042](../../docs/adr/0042-implement-yolo-is-a-third-command.md).

Every sub-agent closes leftover gaps from the documents it was handed and the code. See [ADR-0026](../../docs/adr/0026-implement-agents-close-leftover-gaps.md).

The run never leaves a local checkout: nothing pushes, publishes, or changes a live system, and work that needs that **halts**. See [ADR-0028](../../docs/adr/0028-implement-never-leaves-the-repository.md).

## Process

### 1. Stay on this checkout

Derive `<slug>`: the spec's filename without its extension when the argument names one, otherwise a kebab-case slug from the argument.

A Spec carrying `Blocked by: <spec-slug>` waits on that Spec: while `.agents/specs/<spec-slug>.md` exists in this checkout, stop before anything else and say that Spec lands first ([ADR-0047](../../docs/adr/0047-a-wayfinder-map-ends-in-one-or-more-specs.md)).

`master` here and below means the repository's default branch — `main` where that is what the repo uses.

If `git branch --show-current` is empty, **halt** — HEAD is detached.

The session directory is this checkout, on that branch. Work at the git root (`git rev-parse --show-toplevel`). On a host whose shell starts every command in the original directory, resolve that root once, then begin every command with `cd <that path> &&` (or `git -C <that path>`), scope every search to it, and carry it into every sub-agent prompt as the only directory the agent works in. A host tool that creates a worktree is not this step.

Record `<start>`: `git rev-parse HEAD`. Commits this run adds are `git log <start>..HEAD`. `/code-review` uses `<start>` as the fixed point. Green is measured against `master` at the merge-base; when the current branch *is* `master`, that merge-base is `<start>`.

Find linked worktrees with `git worktree list` (or the host's equivalent):

- **`/implement` in flight** → `.agents/steps/<slug>/` exists in this checkout or in any linked worktree: stop and say `/implement` is already in flight.
- **`/implement-oneshot` in flight** → no Step files, and `git worktree list` shows a worktree on branch `<slug>`, or branch `<slug>` exists: stop and say `/implement-oneshot` is already in flight.

A dirty tree is the working copy. Re-invoking with the same argument resumes at step 2; the tree as it is is the resume.

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
- that Green is measured against `master` ([ADR-0029](../../docs/adr/0029-green-is-measured-against-master.md)): a failure that also fails on `master` at the merge-base goes on the deviations line and does not block finishing; when the current branch is `master`, that merge-base is `<start>`; every other failure is red until fixed
- that a verification the repo's own conventions demand for the surface touched — a browser pass, a smoke run — counts toward green, run from this checkout
- that `CHANGELOG.md` stays untouched whatever the repo's docs rules say; step 4 writes it
- that `git status` is clean before it reports; files that were already uncommitted may be in its commits

Require of it: **green before it finishes**, and its code committed before it returns.

Its entire response is three lines:

```
status: done | blocked
built: <one sentence on what now works>
deviations: <what contradicts the Spec, or "none">
```

Then **check structurally** — the report reads `status: done` and `git status` is clean. That is the whole check. Step 3's review covers the rest.

Report one line to the user after the check — `Oneshot — done` — plus the deviations line when it is not `none`.

A `blocked` report, a dirty tree, or any result that is not the three-line report — a question, a progress note, a pause to wait on a background run — earns exactly one retry. When the host can resume the same agent, resume it once with one line: the work is still yours to finish; return the report. Otherwise re-dispatch, appending a test or environment failure in its own words, or that the previous run returned something other than the report and the gap is still its to close. The tree as it is is the resume. The failure is the Oneshot agent's to diagnose. A second failure **halts** the run.

### 3. Review and improve

**Run `/code-review` yourself**, with `<start>` as the fixed point. Pass the Spec path, or that there is no Spec when the run started from a one-liner, and tell both axes that the Changelog is written in step 4. Hold what its two axes report, weighed on the reports alone.

Give the user a short paragraph per axis in your own words. That summary replaces the verbatim presentation `/code-review` asks its caller for. Then keep going without waiting; the run finishes unattended.

Two sub-agents follow, in this order, each reporting in the same three lines and subject to the same retry-then-halt rule. Hand each the Spec path (or that there is none) and that leftover choices are theirs to close from the findings, the Spec, and the code:

1. **Fixes every finding**, both axes, from the findings you paste into its prompt as the reviewers wrote them. Where a finding and the Spec disagree, the Spec wins and the finding is left, named on the deviations line. When neither axis reports a finding, skip this agent and say so. Retry-then-halt is the whole check on its work.
2. Runs `/improve-data-structures` and applies what it finds, or skips it.

Each leaves the projects it touched green and commits its own work. A schema, migration, or ADR change either one makes goes to the user as a deviations line before you continue.

### 4. Document the change

Run `/document-changes` in **implement mode** while the Spec is still on disk — after review/improve, before delete. Name `<start>` as the fixed point. It prepends product-facing **Changelog** entries beside each affected context's `CONTEXT.md` and commits when it wrote; when nothing is product-visible it reports that and leaves the tree clean.

### 5. Clean up

Delete the Spec and the Idea or Issue document the Spec came from — unless the Spec says that document outlives it, in which case leave it and say so in the final report. Repoint or remove links to the deleted files from other `.agents/` documents. The Prototype folder the Spec points at stays ([ADR-0018](../../docs/adr/0018-prototypes-live-under-agents-prototypes.md)). Commit anything still uncommitted. This step is done when `git status` is clean.

### 6. Retrospective

Run `/retro`.

## Work in another repository

The review diff and the cleanup cover this repository only. Work a Spec puts in another repository goes on a branch named `<slug>` there, committed by the Oneshot agent and never pushed; the final report names the repository, the branch, and what sits on it.

## Halting

A halt is non-destructive and it is the end of the session. Leave the Spec and this checkout exactly as they are — committed work is the resume. Report why it did not finish. Quote a test or environment failure. For a result that was not the report, say the agent did not finish.

Re-invoking `/implement-yolo` with the same argument picks the run back up.
