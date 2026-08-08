---
name: implement
description: "Implement a spec by slicing it into steps and running each one in its own sub-agent."
argument-hint: "Which spec, issue, or idea to implement?"
disable-model-invocation: true
---

You are the **driving session**: you orchestrate, sub-agents implement. You hold the step index, one three-line report per step, any deviations, and the review findings for as long as step 4 takes to hand them on — that is the whole of your context, and it is what lets a spec of any size run to landed inside one session.

Sub-agents share the worktree, so run them one at a time. Step agents are `skills:implementer`, pinned to a cheaper tier because their scope was decided before they started. The planner, the fixer, and the data-structures pass are `general-purpose` and run at your own model and effort — they carry judgement worth paying for. See [ADR-0007](../../docs/adr/0007-pinned-subagent-model-tiers.md).

## Process

### 1. Enter the worktree

Derive `<slug>`: the spec's filename without its extension when the argument names one, otherwise a kebab-case slug from the argument.

A prior run is **in flight** when any linked git worktree contains `.agents/steps/<slug>/` — the planner got that far, so a worktree holds those steps. Find it with `git worktree list` (or the host's equivalent). Check first, because it decides which worktree you enter:

- **In flight** → put the session's working directory on that worktree's path, then `git reset --hard && git clean -fd` to drop whatever the halted step left behind. The steps are already planned: skip step 2 and resume at the lowest-numbered step whose `Status:` is not `done`.
- **Fresh** → open a worktree for this run, put the session's working directory inside it, then `git rebase master` so the run sits on the master you actually have:
  - If this host has a tool that **creates the worktree and moves the session into it**, use that tool — even when its path is not the fallback below. Record the branch name it chose when that name is not `<slug>`.
  - Otherwise ensure the consuming repo ignores `.agents/worktrees/` (add the line if missing; prefer a local ignore when the repo uses one), then `git worktree add` at `.agents/worktrees/<slug>` on branch `<slug>`, and change the session's working directory there.

The session must work *inside* the worktree for the rest of the run — creating a worktree alone is not enough. An `/implement` prompt that explicitly waives the worktree takes the branch in [Worktree waived](#worktree-waived) instead.

### 2. Plan the steps

Dispatch a **planner** sub-agent. Give it the spec path (or the argument text), `<slug>`, and the absolute path to [STEPS.md](STEPS.md) in this skill's directory — it reads the slicing rules itself and writes one file per step to `.agents/steps/<slug>/`.

It returns the index and nothing else: one line per step, `NN | title | one-line deliverable`.

A planner that fails or returns no steps **halts** the run.

### 3. Run each step in `NN` order

Dispatch a fresh `skills:implementer` per step. Hand it paths and let it read what it needs:

- the spec, and its own step file — whose `## Footprint` names the files, symbols and projects the work lands in
- an instruction to read the `## Outcome` of every lower-numbered step file before starting
- `CONTEXT.md` and any ADR covering the area it touches, for vocabulary
- the spec's Testing Decisions, which govern what it tests
- the deviations reported by earlier steps, when there are any

Tell it where it stands and how far to trust its map: it starts in your working directory, and its footprint is a guess — where the code disagrees, the code wins, and the drift goes in its `## Outcome` so its successors inherit the correction.

Require of it: **green before it finishes** — every project on its footprint's `Projects:` line, and the whole suite on the last step. It then appends its `## Outcome` to its step file, sets that file's `Status: done`, and commits its code and its step file together in one commit.

Its entire response is three lines:

```
status: done | blocked
built: <one sentence on what now works>
deviations: <what contradicts the spec or changes a later step, or "none">
```

Then **check the step structurally** — the step file reads `Status: done`, and `git log` shows a new commit. That is the whole check; step 4's review covers the rest.

Report one line to the user — `Step <NN>/<total> — <title>: done` — plus the deviations line when it is not `none`, and carry those deviations into the next dispatch.

A `blocked` report or a failed structural check earns exactly one retry: `git reset --hard && git clean -fd`, then re-dispatch the same step with the failure appended to its prompt. A second failure **halts** the run.

Done when every file in `.agents/steps/<slug>/` reads `Status: done`.

### 4. Review and improve

**Run `/code-review` yourself**, with `master` as the fixed point, and hold what its two axes report.

Give the user a short paragraph per axis in your own words. That summary replaces the verbatim presentation `/code-review` asks its caller for. Then keep going without waiting; the run lands unattended.

Two sub-agents follow, in this order, each reporting in the same three lines and subject to the same retry-then-halt rule:

1. **Fixes every finding**, both axes, from the findings you paste into its prompt. Retry-then-halt is the whole check on its work.
2. Runs `/improve-data-structures` **and applies what it finds**.

Each commits its own work.

### 5. Document the change

Run `/document-changes` in **implement mode** while the Spec and step Outcomes are still on disk — after review/improve, before delete and land. It prepends product-facing **Changelog** entries beside each affected context's `CONTEXT.md` and commits when it wrote; when nothing is product-visible it reports that and leaves the tree clean.

### 6. Land the branch

Delete the spec, any idea or issue document it came from, and the whole `.agents/steps/<slug>/` directory — the work they describe is now in the code. Commit anything still uncommitted; `git rebase` refuses a dirty tree, so the branch cannot land until this is clean.

Each remaining command runs where its branch is checked out, and that constraint fixes the order. `<branch>` is `<slug>`, or the name you recorded when a host tool chose another:

1. From the worktree, still on the branch: `git rebase master`, resolving any conflicts. (The branch lives here, so only the worktree can rebase it.)
2. Return the session to the original directory, keeping the branch and its commits — a host leave-worktree action when it does exactly that, otherwise change directory yourself.
3. From the original directory: `git merge --ff-only <branch>`. (master lives here, so only the original directory can fast-forward it.) The rebase above makes this a fast-forward; if it errors, master moved during the session — re-enter the worktree, rebase again, and retry.
4. `git worktree remove <path>` and `git branch -d <branch>`.

## Worktree waived

Steps live at `.agents/steps/<slug>/` in the checkout, and there is nothing to enter, exit, or remove. Step 1 skips opening a worktree. Step 6 drops the return-to-original-directory step and `git worktree remove`: rebase on the branch, check out master yourself, fast-forward, then delete the branch.

## Halting

A halt is non-destructive and it is the end of the session. Leave the spec, the step files, the branch, and the worktree exactly as they are — the completed steps are committed, and the run is resumable only because nothing was cleaned up. Report the step's number, its title, and what blocked it.

Re-invoking `/implement` with the same argument picks the run back up at that step.
