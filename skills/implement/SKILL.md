---
name: implement
description: "Implement a spec by slicing it into steps and running each one in its own sub-agent."
argument-hint: "Which spec, issue, or idea to implement?"
disable-model-invocation: true
---

You are the **driving session**: you orchestrate, sub-agents implement. You hold the step index, one three-line report per step, any deviations, and the review findings for as long as step 4 takes to hand them on — that is the whole of your context, and it is what lets a spec of any size run to landed inside one session. So until step 5 you hand paths and read nothing behind them — not the Spec, not a Step file or its Outcome, not the diff, not the code — beyond step 3's structural check. The sub-agent that needs a document reads it. While a sub-agent runs there is no parent work; wait for its report.

Sub-agents share the worktree, so run them one at a time, and before every dispatch make sure no sub-agent of this run is still running. Step agents are `skills:implementer` (`agents/implementer.md` at the plugin root), pinned to a cheaper tier because their scope was decided before they started; a host without that tier uses its cheapest model that edits code. The planner, the fixer, and the data-structures pass are `general-purpose` and run at your own model and effort — they carry judgement worth paying for. See [ADR-0007](../../docs/adr/0007-pinned-subagent-model-tiers.md).

Every sub-agent closes leftover gaps from the documents it was handed and the code. See [ADR-0024](../../docs/adr/0024-implement-agents-close-leftover-gaps.md).

The run never leaves a local checkout: nothing pushes, publishes, or changes a live system, and a Step that needs that **halts**. See [ADR-0026](../../docs/adr/0026-implement-never-leaves-the-repository.md).

## Process

### 1. Enter the worktree

Derive `<slug>`: the spec's filename without its extension when the argument names one, otherwise a kebab-case slug from the argument.

`master` here and below means the repository's default branch — `main` where that is what the repo uses. The main checkout's working tree is the user's: nothing in this run pulls over it, stashes it, or checks another branch out in it before step 6.

A prior run is **in flight** when any linked git worktree contains `.agents/steps/<slug>/` — the planner got that far, so a worktree holds those steps. Find it with `git worktree list` (or the host's equivalent). Check first, because it decides which worktree you enter:

- **In flight** → a worktree whose lock names a live process is another session's run: stop and say so. Otherwise:
  - Put the session's working directory on that worktree's path.
  - `git reset --hard && git clean -fd` drops whatever the halted Step left behind; the Step files are committed, so the clean spares them. If the host refuses the reset, `git stash push -u` and name the stash in the final report.
  - The Steps are already planned: skip step 2 and resume at the lowest-numbered Step whose `Status:` is not `done`, or at step 4 when every Step reads `done`.
- **Fresh** → open a worktree for this run, put the session's working directory inside it, then `git rebase master` so the run sits on the master you actually have:
  - If this host has a tool that **creates the worktree and moves the session into it**, use that tool — even when its path is not the fallback below. Decide from the tool list you already have rather than searching the host's CLI or docs. Record the branch name it chose when that name is not `<slug>`.
  - Otherwise ensure the consuming repo ignores `.agents/worktrees/` (add the line if missing; prefer a local ignore when the repo uses one), then `git worktree add` at `.agents/worktrees/<slug>` on branch `<slug>`, and change the session's working directory there.

The session must work *inside* the worktree for the rest of the run — creating a worktree alone is not enough. On a host whose shell starts every command in the original directory, resolve the worktree's absolute path once with `pwd` inside it, then begin every command with `cd <that path> &&` (or `git -C <that path>`), scope every search to it, and carry it into every sub-agent prompt as the only directory the agent works in. A check that ran in the original directory is not a check. An `/implement` prompt that explicitly waives the worktree takes the branch in [Worktree waived](#worktree-waived) instead.

### 2. Plan the steps

Dispatch a **planner** sub-agent. Give it the spec path (or the argument text), `<slug>`, and the absolute path to [STEPS.md](STEPS.md) in this skill's directory — those three and nothing else. It reads the slicing rules itself, writes one file per Step to `.agents/steps/<slug>/`, and commits them in one commit before returning, so the resets in steps 1 and 3 cannot delete a Step not yet done ([ADR-0028](../../docs/adr/0028-planner-commits-the-step-files.md)). When `git status` still shows that directory afterwards, commit it yourself as `plan: <slug>`.

It returns the index and nothing else: one line per step, `NN | title | one-line deliverable`.

A planner that fails or returns no steps **halts** the run.

### 3. Run each step in `NN` order

Dispatch a fresh `skills:implementer` per step. Hand it paths and let it read what it needs — the prompt carries paths, section names, the Step number and count, the earlier deviations verbatim, and the report format; it restates neither the Spec nor the Step:

- the spec, and its own step file — whose `## Footprint` names the files, symbols and projects the work lands in
- an instruction to read the `## Outcome` of every lower-numbered step file before starting
- `CONTEXT.md` and any ADR covering the area it touches, for vocabulary
- the spec's Testing Decisions section, which governs what it tests
- the deviations reported by earlier steps, when there are any

Tell it how far to trust its map: its footprint is a guess — where the code disagrees, the code wins, and the drift goes in its `## Outcome` so its successors inherit the correction.

Require of it: **green before it finishes**, then its `## Outcome` appended to its Step file, that file's `Status:` set to `done`, and its code and Step file committed together in one commit.

- Green covers every project on its footprint's `Projects:` line, and the whole suite on the last Step.
- Green is zero failures in those projects, measured against `master`: a failure that also fails on `master` at the merge-base is not this run's — the agent names the test on its deviations line and finishes, and it does not block landing; a failure that passes on `master` is red until fixed ([ADR-0027](../../docs/adr/0027-green-is-measured-against-master.md)).
- A verification the repo's own conventions demand for the surface the Step touches — a browser pass, a smoke run — counts toward green and is the Step agent's, run from the worktree.
- `CHANGELOG.md` stays untouched whatever the repo's docs rules say; step 5 writes it.

Its entire response is three lines:

```
status: done | blocked
built: <one sentence on what now works>
deviations: <what contradicts the Spec or changes a later Step, or "none">
```

A fact a successor needs goes in `## Outcome`, which the successor reads itself, not on the deviations line.

Then **check the step structurally** — `grep '^Status:'` on the Step file reads `done`, and `git log -1` shows a new commit. That is the whole check; open the Step file only when it fails. Step 4's review covers the rest.

Report one line to the user after each check — `Step <NN>/<total> — <title>: done` — plus the deviations line when it is not `none`, and carry those deviations verbatim into the next dispatch.

A `blocked` report, a failed structural check, or any result that is not the three-line report — a question, a progress note, a pause to wait on a background run — earns exactly one retry. When the host can resume the same agent, resume it once with one line: the step is still yours to finish; return the report. Otherwise `git reset --hard && git clean -fd`, then re-dispatch the same step, appending a test or environment failure in its own words, or that the previous run returned something other than the report and the gap is still its to close. The failure is the Step agent's to diagnose. A second failure **halts** the run.

Done when every file in `.agents/steps/<slug>/` reads `Status: done`.

### 4. Review and improve

**Run `/code-review` yourself**, with `master` as the fixed point. Pass the Spec path, or that there is no Spec when the run started from a one-liner, and tell both axes that the Changelog is written in step 5 and that `.agents/steps/<slug>/` is run bookkeeping — its Outcomes are evidence, not code under review. Hold what its two axes report, weighed on the reports alone.

Give the user a short paragraph per axis in your own words. That summary replaces the verbatim presentation `/code-review` asks its caller for. Then keep going without waiting; the run lands unattended.

Two sub-agents follow, in this order, each reporting in the same three lines and subject to the same retry-then-halt rule. Hand each the Spec path (or that there is none) and that leftover choices are theirs to close from the findings, the Spec, and the code:

1. **Fixes every finding**, both axes, from the findings you paste into its prompt as the reviewers wrote them. Where a finding and the Spec disagree, the Spec wins and the finding is left, named on the deviations line. When neither axis reports a finding, skip this agent and say so. Retry-then-halt is the whole check on its work.
2. Runs `/improve-data-structures` and applies what it finds, or skips it.

Each leaves the projects it touched green and commits its own work. A schema, migration, or ADR change either one makes goes to the user as a deviations line before you continue.

### 5. Document the change

Run `/document-changes` in **implement mode** while the Spec and step Outcomes are still on disk — after review/improve, before delete and land. It prepends product-facing **Changelog** entries beside each affected context's `CONTEXT.md` and commits when it wrote; when nothing is product-visible it reports that and leaves the tree clean.

### 6. Land the branch

Delete the Spec, the whole `.agents/steps/<slug>/` directory, and the Idea or Issue document the Spec came from — unless the Spec says that document outlives it, in which case leave it and say so in the final report. Repoint or remove links to the deleted files from other `.agents/` documents. The Prototype folder the Spec points at stays ([ADR-0017](../../docs/adr/0017-prototypes-live-under-agents-prototypes.md)). Commit anything still uncommitted; `git rebase` refuses a dirty tree, so the branch cannot land until this is clean.

Each remaining command runs where its branch is checked out, and that constraint fixes the order. `<branch>` is `<slug>`, or the name you recorded when a host tool chose another:

1. From the worktree, still on the branch: `git rebase master`, resolving any conflicts. (The branch lives here, so only the worktree can rebase it.)
   - A `CHANGELOG.md` conflict is always keep both, this run's entry above.
   - When the rebase replayed the branch onto commits master gained during the run, green is not known any more: build and run the projects on every Step's `Projects:` line — the whole suite when the last Step ran it — before going on. A red run gets one fixer dispatch under the retry-then-halt rule, and its commit lands before the fast-forward.
2. Return the session to the original directory, keeping the branch and its commits — a host leave-worktree action when it does exactly that, otherwise change directory yourself.
3. From the original directory, on `master`: `git merge --ff-only <branch>`. (master lives here, so only the original directory can fast-forward it.) The rebase above makes this a fast-forward; if it errors, master moved during the session — re-enter the worktree, rebase again, and retry.
4. `git worktree remove <path>` — never forced; a lock means another session still has it — and `git branch -d <branch>`.

## Worktree waived

Steps live at `.agents/steps/<slug>/` in the checkout, and there is nothing to enter, exit, or remove. Step 1 skips opening a worktree. Step 6 drops the return-to-original-directory step and `git worktree remove`: rebase on the branch, check out master yourself, fast-forward, then delete the branch.

## Work in another repository

The worktree, the review diff, and the land cover this repository only. Work a Spec puts in another repository goes on a branch named `<slug>` there, committed by the Step that did it and never pushed; the final report names the repository, the branch, and what sits on it.

## Halting

A halt is non-destructive and it is the end of the session. Leave the spec, the step files, the branch, and the worktree exactly as they are — the completed steps are committed, and the run is resumable only because nothing was cleaned up. Report the step's number, its title, and why it did not finish. Quote a test or environment failure. For a result that is a question, say the agent did not finish.

Re-invoking `/implement` with the same argument picks the run back up at that step.
