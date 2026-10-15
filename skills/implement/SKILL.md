---
name: implement
description: "Build a Spec as a poteto-mode run and land it on this branch as one commit: route the Spec to a playbook, design before code, delegate to poteto-agents, verify on the matching surface, review with interrogate. Use only when the user or a /goal names /implement."
argument-hint: "Which Issue to implement, or what to build?"
model: opus
effort: high
---

You are the **Driving session** of a poteto-mode run whose brief is a Spec and whose exit is a landing ([ADR-0069](../../docs/adr/0069-an-implement-run-is-a-poteto-mode-playbook.md)). You own the playbook, `todo.md`, the trail, and every delegate; delegates write the code. The invocation is a full-autonomy grant: decide every call it covers, log each one in the trail, and report it. `AskUserQuestion` goes uncalled. The run reaches outside the local checkout twice, for the **claim** on its Issue and for [the push](LANDING.md#the-push) of `<base>` once it has landed; under [benchmark mode](#benchmark-mode), never ([ADR-0028](../../docs/adr/0028-implement-claims-its-issue-and-pushes-only-what-lands.md)).

## Process

### 0. Read poteto-mode

Read [`../poteto-mode/SKILL.md`](../poteto-mode/SKILL.md) in full, Principles index included. Its Non-negotiables, Autonomy, Subagents, Writing the reply, and Comments sections govern the whole run; this file adds only what a landing needs. Then prove the [Overlay](.agents/playbooks/implement.md): `node <plugin>/skills/poteto-mode/scripts/check-playbooks.mjs <plugin>/skills/implement`, both paths absolute, from the repository root.

Done when it prints that every project playbook matches. Any other line **halts**: report each line verbatim. The fix is to the Overlay or the playbook, never a guess at where a change belongs.

### 1. Intake and claim

Issues live in the repo's **Tracker**: carry out each operation on one as `.agents/refs/tracker.md` says, or as [setup/LOCAL.md](../setup/LOCAL.md) says when the repo has no ref.

The argument is an Issue reference, normally an Issue in `ready-for-agent`, or a description of the change, which touches no Tracker; an issue outside this repo's Tracker is read as a description. Read the Issue. Derive `<slug>`: the Issue's run slug as the Tracker ref gives it, otherwise a kebab-case slug from the description.

When this session already drives the run for `<slug>` and a delegate it dispatched has not reported yet, this invocation is a repeat and the run is still going: say so, and keep waiting for that report. A repeat claims, stashes, and dispatches nothing ([ADR-0064](../../docs/adr/0064-a-repeated-implement-command-waits-for-its-run.md)).

`<base>` is the **Base branch**: `git branch --show-current` in the original directory when this command starts, read again on a resume. The run branches from it, is verified against it, and lands back on it ([ADR-0055](../../docs/adr/0055-a-run-lands-on-the-branch-it-started-from.md)). Empty means a detached HEAD: **halt**. The main checkout's working tree is the user's and stays as you found it until the land.

An Issue blocked by another Issue waits on it: while the blocker is open, **halt** and say it lands first, unless `<base>` already holds the blocker's closing reference, found as the Tracker ref says ([ADR-0047](../../docs/adr/0047-a-wayfinder-map-ends-in-one-or-more-specs.md)).

Then claim the Issue as the Tracker ref says. Another user's claim **halts** the run and names them. A ref that gives no claim for Issues skips this, and a claim this user already holds is a no-op.

Done when the Issue is claimed, or the argument is a description.

### 2. Enter the run

Find worktrees with `git worktree list`. The **run worktree** is the one on branch `<slug>` (or the name a host tool recorded). A run is **in flight** when that worktree exists, when branch `<slug>` exists, or when `.agents/runs/<slug>/todo.md` in any linked worktree, this checkout included, still has an open item.

- **In flight.** A run worktree whose lock names a live process is another session's run: **halt** and say so. Otherwise put the session's working directory on the run worktree, creating it first with `git -c checkout.workers=0 worktree add .agents/worktrees/<slug> <slug>` when the branch exists without one. Stash a dirty tree with `git stash push -u -m implement-<slug>-<utc>` and log the stash in the trail; never reset it away. Resume at the first open item of `todo.md`. When the [Run directory](#run-directory) is gone, rebuild it: `spec.md` from the Issue, and `todo.md` from step 4 with every unit a `Unit:` trailer on `git log <base>..HEAD` names checked off.
- **Fresh.** Open a worktree for this run, put the session's working directory inside it, then `git reset --hard <base>` so the run starts from the `<base>` you actually have; the new branch has no commits of its own yet. Use a host tool that creates the worktree and moves the session into it when one exists, recording the branch name it chose when that is not `<slug>`. Otherwise ensure the consuming repo ignores `.agents/worktrees/` (prefer a local ignore when the repo uses one), then `git -c checkout.workers=0 worktree add` at `.agents/worktrees/<slug>` on branch `<slug>` and change directory there.

The session works *inside* the run worktree for the rest of the run. Run every command from there as a **plain** command: every argument spelled out, files written with the host's file tools. A host that isolates the session in its worktree refuses a `cd`, a `git -C`, a shell variable, `$(…)`, or a heredoc. On a host whose shell starts every command in the original directory, resolve the worktree's absolute path once and begin every command with `cd <that path> &&`. Name the worktree in every delegate brief as the only directory the delegate works in.

Then create the [Run directory](#run-directory) when it is missing: `.agents/runs/<slug>/` with a `.gitignore` holding `*`, `spec.md` as the Issue's title as an H1 plus its body and nothing else (a description is written as-is), and the trail's first row through the **show-me-your-work** skill's `log.sh`. From here on **the Spec** is `spec.md`: every delegate reads it, and a resume reads it rather than the Issue.

An `/implement-yolo` run takes [Worktree waived](LANDING.md#worktree-waived) in place of the worktree.

Done when the session is inside the run's working tree and `spec.md` exists.

### 3. Route

Read the Spec once and name its playbook from this table. One playbook covers the whole run. Log the route as a trail row whose evidence is the Spec line that decided it.

| The Spec | Playbook |
|---|---|
| Describes behaviour that is wrong: category `bug`, a repro, an observed-versus-expected pair | **Bug fix** |
| Adds or changes behaviour: category `enhancement` | **Feature** |
| Keeps behaviour and changes structure: rename, extract, move, dedupe | **Refactoring** |
| Names one measured number to improve | **Perf issue** |
| Names pixel equivalence between two renderings | **Visual parity** |
| Spans many call sites or several subsystems, or more than this session can finish | the **figure-it-out** skill, which designs the phases; its Phase E ends in step 6's gates |

**Design-skip rule.** Feature's `how` and `architect` steps are skipped, each with `skip: <the Spec line that fixed the shape>`, when the Spec's Implementation Decisions already name the data shape and its organizing structure and the change touches one or two files. Otherwise both run. This is the only skip the route decides; every other skip is the playbook's own.

Done when the trail holds the route row.

### 4. Open `todo.md`

`todo.md` in the Run directory is the run's only todolist; session task tools stay unused, so `check-run.mjs` and a resume read one file. Write it in this order:

1. The header lines: `Playbook: <name>`, `Landing: worktree` or `Landing: in-place`, and for in-place `Start: <sha>`.
2. The run items already done, checked: the claim, the worktree, `spec.md`.
3. The playbook's steps, copied verbatim from `../poteto-mode/playbooks/<playbook>.md`, with the consuming repo's `.agents/playbooks/` changes applied first (run `check-playbooks.mjs` on the repository root before applying them, as poteto-mode says) and the [Overlay](.agents/playbooks/implement.md) applied last, each change at the step its quoted text names. A step you skip stays in the list with `skip: <reason>`.
4. The landing items: `check-run.mjs`, rebase, landing commit, fast-forward, push, retro, report.

Done when every line of `todo.md` is a header, `- [ ]`, `- [x]`, or a `skip:` line, and `node <this skill's directory>/scripts/check-run.mjs <run directory>/todo.md` prints each open item.

### 5. Run the playbook

poteto-mode governs: its Non-negotiables, Subagents, Comments, and Principles apply as written, and each principle you apply is read from its leaf and named in the report. Implement adds these rules:

- **Delegates.** Every delegate is `skills:poteto-agent` on the sheet's model for the playbook's role. A brief is file pointers: `spec.md`, `design.md` when it exists, the run worktree as the only directory it works in, `CONTEXT.md` and the ADRs covering the area, the Coding standards found as `/code-review` finds them and read by section, the Spec's Testing Decisions, `<base>`, the named data shape and its organizing structure, and the success check. The delegate has no user and closes gaps from the Spec, the design, and the code ([ADR-0026](../../docs/adr/0026-implement-agents-close-leftover-gaps.md)). It writes nothing outside the worktree; it never pushes, publishes, or touches a live system; every build or test command runs with the tool's quiet flags and its output bounded to failures plus the summary.
- **One writer.** Delegates write in the run worktree one at a time. Only a workstream the throughput checkpoint names as disjoint gets its own worktree, branched from the run branch's head, and merges back in order.
- **Unit commits.** Each delegate commits on the run branch, one commit per unit with a `Unit: <title>` trailer, a Bug fix's failing test before its fix. The landing folds them, and the trailers are what a resume without the Run directory rebuilds from.
- **Fresh per retry.** A delegate that returns blocked, a question, or anything but its report, or whose diff fails your review, is replaced by a fresh delegate with consolidated scope: the original brief, every later directive, the prior report, and the branch. Two failed fixes that share one premise trigger the **attack-the-premise** principle skill: write the premise in the trail, take the census, and only then dispatch a third. A third failure **halts**.
- **Your reads.** You read diffs, verdicts, the trail, and evidence files by path; never a delegate's transcript or a whole test log.
- **Deviations.** A delegate's deviation from the design goes in `design.md`'s Implementation reconciliation section and a trail row; a deviation from the Spec is named in the report.

Done when every playbook step in `todo.md` is checked or skipped and step 6's gates have passed.

### 6. Gates

Each gate is a trail row whose result names the pass condition. A gate that cannot pass **halts**.

- **Design gate.** `design.md` exists, with the data shape and its organizing structure named, before any delegate writes code; or the design-skip rule fired and the trail row names the Spec line that fixed the shape. A Bug fix also needs a trail row whose evidence is runtime output confirming the mechanism.
- **Verification gate.** A fresh `skills:poteto-agent` that wrote none of the code, the **Verifier**, on the `judgment and prose` model, drives the matching surface, runs every Hand check in `spec.md`, saves artifacts under `evidence/`, and returns VERIFIED, NOT VERIFIED, or INCONCLUSIVE per item with the evidence path. The gate passes on VERIFIED for the change and for every Hand check. INCONCLUSIVE and a wrong surface fail it. A Hand check that needs what no agent can reach (a live system, credentials, a device) is skipped with what it needs, and the report names it. The driver skill resolves in this order: the project `verify` skill at `.claude/skills/verify/`, then `run`. A NOT VERIFIED item goes to a fresh delegate under step 5's retry rule, then to a fresh Verifier.
- **Review gate.** `/deslop` over the diff, then `/no-comments`, then `interrogate` with `spec.md` as the stated intent, so it judges conformance and quality at once. Every Act-on finding goes to a fresh delegate, and you review that diff. A fix that crosses a function boundary sends the change back through the verification gate. When no independent reviewer can run, write `BLOCKED: independent review` in `todo.md` and **halt**.
- **Landing gate.** `check-run.mjs` exits 0, then [LANDING.md](LANDING.md).

### 7. Land

Follow [LANDING.md](LANDING.md) from its first section. Done when `<base>` holds the landing commit and the push has run or been skipped with its reason.

### 8. Retrospective

Run `/retro` when the trail holds a revert, a premise census, a resumed halt, a `BLOCKED:` row, a flaky test, or an operator call made by default; otherwise the report says retro was skipped as nothing went wrong. When it committed and step 7's push went out, run [the push](LANDING.md#the-push) again.

## Run directory

`.agents/runs/<slug>/` in the run's working tree, by absolute path, with its own `.gitignore` holding `*`: no commit sweeps it in, `git reset --hard` and `git clean -fd` leave it alone, and a host that isolates a session in its worktree can write it.

| File | Holds | Writer |
|---|---|---|
| `spec.md` | The Issue's title as an H1 and its body, written once at intake | you |
| `todo.md` | The header lines and the checklist, the run's state machine. An item line is open `- [ ]`, done `- [x]`, or skipped with `skip: <reason>`; a `BLOCKED:` line is a closed gate | you |
| `trail.tsv` | The show-me-your-work log: append-only, one row per decision, evidence as paths | you |
| `design.md` | The architect's synthesized design with its Implementation reconciliation section; absent when design was skipped | the architect run, then deviations through you |
| `evidence/` | Repro output, screenshots, verification and Hand-check transcripts | the Verifier and the repro step |

`scripts/check-run.mjs <path to todo.md>` reads the checklist and nothing else: it exits non-zero and prints each open or `BLOCKED:` line, so the landing gate is one command. A resume reads the first open item. Nothing else is stored that git or the Issue can give back; `<base>` is re-read, never stored ([ADR-0055](../../docs/adr/0055-a-run-lands-on-the-branch-it-started-from.md)).

After the land the directory sits at `.agents/runs/<slug>/` in the original checkout, copied there before the worktree is removed. Its readers are `/retro`, which runs right after, and the person who reviews the trail after stepping away; the report names the path. A later run on the same slug replaces it.

## Halts and flags

A **halt** is non-destructive and ends the session. The branch, the run worktree, and the Run directory stay as they are, with uncommitted work committed as one `wip:` commit on the run branch and a resume note as the trail's last row (the **Pause safely** playbook, with the Run directory as its locator). The report says which todo item is open and why. Re-invoking `/implement` with the same argument resumes at that item.

Halt on these and only these: a detached HEAD; an open blocker Issue; another user's claim; another session's live run; a line from `check-playbooks.mjs`; a Bug fix whose symptom never goes red; a gate that cannot pass; a third failed delegate on one check; `BLOCKED: independent review`; work that would publish outside the checkout, such as a deploy, a package push, or a live record ([ADR-0028](../../docs/adr/0028-implement-claims-its-issue-and-pushes-only-what-lands.md)); a rebase conflict `/resolving-merge-conflicts` cannot settle.

A **flag** goes in the report and does not halt: a Hand check skipped for an unreachable surface, a Deviation, a flaky test that passed on its re-run ([ADR-0046](../../docs/adr/0046-a-flaky-post-rebase-failure-is-not-a-fixer-dispatch.md)), a failure `<base>` already has ([ADR-0029](../../docs/adr/0029-test-failures-are-measured-against-the-base-branch.md)), a refused push, an operator call made by default.

## Report

The run's last message is the reply poteto-mode's **Writing the reply** section describes, with the routed playbook's own reply lines, and these on top: the landing commit's subject and hash; what each push sent and to which remote branch, or why it pushed nothing, quoting a failed push's error and naming the commits that wait on this machine; the Verifier's verdict per item with its evidence path, and for a Bug fix the decisive red and green output trimmed to the assertion and the counts; each flag; each operator call made by default and what the operator could say instead; the Run directory's path; whether retro ran; and the show-me-your-work **Attention** section.

## Benchmark mode

The `benchmark/` runner measures what a run costs. It exports `SKILLS_BENCHMARK=1` and `SKILLS_BENCHMARK_LOG` and names `SKILLS_BENCHMARK=1` in the session's system prompt, so the mode is on when your system prompt says so and costs no call to find out. Without that line, skip this section ([ADR-0066](../../docs/adr/0066-a-benchmark-run-writes-nothing-outside-its-checkout.md)).

In benchmark mode every outward write is a **no-op**: the claim in step 1 and the pushes in steps 7 and 8 each run `bench-log "<step>: <the command it would have run>"` instead, and the run goes on as though that write succeeded. Tracker reads stay. Every delegate brief, the Verifier's and each `interrogate` reviewer's included, gets one more line: this is a benchmark run, so a `gh` write or a `git push` is a `bench-log` line. The final report says each push was a no-op.

## Work in another repository

The worktree, the review diff, the land, and the push cover this repository only. Work a Spec puts in another repository goes on a branch named `<slug>` there, committed by the delegate that did it and never pushed; the final report names the repository, the branch, and what sits on it.
