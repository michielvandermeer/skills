---
name: implement
description: "Implement a spec by slicing it into steps and running each one in its own sub-agent."
argument-hint: "Which Issue to implement, or what to build?"
disable-model-invocation: true
---

You are the **driving session**: you orchestrate, sub-agents implement. You hold the step index, the Step agent's and the Checker's three-line reports per step, any deviations, and the review findings for as long as step 4 takes to hand them on — that is the whole of your context, and it is what lets a spec of any size run to landed inside one session. So you hand paths, and the sub-agent that needs a document reads it; your own reads before step 5 are step 1's read of the Issue, step 3's two structural checks, and the `git rev-parse` that finds the Checker's fixed point, and nothing more. While a sub-agent runs, waiting is the work.

Steps run one at a time, in `NN` order, in one checkout — the run worktree, or this checkout when the worktree is waived. Step agents are `skills:implementer` (`agents/implementer.md` at the plugin root), and the **Checker** that finishes each Step is `skills:checker` (`agents/checker.md` at the plugin root); both run on your model at reduced effort because their scope was decided before they started ([ADR-0051](../../docs/adr/0051-a-fresh-checker-finishes-each-step.md)). The **Planner** is `skills:planner` (`agents/planner.md` at the plugin root) and runs at your own model and effort. The Spec fixer, the Standards fixer, and the data-structures pass are `general-purpose` and run at your own model and effort. See [ADR-0049](../../docs/adr/0049-spec-bound-agents-keep-the-session-model.md), [ADR-0045](../../docs/adr/0045-implement-runs-steps-one-at-a-time.md), and [ADR-0043](../../docs/adr/0043-planner-is-a-named-plugin-agent.md).

Every sub-agent closes leftover gaps from the documents it was handed and the code. See [ADR-0026](../../docs/adr/0026-implement-agents-close-leftover-gaps.md).

The run never leaves a local checkout: nothing pushes, publishes, writes to the Tracker, or changes a live system, and a Step that needs that **halts**. The closing reference its landing commit carries is how the Tracker learns the work is done. See [ADR-0028](../../docs/adr/0028-implement-never-leaves-the-repository.md) and [ADR-0001](../../docs/adr/0001-each-repo-describes-its-tracker.md).

## Process

### 1. Enter the worktree

Issues live in the repo's **Tracker**: carry out each operation on one — file, read, list, rewrite, set status, comment, link, close — as `.agents/refs/tracker.md` says, or as [setup/LOCAL.md](../setup/LOCAL.md) says when the repo has no ref.

The argument is an Issue reference — normally an Issue in `ready-for-agent` — or a description of the change, which touches no Tracker; an issue outside this repo's Tracker is read as a description. Read the Issue. Derive `<slug>`: the Issue's run slug as the Tracker ref gives it, otherwise a kebab-case slug from the description.

`<base>` is the **base branch**: `git branch --show-current` in the original directory when this command starts, read again on a resume. The run branches from it, is reviewed and measured green against it, and lands back on it ([ADR-0055](../../docs/adr/0055-a-run-lands-on-the-branch-it-started-from.md)). If it is empty, **halt** — HEAD is detached. The main checkout's working tree is the user's and stays as you found it until step 6.

An Issue blocked by another Issue waits on it: while the blocker is open, stop before anything else and say it lands first — unless `<base>` already holds the blocker's closing reference, found as the Tracker ref says ([ADR-0047](../../docs/adr/0047-a-wayfinder-map-ends-in-one-or-more-specs.md)).

Find worktrees with `git worktree list` (or the host's equivalent). The **run worktree** is the one whose branch is `<slug>` (or the name a host tool recorded). A prior run is **in flight** when that run worktree exists, or when any linked worktree contains `.agents/steps/<slug>/`.

- **In flight** → a run worktree whose lock names a live process is another session's run: stop and say so. Otherwise:
  - Put the session's working directory on the run worktree's path.
  - `git reset --hard && git clean -fd` drops whatever a halted Step left behind. If the host refuses the reset, `git stash push -u` and name the stash in the final report.
  - When `.agents/steps/<slug>/` holds Step files (`[0-9][0-9]-*.md`), the Steps are already planned: skip step 2 and resume at the lowest-numbered Step whose `Status:` is not `done` — at its Checker when it reads `built`, at its Step agent when it reads `pending` — or at step 4 when every Step reads `done`. A steps directory with no Step files is a fresh plan — continue at step 2.
- **Fresh** → open a worktree for this run, put the session's working directory inside it, then `git reset --hard <base>` so the run starts from the `<base>` you actually have — the new branch has no commits of its own yet:
  - If this host has a tool that **creates the worktree and moves the session into it**, use that tool — even when its path is not the fallback below. Decide from the tool list you already have rather than searching the host's CLI or docs. Record the branch name it chose when that name is not `<slug>`.
  - Otherwise ensure the consuming repo ignores `.agents/worktrees/` (add the line if missing; prefer a local ignore when the repo uses one), then `git -c checkout.workers=0 worktree add` at `.agents/worktrees/<slug>` on branch `<slug>`, and change the session's working directory there.

The session must work *inside* the run worktree for the rest of the run — creating a worktree alone is not enough. On a host whose shell starts every command in the original directory, resolve the worktree's absolute path once with `pwd` inside it, then begin every command with `cd <that path> &&` (or `git -C <that path>`), scope every search to it, and carry that path into every sub-agent prompt as the only directory the agent works in. An `/implement` prompt that explicitly waives the worktree takes the branch in [Worktree waived](#worktree-waived) instead.

Before leaving this step, when the argument is an Issue and `.agents/steps/<slug>/spec.md` is missing, write the Issue's title, as an H1, and its body to that file — nothing else. From here on **the Spec** is that copy: every sub-agent and `/document-changes` reads it, a resume reads it rather than the Issue, and step 2 commits it with the Step files.

### 2. Plan the steps

Dispatch a `skills:planner`. Give it the Spec's path (or the argument text), `<slug>`, and the absolute path to [STEPS.md](STEPS.md) in this skill's directory — those three and nothing else. It reads the slicing rules itself, writes one file per Step to `.agents/steps/<slug>/`, and commits them with the Spec in one commit before returning, so the resets in steps 1 and 3 cannot delete the Spec or a Step not yet done ([ADR-0030](../../docs/adr/0030-planner-commits-the-step-files.md)). When `git status` still shows that directory afterwards, commit it yourself as `plan: <slug>`. A host without that agent type dispatches `general-purpose` with the same prompt.

It returns the index and nothing else: one line per step, `NN | title | one-line deliverable`.

The plan succeeded when that reply is the index and `.agents/steps/<slug>/` holds Step files. Otherwise **halt** — the Planner failed, returned no steps, left no Step files in the directory, or replied with something other than the index. Do not dispatch another agent to write or commit the files; the dirty-directory commit above is the only Driving-session write for this step.

### 3. Run each step in `NN` order

`<proof>` is the run's Proof folder: `$(git rev-parse --path-format=absolute --git-common-dir)/proof/<slug>`.

Dispatch a fresh `skills:implementer` per step, with a prompt made of paths and section names — it reads what is behind them:

- the spec, and its own step file — whose `## Footprint` names the files, symbols and projects the work lands in
- an instruction to read, before starting, the `## Outcome` of each step on its step file's `Depends on:` line — none for `Depends on: none`, and every lower-numbered step's when the line is missing
- `CONTEXT.md` and any ADR covering the area it touches, for vocabulary
- the Coding standards, found the same way `/code-review` finds them — `.agents/refs/` first, then a root-level coding-standards or contributing file when that is what the repo has; only documents that say how code should be written — when those exist
- the spec's Testing Decisions section, which governs what it tests
- the Proof rules, [PROOF.md](PROOF.md) in this skill's directory by absolute path, and `<proof>`
- `<base>`, the branch its tests are measured against
- the deviations reported by earlier steps, verbatim, when there are any
- its Step number and the total, and the report format below

Tell it how far to trust its map: its footprint is a guess — where the code disagrees, the code wins, and the drift goes in its `## Outcome` so the steps that depend on it inherit the correction.

Require of it: **its tests passing before it finishes**, then its `## Outcome` — Safety fact and Proof included — appended to its Step file, that file's `Status:` set to `built`, and its code and Step file committed together in one commit.

- Its tests are those of every project on its footprint's `Projects:` line, and the whole suite on the last Step.
- They are measured against `<base>` ([ADR-0029](../../docs/adr/0029-green-is-measured-against-the-base-branch.md)): a failure that also fails on `<base>` at the merge-base goes on the deviations line and does not block landing; every other failure is red until fixed.
- `CHANGELOG.md` stays untouched whatever the repo's docs rules say; step 5 writes it.

Its entire response is three lines:

```
status: done | blocked
built: <one sentence on what now works>
deviations: <what contradicts the Spec or changes a later Step, or "none">
```

A fact a successor needs goes in `## Outcome`; the successor reads it there.

Then **check the step structurally** — `grep '^Status:'` on the Step file reads `built`, and `git log -1` shows a new commit. That is the whole check; open the Step file only when it fails.

Once that check passes, resolve the parent of the Step's commit with `git rev-parse HEAD~1`, then dispatch a fresh `skills:checker` for the same step. Its prompt is paths and section names too:

- the spec, and the step file
- that SHA, as the fixed point of its review
- `CONTEXT.md` and any ADR covering the area, the Coding standards, the spec's Testing Decisions section, PROOF.md, `<proof>`, and `<base>`, found as above
- the deviations reported by earlier steps and by this step's agent, verbatim, when there are any
- its Step number and the total, and the same three-line report format

Re-running the Proof, and driving the app through the Run recipe when the Step needs rung 4, are the Checker's, with the rest of its work as `agents/checker.md` lays it out. A step is **Green** only once both agents have passed ([ADR-0053](../../docs/adr/0053-green-needs-a-proof.md)).

Then **check the Checker structurally** — `grep '^Status:'` on the Step file reads `done`. Step 4's review covers the rest.

Report one line to the user after that check — `Step <NN>/<total> — <title>: done` — plus each report's deviations line when it is not `none`, and carry both reports' deviations verbatim into later dispatches.

A `blocked` report, a failed structural check, or any result that is not the three-line report — a question, a progress note, a pause to wait on a background run — earns exactly one retry, for the Step agent and the Checker alike. When the host can resume the same agent, resume it once with one line: the step is still yours to finish; return the report. Otherwise `git reset --hard && git clean -fd`, then re-dispatch the same agent for the same step, appending a test or environment failure in its own words, or that the previous run returned something other than the report and the gap is still its to close. The Step agent's commit survives that reset, so a re-dispatched Checker starts from it. The failure is the failed agent's to diagnose. A second failure **halts** the run.

Done when every Step file, `.agents/steps/<slug>/[0-9][0-9]-*.md`, reads `Status: done`.

### 4. Review and improve

**Run `/code-review` yourself**, with `<base>` as the fixed point. Pass the Spec path, or that there is no Spec when the run started from a one-liner, and tell both axes that the Changelog is written in step 5 and that `.agents/steps/<slug>/` is run bookkeeping — its Outcomes are evidence, not code under review. Hold what its two axes report, weighed on the reports alone.

Give the user a short paragraph per axis in your own words. That summary replaces the verbatim presentation `/code-review` asks its caller for. Then keep going without waiting; the run lands unattended.

Three sub-agents follow, in this order, each reporting in the same three lines and subject to the same retry-then-halt rule, each on its own retry. Hand each the Spec path (or that there is none), the Coding standards from step 3 — they bind every line it commits, comments and tests included — and that leftover choices are theirs to close from the findings, the Spec, and the code:

1. The Spec fixer fixes every finding of the Spec axis, which you paste into its prompt as the reviewers wrote them.
2. The Standards fixer fixes every finding of the Standards axis, pasted the same way. Tell it to skip a finding whose code is gone and name that finding on its deviations line.
3. The data-structures pass runs `/improve-data-structures` and applies what it finds, or skips it.

The Spec fixer goes first because a Spec fix can remove code that a Standards finding points at. For both fixers, where a finding and the Spec disagree, the Spec wins and the finding is left, named on the deviations line. When an axis reports no finding, skip its fixer and tell the user so. Retry-then-halt is the whole check on a fixer's work.

Each leaves the projects it touched green and commits its own work. A schema, migration, or ADR change any of the three makes goes to the user as a deviations line before you continue.

### 5. Document the change

Run `/document-changes` in **implement mode** while the Spec and step Outcomes are still on disk — after review/improve, before delete and land. It prepends product-facing **Changelog** entries beside each affected context's `CONTEXT.md` and commits when it wrote; when nothing is product-visible it reports that and leaves the tree clean.

### 6. Land the branch

Hold `grep -h '^Safety fact:' .agents/steps/<slug>/[0-9][0-9]-*.md` for the final report, then delete the whole `.agents/steps/<slug>/` directory, the Spec with it, and `<proof>`. The Prototype folder the Spec points at stays ([ADR-0018](../../docs/adr/0018-prototypes-live-under-agents-prototypes.md)). Commit the deletion with anything still uncommitted; `git rebase` refuses a dirty tree, so the branch cannot land until this is clean. When the run started from an Issue, that commit is its landing commit and carries the Issue's closing reference as the Tracker ref gives it; when it gives none, the final report names the Issue for the user to close.

Each remaining command runs where its branch is checked out, and that constraint fixes the order. `<branch>` is `<slug>`, or the name you recorded when a host tool chose another:

1. From the worktree, still on the branch: `git rebase <base>`. A conflict is `/resolving-merge-conflicts` (the branch lives here, so only the worktree can rebase it).
   - A `CHANGELOG.md` conflict is always keep both, this run's entry above.
   - When the rebase replayed the branch onto commits `<base>` gained during the run, green is not known any more: build and run the projects on every Step's `Projects:` line — the whole suite when the last Step ran it — before going on. Before any fixer dispatch, re-run each failing project once, yourself. A failure that passes on the re-run is a flaky test and does not block landing: its test name goes on the deviations line and into the final report, the same way a failure `<base>` already has does under [ADR-0029](../../docs/adr/0029-green-is-measured-against-the-base-branch.md). A failure that fails again is red and gets one fixer dispatch under the retry-then-halt rule, and its commit lands before the fast-forward ([ADR-0046](../../docs/adr/0046-a-flaky-post-rebase-failure-is-not-a-fixer-dispatch.md)).
2. Return the session to the original directory, keeping the branch and its commits — a host leave-worktree action when it does exactly that, otherwise change directory yourself.
3. From the original directory, on `<base>`: `git merge --ff-only <branch>`. (`<base>` lives here, so only the original directory can fast-forward it.) The rebase above makes this a fast-forward. This step is done when that merge has succeeded, `git worktree remove <path>` has run — never forced; a lock means another session still has it — and `git branch -d <branch>` has run. When the merge errors, `<base>` moved: re-enter the worktree, rebase again under step 1, return under step 2, and retry this merge.

The final report lists each Step's `Safety fact:` line. When the rebase replayed the branch onto new commits, it says the Proofs predate the rebase; they are not re-run.

### 7. Retrospective

Run `/retro`.

## Worktree waived

Steps live at `.agents/steps/<slug>/` in the checkout, and there is nothing to enter, exit, or remove. Step 1 skips opening a worktree. Step 6 drops the return-to-original-directory step and `git worktree remove`: rebase on the branch, check out `<base>` yourself, then fast-forward. That merge is done when it succeeds and `git branch -d` has run. When it errors, `<base>` moved: rebase again on the branch under step 1, check out `<base>` yourself, and retry the merge.

## Work in another repository

The worktree, the review diff, and the land cover this repository only. Work a Spec puts in another repository goes on a branch named `<slug>` there, committed by the Step that did it and never pushed; the final report names the repository, the branch, and what sits on it.

## Halting

A halt is non-destructive and it is the end of the session. Leave the Spec, the Step files, `<proof>`, the branch, and the run worktree exactly as they are — the completed Steps are committed, and the run is resumable only because nothing was cleaned up. Report why the run stopped: for a Planner failure, that the Planner failed and why, and what a re-invoke will do; for a Step, its number, its title, and why it did not finish. Quote a test or environment failure. For a result that was not the report, say the agent did not finish.

Re-invoking `/implement` with the same argument picks the run back up — a steps directory with no Step files runs the Planner again; Step files already on disk resume where step 1 says.
