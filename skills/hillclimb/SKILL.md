---
name: hillclimb
description: "Hillclimb one measured number — test-suite time, build time, memory, bundle size — keeping only the changes that measurably help. Use when the user wants something made faster, smaller, or cheaper, as far as it will go or past a target."
argument-hint: "Which number to improve, or which Issue?"
---

You are the **driving session** of a **Hillclimb**: one number, one direction, and one discipline — one **Attempt**, one measurement, keep or revert. A fresh **Climber** (`skills:climber`, `agents/climber.md` at the plugin root) writes each Attempt's code and leaves it uncommitted; you measure it, run the tests, and keep or revert it, so the agent that wrote a change never judges it. Profiling goes to a `skills:explorer`. Both run on your model at reduced effort because their task is fixed before they start ([ADR-0049](../../docs/adr/0049-spec-bound-agents-keep-the-session-model.md)); the review's fixers are `general-purpose` at your own model and effort. See [ADR-0061](../../docs/adr/0061-hillclimb-keeps-only-measured-wins.md).

You hold the Attempt log, the measurement script's short summaries, the Climber's three-line reports, and the Explorer's report — that is what lets an effort of hours run inside one session. Raw output goes to `<scratch>`, never into your context.

The measurement rules are [MEASURE.md](MEASURE.md) in this skill's directory. Read it before step 3.

Issues live in the repo's **Tracker**: carry out each operation on one — file, read, list, rewrite, set status, comment, link, claim, close — as `.agents/refs/tracker.md` says, or as [setup/LOCAL.md](../setup/LOCAL.md) says when the repo has no ref.

## Names

- `<slug>` names the number, such as `test-suite-time` — never the Issue, so the next Hillclimb on the same number finds the same folder.
- `<folder>` is `.agents/hillclimbs/<slug>/`, holding `log.md` (the **Attempt log**) and `measure.<ext>` (the measurement script). In a repo with a `CONTEXT-MAP.md` it gains a context subfolder — follow [domain-modeling/CONTEXT-PATHS.md](../domain-modeling/CONTEXT-PATHS.md).
- `<branch>` is `hillclimb/<slug>`, or the name in the run worktree's `<scratch>/branch` when a host tool chose another in step 2.
- `<base>` is the **Base branch**: `git branch --show-current` in the original directory when this skill starts, read again on a resume. The Hillclimb branches from it and lands back on it ([ADR-0055](../../docs/adr/0055-a-run-lands-on-the-branch-it-started-from.md)). Empty means HEAD is detached: **halt**.
- `<before>` is a second, detached checkout at `.agents/worktrees/hillclimb/<slug>-before` in the original directory. It sits at the run worktree's HEAD until step 7 moves it to `<base>`, and it is the "before" side of every measurement.
- `<scratch>` is `<folder>/scratch/` in the run worktree, by absolute path: raw run output and profiler output. It sits inside the run worktree because a host that isolates the session there refuses writes outside it, the git common directory included. A `.gitignore` inside it holds `*`, so no commit sweeps it in and `git clean -fd` leaves it. Removing the run worktree in step 7 deletes it; a halt keeps it.

## Process

### 1. Find or agree the start

The argument is an Issue reference or a description of what to improve. Read the Issue. Pick `<slug>`: when a `log.md` under `.agents/hillclimbs/` (every context subfolder included) measures the same number, take its slug; otherwise name the number in kebab case.

Find worktrees with `git worktree list`. The **run worktree** is the linked worktree on `hillclimb/<slug>`, or the one whose `<scratch>/branch` names its branch. When the run worktree or branch `hillclimb/<slug>` exists, the Hillclimb is **in flight**: go to [Resuming](#resuming).

Otherwise agree the start. Name, in plain language:

- the number, its unit, and which direction is better — the end-to-end number the user waits on, not a piece of it;
- the command it comes from;
- the **target**, the **minimum number of Attempts**, and a **time limit** if any — the stop rule in step 5;
- the tests that must keep passing: the whole suite unless the request narrows it.

Propose a value for everything the request left out — a target such as 30% better than the baseline, at least 10 Attempts. When the request already named the number and the target, state the start and go on. Otherwise wait for the user's OK; from that OK on, the Hillclimb runs unattended.

Then claim the Issue as the Tracker ref says. When the ref says another user holds it, stop and name them. A ref that gives no claim for Issues skips this.

### 2. Enter the worktree

Open a worktree on `<branch>` and put the session's working directory inside it, then `git reset --hard <base>`:

- If this host has a tool that **creates the worktree and moves the session into it**, use that tool — even when its path is not the fallback below. Decide from the tool list you already have. Record the branch name it chose when that name is not `hillclimb/<slug>`.
- Otherwise ensure the consuming repo ignores `.agents/worktrees/` (add the line if missing; prefer a local ignore when the repo uses one), then `git -c checkout.workers=0 worktree add` at `.agents/worktrees/hillclimb/<slug>` on `<branch>`, and change the session's working directory there.

The session works *inside* the run worktree until step 7 returns it. Run every command from there as a **plain** command: every argument spelled out, and files written with the host's file tools. A host that isolates the session in its worktree refuses a command it cannot prove stays inside, such as one with a `cd` or `git -C`, a shell variable, `$(…)`, or a heredoc, and says how to split it. Name the run worktree in every sub-agent prompt as the only directory the agent works in, adding the plain-command rule for the Explorer and a `general-purpose` agent. On a host whose shell starts every command in the original directory, resolve the worktree's absolute path once with `pwd` inside it and begin every command with `cd <that path> &&`. A Hillclimb always runs in a worktree; a prompt cannot waive it.

Create `<scratch>` and its `.gitignore`, and write a recorded branch name to `<scratch>/branch`.

Create `<before>` with `git worktree add --detach` at the run worktree's HEAD, after ensuring `.agents/worktrees/` is ignored as above.

### 3. Freeze the measurement

When `<folder>/log.md` exists, read it whole and reuse the script beside it. Otherwise write both, the log in [the shape below](#the-attempt-log).

Hold the script to MEASURE.md: its contract, then its sensitivity check, run now even on a reused script. A script that cannot tell a slow case from a fast one gets a revised workload or number; when no revision separates them, **halt**.

Record the baseline: check what else is running, build `<before>`, and measure it alone with at least 3 runs. Run the agreed tests once in the run worktree. Write this Hillclimb's section at the top of the log — the agreed start, the deadline (start plus the time limit), the baseline, and the tests that already fail. An already-failing test is noted and blocks nothing ([ADR-0029](../../docs/adr/0029-green-is-measured-against-the-base-branch.md)). Commit `<folder>` as `hillclimb(<slug>): start`.

### 4. Profile

Dispatch a `skills:explorer` with: the number and its command, the script, the log's path, `<scratch>` for its output, and MEASURE.md's [limiter](MEASURE.md#finding-the-limiter) section. It finds what limits the number in runs nobody reports, and returns that limiter in one paragraph plus a ranked list of ideas. Each idea names the mechanism it targets and the effect it expects. An idea the log shows reverted comes back only with what has changed since.

Replace the log's **Ideas not yet tried** with that list and commit the log.

### 5. Run the Attempts, one at a time

Before each Attempt, check the **stop rule**. The Hillclimb stops when the target and the minimum number of Attempts are both met, when the deadline has passed, or when the ideas left are marginal and not worth their cost. Cheap untried ideas left mean it goes on, and the target stays as agreed. When it stops, go to step 6.

Each Attempt:

1. Take the top idea from **Ideas not yet tried**, and read the log's rows on the code it touches.
2. Dispatch a fresh `skills:climber`. Its prompt is the idea in your words plus paths: the run worktree, the log, `CONTEXT.md` and any ADR covering the area, the Coding standards — found the way `/code-review` finds them, `.agents/refs/` first — the command for the agreed tests, and this report format:

   ```
   status: ready | blocked
   changed: <one sentence on what the change does, naming any work it removes>
   merge risk: <what a revert would not undo, and who would notice if it went wrong — or "revert restores everything">
   ```

3. A `blocked` report, an empty `git status`, or anything but that report is a failed Attempt: go to 7 as reverted, with the reason in the row's `Note`.
4. Build `<before>` and the run worktree, then measure the pair as MEASURE.md says: alternating, at least 3 runs per side.
5. Run the agreed tests in the run worktree.
6. **Keep** the change when the number moved past the run-to-run spread in the agreed direction, no test fails that did not fail at the baseline, and the work count held — or when it simplifies the code and holds the number. A change that removes counted work is kept only when the Climber's `changed:` line names what it removed. A change that breaks behaviour is reverted however much it helps. Everything else is **reverted**.
7. Record it in one commit. Kept: write the row, then commit the changed files and the log together — never `git add -A` — with a message that names the change and its before → after, and move `<before>` to the new HEAD. Reverted: `git reset --hard && git clean -fd` first, then write the row and commit the log alone.
8. Tell the user one line: `Attempt <n> — <idea>: kept | reverted, <before> → <after>`.

After 3 reverted Attempts in a row, dispatch a fresh Explorer as in step 4, naming the kind of change that kept failing and asking for a different kind. Its list replaces the old one.

Done when the stop rule holds.

### 6. Review

**Run `/code-review` yourself**, with `git merge-base <base> HEAD` as the fixed point. Pass the Issue as the Spec when the Hillclimb started from one; otherwise say there is no Spec. Tell both axes that `<folder>` is the Hillclimb's record — the measurement script is frozen and the log is evidence, not code under review.

Then dispatch, in this order, a **Spec fixer** for the Spec axis's findings and a **Standards fixer** for the Standards axis's, each `general-purpose`, each with the findings pasted as the reviewers wrote them, the run worktree, the Issue when there is one, the Coding standards, the command for the agreed tests, and the three-line report `status: / built: / deviations:`. Skip a fixer whose axis found nothing. Each runs the agreed tests, leaves them passing, and commits its own work. A `blocked` report or anything but the report earns one fresh dispatch; a second failure **halts**.

Done when every finding is fixed or named on a deviations line, and each axis's fixer has reported or was skipped.

### 7. Land

Commit anything still uncommitted. Then, in order:

1. In the run worktree: `git rebase <base>`. A conflict is `/resolving-merge-conflicts`. When the rebase replayed the branch onto new commits, run the agreed tests again. Re-run a failing project once yourself: a failure that passes on the re-run is a flaky test for the report ([ADR-0046](../../docs/adr/0046-a-flaky-post-rebase-failure-is-not-a-fixer-dispatch.md)); one that fails again gets one `general-purpose` fixer, and a second failure **halts**.
2. Move `<before>` to `<base>` and measure the pair as MEASURE.md says. Write the result into this Hillclimb's section of the log. It goes in the report and blocks nothing. Commit the log. When the Hillclimb started from an Issue, this log commit carries the Issue's closing reference as the Tracker ref gives it; when the ref gives none, the report names the Issue for the user to close.
3. Return the session to the original directory, keeping the branch — a host leave-worktree action when it does exactly that, otherwise change directory yourself.
4. On `<base>`: `git merge --ff-only <branch>`. This step is done when the merge has succeeded, `git worktree remove` has run on the run worktree, deleting `<scratch>` with it — never forced; a lock means another session still has it — `git worktree remove --force` has run on `<before>`, and `git branch -d <branch>` has run. When the merge errors, `<base>` moved: re-enter the run worktree, drop the log commit with `git reset --hard HEAD~1`, go through 1 to 3 again, and retry the merge.

### 8. Report

Run `/plain-language`, then report:

- the number and its target, the baseline and the final value against `<base>`, and the change in percent;
- how many Attempts were kept and how many reverted;
- each kept change on one line, with its merge risk;
- the tests that already failed, and any flaky test from step 7;
- the log's path, and the best idea still untried.

### 9. Retrospective

Run `/retro` — unless another Named session skill started this Hillclimb; that skill runs it.

### 10. Push

Run `/implement`'s [push](../implement/SKILL.md#the-push). Read only that section of that file. A line in `AGENTS.md` or `CLAUDE.md` saying implement runs do not push turns this push off too.

## The Attempt log

`<folder>/log.md`, committed and kept across Hillclimbs. A later session reads it: the next Hillclimb on this number, and any resume. Newest Hillclimb first:

```markdown
# <number> (<unit>, <lower | higher> is better)

Measured by `measure.<ext>`: <what it runs, in one line>.

## Ideas not yet tried

- <idea> — <the mechanism it targets>

## Hillclimb <YYYY-MM-DD>

Started from: <Issue, or the request in one line>. Target: <target>. Minimum Attempts: <n>. Deadline: <time, or none>.
Baseline: <median> (<min>–<max>, <runs> runs), <work count>. Already failing: <tests, or none>.
Result: <final median against <base>> (<change in %>) — written in step 7.

| # | Idea | Change | Before | After | Tests | Verdict | Note |
|---|------|--------|--------|-------|-------|---------|------|
```

`Before` and `After` are median and range. `Verdict` is `kept` or `reverted`. The reverted rows are the ideas proven not to help; `Note` says why, or what the measurement showed.

## Resuming

A run worktree whose lock names a live process is another session's Hillclimb: stop and say so. Otherwise put the session's working directory on the run worktree, or `git -c checkout.workers=0 worktree add` one at `.agents/worktrees/hillclimb/<slug>` on `<branch>` when it has none. `git reset --hard && git clean -fd` throws away an Attempt that never reached its commit. Recreate `<scratch>` as step 2 does, and `<before>`, when either is missing.

Read the log. When this Hillclimb's section has no baseline, go to step 3. When the deadline has passed, go to step 6 — unless the user's request gives a new time limit, which goes in the section as the new deadline. Otherwise go to step 5, or to step 4 when **Ideas not yet tried** is empty.

## Halting

A halt is non-destructive and ends the session. Leave the branch, the run worktree, `<before>`, `<scratch>`, and the log exactly as they are — every finished Attempt is committed, and re-invoking `/hillclimb` with the same number picks it back up. Report why it stopped, quoting the failure. A halt skips step 9.
