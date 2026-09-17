---
name: implement
description: "Implement a spec by slicing it into steps and running ready steps in parallel sub-agents."
argument-hint: "Which spec, issue, or idea to implement?"
disable-model-invocation: true
---

You are the **driving session**: you orchestrate, sub-agents implement. You hold the step index, which Steps are in flight, one three-line report per step, any deviations, and the review findings for as long as step 4 takes to hand them on — that is the whole of your context, and it is what lets a spec of any size run to landed inside one session. So you hand paths, and the sub-agent that needs a document reads it; your own reads before step 5 are step 3's structural check and nothing more. While Step agents run, waiting is the work.

A **Ready** Step (every blocker done) runs as soon as it is Ready, together with the others that are. Each Ready Step gets its own worktree off the run branch; rebase it onto that branch before anything that was waiting on it starts. Step agents are `skills:implementer` (`agents/implementer.md` at the plugin root), pinned to a cheaper tier because their scope was decided before they started; a host without that tier uses its cheapest model that edits code. The planner, the fixer, and the data-structures pass run at your own model and effort — they carry judgement worth paying for. See [ADR-0007](../../docs/adr/0007-pinned-subagent-model-tiers.md) and [ADR-0033](../../docs/adr/0033-implement-runs-ready-steps-in-parallel.md).

Every sub-agent closes leftover gaps from the documents it was handed and the code. See [ADR-0026](../../docs/adr/0026-implement-agents-close-leftover-gaps.md).

The run never leaves a local checkout: nothing pushes, publishes, or changes a live system, and a Step that needs that **halts**. See [ADR-0028](../../docs/adr/0028-implement-never-leaves-the-repository.md).

## Process

### 1. Enter the worktree

Derive `<slug>`: the spec's filename without its extension when the argument names one, otherwise a kebab-case slug from the argument.

`master` here and below means the repository's default branch — `main` where that is what the repo uses. The main checkout's working tree is the user's and stays as you found it until step 6.

Find worktrees with `git worktree list` (or the host's equivalent). The **run worktree** is the one whose branch is `<slug>` (or the name a host tool recorded). Branches named `<slug>-<NN>` are Step worktrees; they are not the session directory. A prior run is **in flight** when that run worktree exists, or when any linked worktree contains `.agents/steps/<slug>/`.

- **In flight** → a run worktree whose lock names a live process is another session's run: stop and say so. Otherwise:
  - Put the session's working directory on the run worktree's path.
  - `git reset --hard && git clean -fd` drops whatever a halted merge left in the run worktree. If the host refuses the reset, `git stash push -u` and name the stash in the final report.
  - For each Step worktree: a lock means that Step agent is still live — leave it. A Step file that already reads `Status: done` is waiting to rebase onto the run branch: do that in step 3 before dispatching anything new. A not-done Step with no lock is reset in its worktree the same way, then treated as pending.
  - When `.agents/steps/<slug>/` holds Step files, the Steps are already planned: skip step 2 and resume at step 3, or at step 4 when every Step reads `done` and no Step worktree remains. A missing or empty steps directory is a fresh plan — continue at step 2.
- **Fresh** → open a worktree for this run, put the session's working directory inside it, then `git rebase master` so the run sits on the master you actually have:
  - If this host has a tool that **creates the worktree and moves the session into it**, use that tool — even when its path is not the fallback below. Decide from the tool list you already have rather than searching the host's CLI or docs. Record the branch name it chose when that name is not `<slug>`.
  - Otherwise ensure the consuming repo ignores `.agents/worktrees/` (add the line if missing; prefer a local ignore when the repo uses one), then `git -c checkout.workers=0 worktree add` at `.agents/worktrees/<slug>` on branch `<slug>`, and change the session's working directory there.

The session must work *inside* the run worktree for the rest of the run — creating a worktree alone is not enough. On a host whose shell starts every command in the original directory, resolve the worktree's absolute path once with `pwd` inside it, then begin every command with `cd <that path> &&` (or `git -C <that path>`), scope every search to it, and carry the run worktree path into every sub-agent prompt that works there. An `/implement` prompt that explicitly waives the worktree takes the branch in [Worktree waived](#worktree-waived) instead.

### 2. Plan the steps

Dispatch a **planner** sub-agent. Give it the spec path (or the argument text), `<slug>`, and the absolute path to [STEPS.md](STEPS.md) in this skill's directory — those three and nothing else. It reads the slicing rules itself, writes one file per Step to `.agents/steps/<slug>/`, and commits them in one commit before returning, so the resets in steps 1 and 3 cannot delete a Step not yet done ([ADR-0030](../../docs/adr/0030-planner-commits-the-step-files.md)). When `git status` still shows that directory afterwards, commit it yourself as `plan: <slug>`.

It returns the index and nothing else: one line per step, `NN | title | blocked by: none|<NNs> | one-line deliverable`.

The plan succeeded when that reply is the index and `.agents/steps/<slug>/` holds Step files. Otherwise **halt** — the planner failed, returned no steps, left the directory missing or empty, or replied with something other than the index. Do not dispatch another agent to write or commit the files; the dirty-directory commit above is the only Driving-session write for this step.

### 3. Run the Ready Steps

Dispatch every Ready pending Step together (`Blocked by: none`, or every listed NN reading `Status: done`). For each one:

1. Resolve the main checkout from `git worktree list` (the first worktree). Open a Step worktree there at `.agents/worktrees/<slug>-<NN>` on a new branch `<slug>-<NN>` starting at the run branch's current HEAD, with `git -c checkout.workers=0 worktree add`, so this session stays in the run worktree.
2. Dispatch a fresh `skills:implementer` whose only working directory is that Step worktree, with a prompt made of paths and section names — it reads what is behind them:
   - the spec, and its own step file — whose `## Footprint` names the files, symbols and projects the work lands in
   - an instruction to read the `## Outcome` of every Step file whose `Status:` is `done` before starting
   - `CONTEXT.md` and any ADR covering the area it touches, for vocabulary
   - the coding-standards sources found the same way `/code-review` finds them — `.agents/refs/` first, then a root-level coding-standards or contributing file when that is what the repo has; only documents that say how code should be written — when those exist
   - the spec's Testing Decisions section, which governs what it tests
   - the deviations reported so far, verbatim, when there are any
   - its Step number and the total, and the report format below

Tell it how far to trust its map: its footprint is a guess — where the code disagrees, the code wins, and the drift goes in its `## Outcome` so its successors inherit the correction.

Require of it: **green before it finishes**, then its `## Outcome` appended to its Step file, that file's `Status:` set to `done`, and its code and Step file committed together in one commit.

- Green covers every project on its footprint's `Projects:` line, and the whole suite on the last Step.
- Green is measured against `master` ([ADR-0029](../../docs/adr/0029-green-is-measured-against-master.md)): a failure that also fails on `master` at the merge-base goes on the deviations line and does not block landing; every other failure is red until fixed.
- A verification the repo's own conventions demand for the surface the Step touches — a browser pass, a smoke run — counts toward green and is the Step agent's, run from its worktree.
- `CHANGELOG.md` stays untouched whatever the repo's docs rules say; step 5 writes it.

Its entire response is three lines:

```
status: done | blocked
built: <one sentence on what now works>
deviations: <what contradicts the Spec or changes a later Step, or "none">
```

A fact a successor needs goes in `## Outcome`; the successor reads it there.

Then **check the step structurally** — `grep '^Status:'` on the Step file in that worktree reads `done`, and `git log -1` on `<slug>-<NN>` shows a new commit. That is the whole check; open the Step file only when it fails. Step 4's review covers the rest.

**Rebase onto the run branch.** From the Step worktree, `git rebase` onto the run branch. From the run worktree, `git merge --ff-only <slug>-<NN>`. A conflict in either step is `/resolving-merge-conflicts`, with the stated goal: this run's commits, linear, this Step's intent preserved where it does not contradict a Step already on the run branch. Then `git worktree remove` the Step worktree and `git branch -d <slug>-<NN>`. Completions that arrive together rebase one at a time, lowest NN first.

Report one line to the user after each rebase — `Step <NN>/<total> — <title>: done` — plus the deviations line when it is not `none`, and carry those deviations verbatim into every later dispatch.

Dispatch any Step that just became Ready.

A `blocked` report, a failed structural check, or any result that is not the three-line report — a question, a progress note, a pause to wait on a background run — earns exactly one retry of **that** Step. When the host can resume the same agent, resume it once with one line: the step is still yours to finish; return the report. Otherwise `git reset --hard && git clean -fd` in its worktree, then re-dispatch the same step, appending a test or environment failure in its own words, or that the previous run returned something other than the report and the gap is still its to close. The failure is the Step agent's to diagnose. A second failure **halts** new dispatch; in-flight siblings finish or fail on their own, then the session ends.

Done when every file in `.agents/steps/<slug>/` reads `Status: done` and no Step worktree remains.

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

Delete the Spec, the whole `.agents/steps/<slug>/` directory, and the Idea or Issue document the Spec came from — unless the Spec says that document outlives it, in which case leave it and say so in the final report. Repoint or remove links to the deleted files from other `.agents/` documents. The Prototype folder the Spec points at stays ([ADR-0018](../../docs/adr/0018-prototypes-live-under-agents-prototypes.md)). Commit anything still uncommitted; `git rebase` refuses a dirty tree, so the branch cannot land until this is clean.

Each remaining command runs where its branch is checked out, and that constraint fixes the order. `<branch>` is `<slug>`, or the name you recorded when a host tool chose another:

1. From the worktree, still on the branch: `git rebase master`. A conflict is `/resolving-merge-conflicts` (the branch lives here, so only the worktree can rebase it).
   - A `CHANGELOG.md` conflict is always keep both, this run's entry above.
   - When the rebase replayed the branch onto commits master gained during the run, green is not known any more: build and run the projects on every Step's `Projects:` line — the whole suite when the last Step ran it — before going on. A red run gets one fixer dispatch under the retry-then-halt rule, and its commit lands before the fast-forward.
2. Return the session to the original directory, keeping the branch and its commits — a host leave-worktree action when it does exactly that, otherwise change directory yourself.
3. From the original directory, on `master`: `git merge --ff-only <branch>`. (master lives here, so only the original directory can fast-forward it.) The rebase above makes this a fast-forward; if it errors, master moved during the session — re-enter the worktree, rebase again, and retry.
4. `git worktree remove <path>` — never forced; a lock means another session still has it — and `git branch -d <branch>`.

### 7. Retrospective

Run `/retro`.

## Worktree waived

Steps live at `.agents/steps/<slug>/` in the checkout, and there is nothing to enter, exit, or remove. Step 1 skips opening a worktree. Step 3 runs Ready Steps **one at a time in this checkout** — skip the Step worktree and the rebase; a shared tree cannot hold two editors. Step 6 drops the return-to-original-directory step and `git worktree remove`: rebase on the branch, check out master yourself, fast-forward, then delete the branch.

## Work in another repository

The worktree, the review diff, and the land cover this repository only. Work a Spec puts in another repository goes on a branch named `<slug>` there, committed by the Step that did it and never pushed; the final report names the repository, the branch, and what sits on it.

## Halting

A halt is non-destructive and it is the end of the session. Leave the Spec, the Step files, the branch, the run worktree, and any Step worktrees exactly as they are — the completed Steps are committed, and the run is resumable only because nothing was cleaned up. Report why the run stopped: for a Planner failure, that the Planner failed and why, and what a re-invoke will do; for a Step, its number, its title, and why it did not finish. Quote a test or environment failure. For a result that was not the report, say the agent did not finish.

Re-invoking `/implement` with the same argument picks the run back up — a missing or empty steps directory runs the Planner again; Step files already on disk resume at running Steps.
