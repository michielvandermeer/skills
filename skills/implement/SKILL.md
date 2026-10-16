---
name: implement
description: "Implement a spec in a loop of implement, review, and verify, each in its own sub-agent. Use only when the user or a /goal names /implement."
argument-hint: "Which Issue to implement, or what to build?"
model: sonnet
effort: high
---

You are the **driving session**: you orchestrate, sub-agents implement, review, and verify. You hold each sub-agent's short report, the findings that go back to the next Iteration, and any deviations — that is the whole of your context, and it is what lets the run land inside one session. So you hand paths, and the sub-agent that needs a document reads it. While a sub-agent runs, waiting is the work.

The run is a loop over the whole Spec, at most three **Iterations** ([ADR-0072](../../docs/adr/0072-implement-is-a-loop-of-implement-review-verify.md)):

1. **Implement** — a fresh `skills:implementer` makes the change the Spec asks for, or fixes what the last Iteration found.
2. **Review** — `/code-review` judges the diff on its Standards axis: the repo's Coding standards and the design principles. A finding sends the run back to 1.
3. **Verify** — a fresh `skills:verifier` checks the change does what the Spec asks: the Spec read against the diff, the build and the whole test suite, and the Spec's Hand checks. A finding sends the run back to 1.

The run lands when one Iteration passes both Review and Verify. The Implementer and the Verifier are pinned in their agent files (`agents/implementer.md`, `agents/verifier.md` at the plugin root) to Sonnet at high effort, because the Spec was decided before they started; the Reviewer `/code-review` starts is pinned to Opus at high ([ADR-0049](../../docs/adr/0049-agents-are-pinned-in-their-agent-files.md)).

Every sub-agent closes leftover gaps from the documents it was handed and the code. See [ADR-0026](../../docs/adr/0026-implement-agents-close-leftover-gaps.md).

No sub-agent pushes, publishes, or changes a live system; work that needs that **halts**. The run reaches outside the local checkout twice: the **claim** on its Issue, so concurrent runs skip that Issue, and [the push](#the-push) of `<base>` once it has landed. The closing reference its landing commit carries is how the Tracker learns the work is done. Under [benchmark mode](#benchmark-mode) it reaches outside zero times. See [ADR-0028](../../docs/adr/0028-implement-claims-its-issue-and-pushes-only-what-lands.md) and [ADR-0001](../../docs/adr/0001-each-repo-describes-its-tracker.md).

## Process

### 1. Enter the worktree

Issues live in the repo's **Tracker**: carry out each operation on one — file, read, list, rewrite, set status, comment, link, claim, close — as `.agents/refs/tracker.md` says, or as [setup/LOCAL.md](../setup/LOCAL.md) says when the repo has no ref.

The argument is an Issue reference — normally an Issue in `ready-for-agent` — or a description of the change, which touches no Tracker; an issue outside this repo's Tracker is read as a description. A description is the Spec: it gets no interview, and the user who wants one runs `/grill-with-docs` first. Read the Issue. Derive `<slug>`: the Issue's run slug as the Tracker ref gives it, otherwise a kebab-case slug from the description.

When this session already drives the run for `<slug>` and a sub-agent it dispatched for that run has not reported yet, this invocation is a repeat and the run is still going: say so, and keep waiting for that report. A repeat claims, resets, and dispatches nothing ([ADR-0064](../../docs/adr/0064-a-repeated-implement-command-waits-for-its-run.md)).

`<base>` is the **base branch**: `git branch --show-current` in the original directory when this command starts, read again on a resume. The run branches from it, is reviewed and verified against it, and lands back on it ([ADR-0055](../../docs/adr/0055-a-run-lands-on-the-branch-it-started-from.md)). If it is empty, **halt** — HEAD is detached. The main checkout's working tree is the user's and stays as you found it until step 3.

An Issue blocked by another Issue waits on it: while the blocker is open, stop before anything else and say it lands first — unless `<base>` already holds the blocker's closing reference, found as the Tracker ref says ([ADR-0047](../../docs/adr/0047-a-wayfinder-map-ends-in-one-or-more-specs.md)).

Then claim the Issue as the Tracker ref says. When the ref says another user holds it, stop and name them. A ref that gives no claim for Issues skips this.

Find worktrees with `git worktree list` (or the host's equivalent). The **run worktree** is the one whose branch is `<slug>` (or the name a host tool recorded). A prior run is **in flight** when that run worktree exists, when branch `<slug>` exists, or when any linked worktree contains `.agents/runs/<slug>/`.

- **In flight** → a run worktree whose lock names a live process is another session's run: stop and say so. Otherwise:
  - Put the session's working directory on the run worktree's path. When the branch exists without a worktree, `git -c checkout.workers=0 worktree add` at `.agents/worktrees/<slug>` on branch `<slug>` first (ensure `.agents/worktrees/` is ignored; prefer a local ignore when the repo uses one).
  - `git reset --hard && git clean -fd` drops whatever a halted sub-agent left behind. If the host refuses the reset, `git stash push -u` and name the stash in the final report.
  - Resume at Iteration 1 of step 2. The branch's commits are the work so far; the Implementer builds on them.
- **Fresh** → open a worktree for this run, put the session's working directory inside it, then `git reset --hard <base>` so the run starts from the `<base>` you actually have — the new branch has no commits of its own yet:
  - If this host has a tool that **creates the worktree and moves the session into it**, use that tool — even when its path is not the fallback below. Decide from the tool list you already have rather than searching the host's CLI or docs. Record the branch name it chose when that name is not `<slug>`.
  - Otherwise ensure the consuming repo ignores `.agents/worktrees/` (add the line if missing; prefer a local ignore when the repo uses one), then `git -c checkout.workers=0 worktree add` at `.agents/worktrees/<slug>` on branch `<slug>`, and change the session's working directory there.

The session must work *inside* the run worktree for the rest of the run — creating a worktree alone is not enough. Run every command from there as a **plain** command: every argument spelled out, and files written with the host's file tools. A host that isolates the session in its worktree refuses a command it cannot prove stays inside, such as one with a `cd` or `git -C`, a shell variable, `$(…)`, or a heredoc, and says how to split it. Scope every search to the worktree, and name it in every sub-agent prompt as the only directory the agent works in. On a host whose shell starts every command in the original directory, resolve the worktree's absolute path once with `pwd` inside it and begin every command with `cd <that path> &&`. An `/implement` prompt that explicitly waives the worktree takes the branch in [Worktree waived](#worktree-waived) instead.

Before leaving this step, when `.agents/runs/<slug>/spec.md` is missing, write **the Spec** to it — the Issue's title as an H1 and its body, or the description as the argument gave it — and nothing else, then commit it as `spec: <slug>`. The commit keeps it through a resume's reset. From here on every sub-agent reads that copy, and a resume reads it rather than the Issue.

`<scratch>` is `.agents/runs/<slug>/scratch/`, by absolute path: the Verifier's throwaway scripts, screenshots, and transcripts. Create it when it is missing, with a `.gitignore` inside that holds `*`, so no commit sweeps it in. The land deletes it with the run folder; a halt leaves it.

### 2. Loop

Run Iterations, numbered from 1, until one passes both Review and Verify. Each Iteration is the three parts below, in order.

#### Implement

Hold `git rev-parse HEAD` as `<before>`, then dispatch a fresh `skills:implementer` with a prompt of paths and section names — it reads what is behind them:

- the Spec, and `<base>`, the branch its tests are measured against
- `CONTEXT.md` and any ADR covering the area it touches, for vocabulary
- the Coding standards, found the same way `/code-review` finds them — `.agents/refs/` first, then a root-level coding-standards or contributing file when that is what the repo has; only documents that say how code should be written — when those exist
- the design principles, [PRINCIPLES.md](../code-review/PRINCIPLES.md) in the `code-review` skill's directory by absolute path — the Review judges the diff by them and by the Coding standards
- the Spec's Testing Decisions section, when it has one, which governs what it tests, and the testing documents it names
- from Iteration 2 on: every finding the last Review or Verify reported, verbatim, and every finding an earlier Iteration declined, with its reason
- the deviations reported so far, verbatim, when there are any
- its Iteration number and the limit of three, and the report format below

Require of it: **its build and the tests closest to its change passing before it finishes**, and its work committed. The whole suite is the Verifier's to run. From Iteration 2 on, it fixes every Verify finding, and fixes each Review finding or declines it on its `declined:` line with the reason. A Review finding that contradicts the Spec is declined: the Spec wins.

Its entire response is four lines:

```
status: done | blocked
built: <one sentence on what now works, or what it fixed>
declined: <each Review finding left as it is, with why — or "none">
deviations: <what contradicts the Spec, or "none">
```

Then **check it structurally**: `git rev-parse HEAD` differs from `<before>` and `git status` is clean, or every finding it was handed is on its `declined:` line and HEAD has not moved. That is the whole check; read the diff only when it fails.

#### Review

**Run `/code-review` yourself** on the Standards axis alone, with `<base>` as the fixed point. Tell it that `.agents/runs/<slug>/` is run bookkeeping, not code under review, and hand it every finding declined so far with its reason: a declined finding is raised again only when the reason does not hold, and the report says why. Hold the Standards report; weigh it on the report alone.

Review passes when the report has no finding. Tell the user `Iteration <N>/3 — review: passed`, or `Iteration <N>/3 — review: <count> findings`, then go on without waiting: a passed Review goes to Verify; findings start the next Iteration at Implement, with Verify skipped.

#### Verify

Dispatch a fresh `skills:verifier` with a prompt of paths: the Spec, `<base>`, the Spec's Testing Decisions section when it has one, `<scratch>`, and the report format below.

```
status: passed | failed | blocked
deviations: <failures red on <base> too, tests that passed only on a re-run, Hand checks skipped with what they need — or "none">
findings:
- <one line per Spec requirement missing, partial, or wrong; scope the Spec did not ask for; a red test; a Hand check that failed twice — or "none">
```

Tell the user `Iteration <N>/3 — verify: passed`, or `Iteration <N>/3 — verify: <count> findings`. `passed` goes to step 3. `failed` starts the next Iteration at Implement.

#### The limit

An Iteration that ends in findings when it is Iteration 3 **halts** the run, and the halt report quotes those findings.

A `blocked` report, a failed structural check, or any result that is not the report — a question, a progress note, a pause to wait on a background run — earns exactly one retry, for the Implementer and the Verifier alike, and the retry is not a new Iteration. When the host can resume the same agent, resume it once with one line: the work is still yours to finish; return the report. Otherwise `git reset --hard && git clean -fd`, then re-dispatch the same agent with the same prompt, appending a test or environment failure in its own words, or that the previous run returned something other than the report. Commits it made survive that reset. A second failure **halts** the run.

Carry every deviations line that is not `none`, verbatim, into later dispatches and the final report.

### 3. Land the branch

Commit anything still uncommitted; `git rebase` refuses a dirty tree. Each remaining command runs where its branch is checked out, and that constraint fixes the order. `<branch>` is `<slug>`, or the name you recorded when a host tool chose another:

1. From the worktree, still on the branch: hold `git merge-base HEAD <base>` as `<fork>` and `git rev-parse <base>` as `<onto>`, then `git rebase <onto>`. A conflict: read and follow [`/resolving-merge-conflicts`](../resolving-merge-conflicts/SKILL.md) (the branch lives here, so only the worktree can rebase it). Later items build on `<onto>`: other sessions can land on `<base>` while this run works, and a commit built on the moved `<base>` would undo what they landed.
   - When the rebase replayed the branch onto commits `<base>` gained during the run, the last Verify no longer covers the code that lands: dispatch the Verifier again, as step 2 says. `passed` goes on. `failed` starts the next Iteration at Implement, and the run comes back here when that Iteration passes. When the run already reached Iteration 3, `failed` **halts** it.
   - Skip that Verify when no build, test, or Hand check reads anything `<base>` gained: every path `git diff --name-only <fork> <onto>` lists is Markdown or sits under `.agents/` — another run's ADR, its glossary edit, its retro edit to `.agents/refs/tracker.md` — and no project file, build script, test, or app the Verify skill launches reads that file. The last Verify then still holds. Any other path, or any doubt about one, and the Verify runs. A skip goes in the final report: the range `<fork>..<onto>` you compared, and why none of its files is read.
2. Still in the worktree: delete the whole `.agents/runs/<slug>/` directory, the Spec and `<scratch>` with it, and commit the deletion. The Prototype folder the Spec points at stays ([ADR-0018](../../docs/adr/0018-prototypes-live-under-agents-prototypes.md)). Then build [the landing commit](#the-landing-commit) from that tree, on top of `<onto>`, leaving the branch where it is: `git commit-tree HEAD^{tree} -p <onto> -F -`, with the message on stdin. Hold the hash it prints as `<landing>`.
3. Return the session to the original directory, keeping the branch and its commits — a host leave-worktree action when it does exactly that, otherwise change directory yourself.
4. From the original directory, on `<base>`: `git merge --ff-only <landing>`. (`<base>` lives here, so only the original directory can fast-forward it.) `<landing>`'s parent is `<onto>`, so this is a fast-forward only while `<base>` is still `<onto>`. This step is done when that merge has succeeded, `git worktree remove <path>` has run — never forced; a lock means another session still has it — and the branch is deleted. Delete the branch with `git branch -D <branch>` once `git diff --quiet <branch> <base>` succeeds: its commits never reach `<base>`, so `-d` refuses it, and the empty diff shows `<base>` holds all of its work. When the diff is not empty, keep the branch and name it in the final report. When the merge errors, `<base>` moved: re-enter the worktree, drop the deletion commit with `git reset --hard HEAD~1` — it holds only the deletion, so the Spec comes back for the Verifier — then go through 1 to 3 again and retry this merge.

The final report says how many Iterations the run took, quotes every `declined:` line that was not `none` and every deviations line, and names each Hand check the Verifier skipped and what it needs.

### 4. Push

Run [the push](#the-push).

### 5. Retrospective

Read and follow [`/retro`](../retro/SKILL.md) only when the run had a deviations line that was not `none`, a retried or halted agent, or a second Iteration; otherwise the final report says retro was skipped as nothing went wrong. When it committed and step 4's push went out, run [the push](#the-push) again.

## The landing commit

The landing commit is the one commit the run leaves on `<base>`: the run's whole change, without the run folder ([ADR-0062](../../docs/adr/0062-an-implement-run-lands-as-one-commit.md)). Write its message before the Spec is deleted:

- **Subject**: what the change does, ending with the Issue's reference — `Roles are given from the Person (#104)`. Write it from the Spec, not from the Issue's title, which often names the problem. Follow the commit style the repo's `AGENTS.md`, `CLAUDE.md`, or Coding standards document, when they document one. A run from a description has no reference.
- **Body**: the Issue's closing reference as the Tracker ref gives it; when the ref gives none, the final report names the Issue for the user to close.

## The push

The push sends `<base>` from the original directory: in step 4, once the landing commit is on it, so the CI run it starts carries the landing commit's subject; and in step 5, when `/retro` committed ([ADR-0028](../../docs/adr/0028-implement-claims-its-issue-and-pushes-only-what-lands.md)). Skip both when the repo's `AGENTS.md` or `CLAUDE.md` says implement runs do not push, or when `git remote` lists nothing. Otherwise:

- `<base>` tracks a remote branch: `git push <remote> <base>:<branch>`, with `<remote>` from `git config branch.<base>.remote` and `<branch>` from `git config branch.<base>.merge`.
- `<base>` tracks nothing: `git push -u origin <base>`. A repo with no `origin` skips the push.

The push sends `<base>` as it stands, commits the user had not pushed yet included. It is a plain push with hooks running — never `--force`, `--force-with-lease`, or `--no-verify`. A refused or failed push gets no retry and is not a halt: the run has landed, and nothing is left to resume.

The run's last lines name the landing commit, then say what each push sent and to which remote branch. When it pushed nothing, they say why: the `AGENTS.md` or `CLAUDE.md` line, no remote, or no `origin`. When a push failed, they quote the error and name the commits that wait on this machine — the landing commit and `/retro`'s after a failed first push, `/retro`'s after a failed second — for the user to pull and push.

## Benchmark mode

The `benchmark/` runner measures what a run costs. It exports `SKILLS_BENCHMARK=1` and `SKILLS_BENCHMARK_LOG` and names `SKILLS_BENCHMARK=1` in the session's system prompt, so the mode is on when your system prompt says so and costs no call to find out. Without that line, skip this section ([ADR-0066](../../docs/adr/0066-a-benchmark-run-writes-nothing-outside-its-checkout.md)).

In benchmark mode every outward write is a **no-op**: the claim in step 1 and the push in steps 4 and 5 each run `bench-log "<step>: <the command it would have run>"` instead, and the run goes on as though that write succeeded. Tracker reads stay. Every sub-agent prompt gets one more line: this is a benchmark run, so a `gh` write or a `git push` is a `bench-log` line. The final report says each push was a no-op.

## Worktree waived

The run folder lives at `.agents/runs/<slug>/` in the checkout, and there is nothing to enter, exit, or remove. Step 1 skips opening a worktree. Step 3 drops the return-to-original-directory step and `git worktree remove`: rebase on the branch, make the deletion commit and `<landing>` there, check out `<base>` yourself, then fast-forward to `<landing>`. That merge is done when it succeeds and the branch is deleted as step 3 says. When it errors, `<base>` moved: check out the branch, drop the deletion commit as step 3 says, go through items 1 and 2 of step 3 again, check out `<base>` yourself, and retry the merge. A run in flight is branch `<slug>`, or `.agents/runs/<slug>/` in this checkout.

## Work in another repository

The worktree, the review diff, the land, and the push cover this repository only. Work a Spec puts in another repository goes on a branch named `<slug>` there, committed by the Implementer and never pushed; the final report names the repository, the branch, and what sits on it.

## Halting

A halt is non-destructive and it is the end of the session. Leave the Spec, the branch, and the run worktree exactly as they are — the work is committed, and the run is resumable only because nothing was cleaned up. Report why the run stopped: the Iteration, the part — Implement, Review, or Verify — and why it did not finish. Quote a test or environment failure, and the findings an Iteration 3 left. For a result that was not the report, say the agent did not finish.

Re-invoking `/implement` with the same argument picks the run back up at Iteration 1, as step 1 says, with three Iterations again.
