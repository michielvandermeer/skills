---
name: implement
description: "Implement a spec by slicing it into steps, then a loop of implement, review, and verify, each in its own sub-agent. Use only when the user or a /goal names /implement."
argument-hint: "Which Issue to implement, or what to build?"
model: sonnet
effort: high
---

You are the **driving session**: you orchestrate, sub-agents plan, implement, review, and verify. You hold the Step index, each sub-agent's short report, the findings that go back to the next Iteration, and any deviations — that is the whole of your context, and it is what lets a Spec of any size land inside one session. So you hand paths, and the sub-agent that needs a document reads it. While a sub-agent runs, waiting is the work.

A **Planner** first slices the Spec into **Steps**, each small enough for one fresh agent; about half of Specs are one Step. Then the run is a loop over the whole Spec, at most three **Iterations** ([ADR-0072](../../docs/adr/0072-implement-plans-steps-then-loops-implement-review-verify.md)):

1. **Implement** — on a **building Iteration**, a fresh `skills:implementer` builds each Step in order; on a **fixing Iteration**, a single fresh Implementer fixes the findings it starts from. Iteration 1 builds and every later one fixes, except that a resume from a [Halt record](#halting) makes Iteration 1 a fixing one too.
2. **Review** — `/code-review` judges the diff on its Standards axis: the repo's Coding standards and the design principles. A **Hard violation** sends the run back to 1; a **Judgement call** waits for the next Implementer, or the final report. On a fixing Iteration, Review reads only the fix.
3. **Verify** — a fresh `skills:verifier` checks the change does what the Spec asks: the Spec read against the diff, the build and the whole test suite, and the Spec's Hand checks. A finding sends the run back to 1.

The run lands when one Iteration passes both Review and Verify. The Planner, the Implementer, and the Verifier are pinned in their agent files (`agents/planner.md`, `agents/implementer.md`, `agents/verifier.md` at the plugin root) to Sonnet at high effort, because the Spec was decided before they started; the Reviewer `/code-review` starts is pinned to Opus at high ([ADR-0049](../../docs/adr/0049-agents-are-pinned-in-their-agent-files.md)).

Every sub-agent closes leftover gaps from the documents it was handed and the code. See [ADR-0026](../../docs/adr/0026-implement-agents-close-leftover-gaps.md).

No sub-agent pushes, publishes, or changes a live system; work that needs that **halts**. The run reaches outside the local checkout twice: the **claim** on its Issue, so concurrent runs skip that Issue, and [the push](#the-push) of `<base>` once it has landed. The closing reference its landing commit carries is how the Tracker learns the work is done. Under [benchmark mode](#benchmark-mode) it reaches outside zero times. See [ADR-0028](../../docs/adr/0028-implement-claims-its-issue-and-pushes-only-what-lands.md) and [ADR-0001](../../docs/adr/0001-each-repo-describes-its-tracker.md).

## Process

### 1. Enter the worktree

Issues live in the repo's **Tracker**: carry out each operation on one — file, read, list, rewrite, set status, comment, link, claim, close — as `.agents/refs/tracker.md` says, or as [setup/LOCAL.md](../setup/LOCAL.md) says when the repo has no ref.

The argument is an Issue reference — normally an Issue in `ready-for-agent` — or a description of the change, which touches no Tracker; an issue outside this repo's Tracker is read as a description. A description is the Spec: it gets no interview, and the user who wants one runs `/grill-with-docs` first. Read the Issue. Derive `<slug>`: the Issue's run slug as the Tracker ref gives it, otherwise a kebab-case slug from the description.

When this session already drives the run for `<slug>` and a sub-agent it dispatched for that run has not reported yet, this invocation is a repeat and the run is still going: say so, and keep waiting for that report. A repeat claims, resets, and dispatches nothing ([ADR-0064](../../docs/adr/0064-a-repeated-implement-command-waits-for-its-run.md)).

`<base>` is the **base branch**: `git branch --show-current` in the original directory when this command starts, read again on a resume. The run branches from it, is reviewed and verified against it, and lands back on it ([ADR-0055](../../docs/adr/0055-a-run-lands-on-the-branch-it-started-from.md)). If it is empty, **halt** — HEAD is detached. The main checkout's working tree is the user's and stays as you found it until step 4.

An Issue blocked by another Issue waits on it: while the blocker is open, stop before anything else and say it lands first — unless `<base>` already holds the blocker's closing reference, found as the Tracker ref says ([ADR-0047](../../docs/adr/0047-a-wayfinder-map-ends-in-one-or-more-specs.md)).

Then claim the Issue as the Tracker ref says. When the ref says another user holds it, stop and name them. A ref that gives no claim for Issues skips this.

Find worktrees with `git worktree list` (or the host's equivalent). The **run worktree** is the one whose branch is `<slug>` (or the name a host tool recorded). A prior run is **in flight** when that run worktree exists, when branch `<slug>` exists, or when any linked worktree contains `.agents/runs/<slug>/`.

- **In flight** → a run worktree whose lock names a live process is another session's run: stop and say so. Otherwise:
  - Put the session's working directory on the run worktree's path. When the branch exists without a worktree, `git -c checkout.workers=0 worktree add` at `.agents/worktrees/<slug>` on branch `<slug>` first (ensure `.agents/worktrees/` is ignored; prefer a local ignore when the repo uses one).
  - `git reset --hard && git clean -fd` drops whatever a halted sub-agent left behind. If the host refuses the reset, `git stash push -u` and name the stash in the final report.
  - When `.agents/runs/<slug>/` holds Step files (`[0-9][0-9]-*.md`), the Steps are already planned: skip step 2 and resume Iteration 1 of step 3. With a Halt record at `.agents/runs/<slug>/halt.md`, read it and hold what it lists as the last Iteration's report, the Judgement calls held, the declines, and the deviations so far; and start a fixing Iteration at its Implement. Without one, start a building Iteration at the lowest-numbered Step whose `Status:` is not `done`, or at its Review when every Step reads `done`. With no Step files, continue at step 2. Whichever applies, it starts after **Resume lines** below. The branch's commits are the work so far; the Implementer builds on them.
- **Fresh** → open a worktree for this run, put the session's working directory inside it, then `git reset --hard <base>` so the run starts from the `<base>` you actually have — the new branch has no commits of its own yet:
  - If this host has a tool that **creates the worktree and moves the session into it**, use that tool — even when its path is not the fallback below. Decide from the tool list you already have rather than searching the host's CLI or docs. Record the branch name it chose when that name is not `<slug>`.
  - Otherwise ensure the consuming repo ignores `.agents/worktrees/` (add the line if missing; prefer a local ignore when the repo uses one), then `git -c checkout.workers=0 worktree add` at `.agents/worktrees/<slug>` on branch `<slug>`, and change the session's working directory there.

The session must work *inside* the run worktree for the rest of the run — creating a worktree alone is not enough. Run every command from there as a **plain** command: every argument spelled out. A host that isolates the session in its worktree refuses a command it cannot prove stays inside, such as one with a `cd` or `git -C`, a shell variable, `$(…)`, or a heredoc, and says how to split it. Every file the session reads, edits, or writes goes through the host's file tools, addressed by an absolute path under the worktree; a repo-relative path, such as a Footprint entry, is joined to the worktree's path, and a file in another repository, named by absolute path, is the one exception. Scope every search to the worktree, and name it in every sub-agent prompt as the only directory the agent works in. On a host whose shell starts every command in the original directory, resolve the worktree's absolute path once with `pwd` inside it and begin every command with `cd <that path> &&`. An `/implement` prompt that explicitly waives the worktree takes the branch in [Worktree waived](#worktree-waived) instead.

Before leaving this step, when `.agents/runs/<slug>/spec.md` is missing, write **the Spec** to it — the Issue's title as an H1 and its body, or the description as the argument gave it — and nothing else, then commit it as `spec: <slug>`. Every commit a run makes runs the repo's hooks, and no commit passes `--no-verify`: a repo whose hook would refuse run bookkeeping exempts `.agents/runs/` in the hook itself. A refused `spec:` commit halts the run before the Planner ([Halting](#halting)); the resume's reset deletes the uncommitted copy, so this step writes it fresh from the Issue, a first write and not a rewrite. The commit keeps the copy through a resume's reset. From here on every sub-agent reads that copy. A run never rewrites it and a resume never builds from the Issue's body, which it uses only for the comparison in **Resume lines** below, so a changed Spec is built by deleting the run's branch and worktree and running `/implement` again.

`<precheck>` is the repo's **Pre-review check**: the command on the line that starts `Pre-review check:` in `AGENTS.md` or `CLAUDE.md`, with `<base>` filled in. Without that line there is none, and every step below that names it skips it.

`<standards>` is the Coding standards' paths, found the same way `/code-review` finds them — `.agents/refs/` first, then a root-level coding-standards or contributing file when that is what the repo has; only documents that say how code should be written; none when the repo has none. `<principles>` is the absolute path to [PRINCIPLES.md](../code-review/PRINCIPLES.md) in the `code-review` skill's directory, built from the folder the host loaded this skill from and confirmed with `ls`. The Planner copies what bears on each Step from both into its Step file ([ADR-0080](../../docs/adr/0080-the-planner-copies-each-steps-rules-into-its-step-file.md)).

`<scratch>` is `.agents/runs/<slug>/scratch/`, by absolute path: the Verifier's throwaway scripts, screenshots, and transcripts. Create it when it is missing, with a `.gitignore` inside that holds `*`, so no commit sweeps it in. The land deletes it with the run folder; a halt leaves it.

**Resume lines.** On an **In flight** run other than a repeat, run `python3 <skill>/resume.py <slug> --spec <spec> --halt <halt>` from the run worktree, once `<scratch>` exists, as a plain command with absolute paths: `<skill>` is this skill's folder, [resume.py](resume.py) is the script, `<spec>` is `.agents/runs/<slug>/spec.md`, and `<halt>` is `.agents/runs/<slug>/halt.md`, whether or not that file exists. When `python3` is not found, run it with `python`; when neither runs, tell the user the resume lines could not be printed and go on. When the argument is an Issue, first put its body alone, without the title, status, labels, or comments, in `<scratch>/issue-body.md`, and add `--issue <scratch>/issue-body.md`. Where the Tracker ref's Read operation is a command, run it narrowed to the body field and redirect its output to that file. Otherwise write the body with the host's file tools, character for character as Read returns it. The script compares and counts, prints `Resuming from the Halt record: <count> findings` and the Issue-changed line when each applies, and prints nothing otherwise. Its output is the whole message to the user: say nothing more about either line. Then go on to step 2 or 3 as the **In flight** branch says. A changed Issue never stops, asks, or halts the run, and the Spec copy is never rewritten.

### 2. Plan the Steps

Dispatch a `skills:planner`. Give it the Spec's path, `<slug>`, the absolute path to [STEPS.md](STEPS.md) in this skill's directory, `<standards>`, `<principles>`, and the run worktree's absolute path, as the only directory it works in — those six and nothing else. It reads the slicing rules itself, writes one Step file per Step to `.agents/runs/<slug>/`, and commits them before returning, so the resets later in the run cannot delete a Step not yet built. When `git status` still shows Step files afterwards, commit them yourself as `plan: <slug>`. A hook that refused the Planner's commit leaves them there, so this is the second attempt, and its refusal halts the run ([Halting](#halting)); a resume then finds no committed Step files and runs the Planner again.

It returns the index and nothing else — one line per Step, `NN | title | one-line deliverable` — with one line before it only when its commit was refused. Tell the user how many Steps it planned, with their titles.

The plan succeeded when that reply is the index, with or without the one refused-commit line before it, and `.agents/runs/<slug>/` holds Step files, committed or left uncommitted by a refused commit. Otherwise the Planner gets the retry in [The limit](#the-limit), and a second failure **halts** the run. The commit above is your only write in this step: the Step files are the Planner's to write.

### 3. Loop

Run Iterations, numbered from 1, until one passes both Review and Verify. Each Iteration is the three parts below, in order.

#### Implement

On a building Iteration, run each Step in `NN` order, skipping a Step whose `Status:` already reads `done`; its Implement is done when every Step file, `.agents/runs/<slug>/[0-9][0-9]-*.md`, reads `Status: done`. On a fixing Iteration, run one Implementer for the findings, with no Step file.

Hold `git rev-parse HEAD` as `<start>` before the Iteration's first dispatch. On a resume from a Halt record, `<start>` is instead the commit that last wrote it, `git log -1 --format=%H -- .agents/runs/<slug>/halt.md`, so Review also reads what was committed after the halt. For each dispatch, hold `git rev-parse HEAD` as `<before>`, then dispatch a fresh `skills:implementer` with a prompt of paths and section names — it reads what is behind them:

- the run worktree's absolute path, as the only directory it works in
- the Spec, and `<base>`, the branch its tests are measured against
- on a building Iteration: its own Step file, and an instruction to read the `## Outcome` of every lower-numbered Step file before starting
- `CONTEXT.md` and any ADR covering the area it touches, for vocabulary
- `<standards>`, for code beyond its Step file's `## Coding standards` section
- the Spec's Testing Decisions section, when it has one, which governs what it tests, and the testing documents it names
- on a fixing Iteration: every Hard violation and Verify finding the last Iteration reported, and every Judgement call held, verbatim; and every finding an earlier Iteration declined, with its reason
- on a resume from a Halt record: that commits after `<start>` are progress, and a finding they already answer goes on its `declined:` line, naming the commit
- `<precheck>`, when the repo names one
- the deviations reported so far, verbatim, when there are any
- its Iteration number and the limit of three, on a building Iteration its Step number and the total, and the report format below

Require of it: **its build, the tests closest to its change, and `<precheck>` passing before it finishes**, and its work committed. The whole suite is the Verifier's to run. On a building Iteration, it builds every project on its Footprint's `Projects:` line, appends a short `## Outcome` to its Step file (what it built, where the code differed from the Footprint, and what a later Step needs to know), sets that file's `Status:` to `done`, and commits the file with its code. On a fixing Iteration, it fixes every Verify finding, and fixes each Review finding or declines it on its `declined:` line with the reason. A Review finding that contradicts the Spec is declined: the Spec wins.

Its entire response is four lines:

```
status: done | blocked
built: <one sentence on what now works, or what it fixed>
declined: <each Review finding left as it is, with why — or "none">
deviations: <what contradicts the Spec or changes a later Step, or "none">
```

Then **check it structurally**: `git rev-parse HEAD` differs from `<before>` and `git status` is clean, or every finding it was handed is on its `declined:` line and HEAD has not moved. On a building Iteration, `grep '^Status:'` on its Step file also reads `done`. Then run `<precheck>` from the run worktree, with its output bounded to the findings; it passes when it exits 0. When its `deviations:` line names a stray path, an edit it found outside the worktree and redid there, hold the path for the final report and leave the main checkout alone. That is the whole check; read the diff only when it fails. A `<precheck>` that still lists findings after the retry is no halt: the run goes on to Review, and the Review prompt carries those findings ([ADR-0078](../../docs/adr/0078-an-implement-run-runs-the-pre-review-check-before-review.md)). Tell the user `Step <NN>/<total> — <title>: done` after each Step passes it.

#### Review

**Run `/code-review` yourself** on the Standards axis alone. The fixed point is `<base>` on a building Iteration, so the first Review reads the whole change. On a fixing Iteration it is `<start>`, so the Review reads only the fix; when HEAD has not moved from `<start>` because every finding was declined, it is `<base>` again, and the Review judges the declines alone. Tell it:

- the Spec's path, `.agents/runs/<slug>/spec.md`
- that `.agents/runs/<slug>/` is run bookkeeping, not code under review
- that only agents read its report
- any `<precheck>` findings the last Implementer left, verbatim, to judge as Hard violations or not
- every finding declined so far with its reason: a declined finding is raised again only when the reason does not hold, and the report says why
- on a fixing Iteration, every finding the last Implementer was handed, to judge as fixed or declined, with the fix itself judged against the standards

Check the Standards report for its closing line before weighing it: the report's last line reads `Standards: <h> hard violations, <j> judgement calls`, and a line of another shape, or one mid-report, is not it. The line proves the report is complete; it does not decide the result, so a line that undercounts never turns a Hard violation into a pass. A report with no closing line, or a result that is not a report at all (empty, cut off, a question, a progress note), is a failed Review and earns the retry in [The limit](#the-limit).

Hold the Standards report; weigh it on the report alone. `/code-review` opens each finding with `Hard violation:` or `Judgement call:`. Hold its Judgement calls with any held from earlier Iterations until the next Implementer is handed them.

Review passes when its complete report has no Hard violation. Tell the user `Iteration <N>/3 — review: passed`, with `(<j> judgement calls)` after it when there are any, or `Iteration <N>/3 — review: <h> hard violations, <j> judgement calls`, then go on without waiting: a passed Review goes to Verify; a Hard violation starts the next Iteration at Implement, with Verify skipped.

#### Verify

Dispatch a fresh `skills:verifier` with a prompt of paths: the run worktree's absolute path, as the only directory it works in, the Spec, `<base>`, the Spec's Testing Decisions section when it has one, `<scratch>`, and the report format below.

```
status: passed | failed | blocked
deviations: <failures red on <base> too, tests that passed only on a re-run, Hand checks skipped with what they need — or "none">
findings:
- <one line per Spec requirement missing, partial, or wrong; scope the Spec did not ask for; a red test; a Hand check that failed twice — or "none">
```

Tell the user `Iteration <N>/3 — verify: passed`, or `Iteration <N>/3 — verify: <count> findings`. `passed` goes to step 4. `failed` starts the next Iteration at Implement.

#### The limit

An Iteration 3 that ends on a Hard violation or a Verify finding **halts** the run, and the halt report quotes those findings. Judgement calls alone never halt a run.

A `blocked` report, a failed structural check, or any result that is not the report — a question, a progress note, a pause to wait on a background run — earns exactly one retry, for the Planner, each Implementer, the Verifier, and the Review alike, and the retry is not a new Iteration. When the host can resume the same agent, resume it once with one line: the work is still yours to finish; return the report. Otherwise `git reset --hard && git clean -fd`, then re-dispatch the same agent with the same prompt, appending a test or environment failure in its own words, or that the previous run returned something other than the report. Commits it made survive that reset. The Review changes no code, so its retry skips the reset: it runs the same Standards Review with the same inputs, resuming the same reviewer once when the host can, otherwise running `/code-review` again with the same fixed point and the same things told to it. A second failure **halts** the run.

Carry every deviations line that is not `none`, verbatim, into later dispatches and the final report.

### 4. Land the branch

Commit anything still uncommitted; `git rebase` refuses a dirty tree. Each remaining command runs where its branch is checked out, and that constraint fixes the order. `<branch>` is `<slug>`, or the name you recorded when a host tool chose another:

1. From the worktree, still on the branch: hold `git merge-base HEAD <base>` as `<fork>` and `git rev-parse <base>` as `<onto>`, then `git rebase <onto>`. A conflict: read [`resolving-merge-conflicts/SKILL.md`](../resolving-merge-conflicts/SKILL.md) and follow it (the branch lives here, so only the worktree can rebase it). Later items build on `<onto>`: other sessions can land on `<base>` while this run works, and a commit built on the moved `<base>` would undo what they landed.
   - When the rebase replayed the branch onto commits `<base>` gained during the run, the last Verify no longer covers the code that lands: dispatch the Verifier again, as step 3 says, with `<fork>..<onto>` added to its prompt. That range makes it a reduced Verify: the build and the whole suite run, and a Hand check runs only when a path `git diff --name-only <fork> <onto>` lists is one its journey reads ([ADR-0029](../../docs/adr/0029-green-is-measured-against-the-base-branch.md)). `passed` goes on. `failed` starts the next Iteration at Implement, and the run comes back here when that Iteration passes. When the run already reached Iteration 3, `failed` **halts** it.
   - Skip that Verify when no build, test, or Hand check reads anything `<base>` gained: every path `git diff --name-only <fork> <onto>` lists is Markdown or sits under `.agents/` — another run's ADR, its glossary edit, its retro edit to `.agents/refs/tracker.md` — and no project file, build script, test, or app the Verify skill launches reads that file. The last Verify then still holds. Any other path, or any doubt about one, and the reduced Verify runs. A skip goes in the final report: the range `<fork>..<onto>` you compared, and why none of its files is read.
2. Still in the worktree: delete the whole `.agents/runs/<slug>/` directory, the Spec, the Step files, and `<scratch>` with it, and commit the deletion. A hook that refuses that commit halts the run with nothing landed ([Halting](#halting)); a resume finds every Step done and starts at Review. The Prototype folder the Spec points at stays ([ADR-0018](../../docs/adr/0018-prototypes-live-under-agents-prototypes.md)). Then build [the landing commit](#the-landing-commit) from that tree, on top of `<onto>`, leaving the branch where it is: `git commit-tree HEAD^{tree} -p <onto> -F -`, with the message on stdin. `git commit-tree` runs no hooks, and every commit whose tree it reuses already ran them. Hold the hash it prints as `<landing>`.
3. Return the session to the original directory, keeping the branch and its commits — a host leave-worktree action when it does exactly that, otherwise change directory yourself.
4. From the original directory, on `<base>`: `git merge --ff-only <landing>`. (`<base>` lives here, so only the original directory can fast-forward it.) `<landing>`'s parent is `<onto>`, so this is a fast-forward only while `<base>` is still `<onto>`. This step is done when that merge has succeeded, `git worktree remove <path>` has run — never forced; a lock means another session still has it — and the branch is deleted. Delete the branch with `git branch -D <branch>` once `git diff --quiet <branch> <base>` succeeds: its commits never reach `<base>`, so `-d` refuses it, and the empty diff shows `<base>` holds all of its work. When the diff is not empty, keep the branch and name it in the final report. When the merge errors, `<base>` moved: re-enter the worktree, drop the deletion commit with `git reset --hard HEAD~1` — it holds only the deletion, so the Spec comes back for the Verifier — then go through 1 to 3 again and retry this merge.

The final report says how many Steps the Planner made and how many Iterations the run took, quotes every `declined:` line that was not `none` and every deviations line, names each stray path an Implementer reported as a file to check in the user's main checkout, lists every Judgement call still held, which lands unfixed, and names each Hand check the Verifier skipped and what it needs.

### 5. Push

Run [the push](#the-push).

## The landing commit

The landing commit is the one commit the run leaves on `<base>`: the run's whole change, without the run folder ([ADR-0062](../../docs/adr/0062-an-implement-run-lands-as-one-commit.md)). Write its message before the Spec and the Step files are deleted:

- **Subject**: what the change does, ending with the Issue's reference — `Roles are given from the Person (#104)`. Write it from the Spec, not from the Issue's title, which often names the problem. Follow the commit style the repo's `AGENTS.md`, `CLAUDE.md`, or Coding standards document, when they document one. A run from a description has no reference.
- **Body**: each Step's title from the index, one per line, when the run had more than one Step. Then the Issue's closing reference as the Tracker ref gives it; when the ref gives none, the final report names the Issue for the user to close.

## The push

The push sends `<base>` from the original directory in step 5, once the landing commit is on it, so the CI run it starts carries the landing commit's subject ([ADR-0028](../../docs/adr/0028-implement-claims-its-issue-and-pushes-only-what-lands.md)). Skip it when the repo's `AGENTS.md` or `CLAUDE.md` says implement runs do not push, or when `git remote` lists nothing. Otherwise:

- `<base>` tracks a remote branch: `git push <remote> <base>:<branch>`, with `<remote>` from `git config branch.<base>.remote` and `<branch>` from `git config branch.<base>.merge`.
- `<base>` tracks nothing: `git push -u origin <base>`. A repo with no `origin` skips the push.

The push sends `<base>` as it stands, commits the user had not pushed yet included. It is a plain push with hooks running — never `--force`, `--force-with-lease`, or `--no-verify`. A refused or failed push gets no retry and is not a halt: the run has landed, and nothing is left to resume.

The run's last lines name the landing commit, then say what the push sent and to which remote branch. When it pushed nothing, they say why: the `AGENTS.md` or `CLAUDE.md` line, no remote, or no `origin`. When the push failed, they quote the error and name the landing commit, which waits on this machine, for the user to pull and push.

## Benchmark mode

The `benchmark/` runner measures what a run costs. It exports `SKILLS_BENCHMARK=1` and `SKILLS_BENCHMARK_LOG` and names `SKILLS_BENCHMARK=1` in the session's system prompt, so the mode is on when your system prompt says so and costs no call to find out. Without that line, skip this section ([ADR-0066](../../docs/adr/0066-a-benchmark-run-writes-nothing-outside-its-checkout.md)).

In benchmark mode every outward write is a **no-op**: the claim in step 1 and the push in step 5 each run `bench-log "<step>: <the command it would have run>"` instead, and the run goes on as though that write succeeded. Tracker reads stay. Every sub-agent prompt gets one more line: this is a benchmark run, so a `gh` write or a `git push` is a `bench-log` line. The final report says the push was a no-op.

## Worktree waived

The run folder lives at `.agents/runs/<slug>/` in the checkout, and there is nothing to enter, exit, or remove. The "run worktree" path every sub-agent is told is the checkout's own absolute path. Step 1 skips opening a worktree. Step 4 drops the return-to-original-directory step and `git worktree remove`: rebase on the branch, make the deletion commit and `<landing>` there, check out `<base>` yourself, then fast-forward to `<landing>`. That merge is done when it succeeds and the branch is deleted as step 3 says. When it errors, `<base>` moved: check out the branch, drop the deletion commit as step 4 says, go through items 1 and 2 of step 4 again, check out `<base>` yourself, and retry the merge. A run in flight is branch `<slug>`, or `.agents/runs/<slug>/` in this checkout.

## Work in another repository

The worktree, the review diff, the land, and the push cover this repository only. Work a Spec puts in another repository goes on a branch named `<slug>` there, committed by the Implementer that did it and never pushed; the final report names the repository, the branch, and what sits on it.

## Halting

A halt is non-destructive and it is the end of the session. Leave the Spec, the Step files, the branch, and the run worktree exactly as they are — the work is committed, and the run is resumable only because nothing was cleaned up. Report why the run stopped: that the Planner failed and why; or the Iteration, the part — Implement, Review, or Verify — with the Step's number and title on Iteration 1's Implement, and why it did not finish. Quote a test or environment failure, and the findings an Iteration 3 left. For a result that was not the report, say the agent did not finish; for a Review that failed twice to return a report with its closing line, say the Review returned no report.

A halt with findings — an Iteration 3 that ended on a Hard violation or a Verify finding, or the failed Verify after the land's rebase — first writes the **Halt record**, the one commit a halt makes. Write `.agents/runs/<slug>/halt.md`, replacing any earlier one, with four lists, each under its own `## ` heading, one `- ` bullet per item (`- none` for an empty list), all verbatim: the Hard violations and Verify findings that ended the run, the Judgement calls held, every finding declined with its reason, and the deviations so far. Commit that file alone as `halt: <slug>`. The halt report then says the Halt record holds the findings and that running `/implement` again hands them to an Implementer.

A halt on a Review with no report holds no findings, so it writes no Halt record and makes no `halt:` commit.

A hook that refuses one of the run-folder commits — `spec:`, `plan:`, `halt:`, or the deletion commit in step 4 — halts the run with no findings, so no Halt record is written unless the refused commit is `halt:`. The run neither retries the commit nor carries on uncommitted. The halt report names the refused commit, quotes the hook's output, and tells the user to exempt `.agents/runs/` in that hook and run `/implement` again. A refused `halt:` commit puts the findings that would have filled the Halt record in the report, verbatim, and says the record is not committed, so the next resume starts a building Iteration rather than a fixing one. A refused deletion commit says nothing landed.

Re-invoking `/implement` with the same argument picks the run back up where step 1 says, with three Iterations again: at the Planner when no Step file exists, otherwise in Iteration 1.
