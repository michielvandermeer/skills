---
name: implement
description: "Implement a spec by slicing it into steps and running each one in its own sub-agent."
argument-hint: "Which spec, issue, or idea to implement?"
disable-model-invocation: true
---

You are the **driving session**: you orchestrate, sub-agents implement. You hold the step index, one three-line report per step, and any deviations — that is the whole of your context, and it is what lets a spec of any size run to landed inside one session.

Sub-agents share the worktree, so run them one at a time. Step agents are `skills:implementer`, pinned to a cheaper tier because their scope was decided before they started. The planner, the fixer, and the data-structures pass are `general-purpose` and run at your own model and effort — they carry judgement worth paying for. See [ADR-0007](../../docs/adr/0007-pinned-subagent-model-tiers.md).

## Process

### 1. Enter the worktree

Derive `<slug>`: the spec's filename without its extension when the argument names one, otherwise a kebab-case slug from the argument.

A prior run is **in flight** when `.claude/worktrees/<slug>/.agents/steps/<slug>/` exists — the planner got that far, so the worktree does too. Check first, because it decides which worktree you enter:

- **In flight** → call `EnterWorktree` with `path: .claude/worktrees/<slug>`, then `git reset --hard && git clean -fd` to drop whatever the halted step left behind. The steps are already planned: skip step 2 and resume at the lowest-numbered step whose `Status:` is not `done`.
- **Fresh** → call `EnterWorktree` with `name: <slug>`, then `git rebase master`. The tool branches from `origin/master` by default, and the rebase puts the run on the master you actually have.

Use the `EnterWorktree` tool, not `git worktree add`, which leaves the session in the original directory. The only exemption is an `/implement` prompt that explicitly waives the worktree; then steps live at `.agents/steps/<slug>/` in the checkout and there is no worktree to enter, exit, or remove.

### 2. Plan the steps

Dispatch a **planner** sub-agent. Give it the spec path (or the argument text), `<slug>`, and the absolute path to [STEPS.md](STEPS.md) in this skill's directory — it reads the slicing rules itself and writes one file per step to `.agents/steps/<slug>/`.

Each step file carries a **footprint**: the files and symbols that step is expected to touch, and the projects that must be green when it finishes. The planner walks the codebase anyway to slice the spec, and writing that walk down is what stops every step agent from repeating it.

It returns the index and nothing else: one line per step, `NN | title | one-line deliverable`.

A planner that fails or returns no steps **halts** the run.

### 3. Run each step in `NN` order

Dispatch a fresh `skills:implementer` per step. Hand it paths and let it read what it needs:

- the spec, and its own step file — whose `## Footprint` tells it where the work lands
- an instruction to read the `## Outcome` of every lower-numbered step file before starting
- `CONTEXT.md` and any ADR covering the area it touches, for vocabulary
- the spec's Testing Decisions, which govern what it tests
- the deviations reported by earlier steps, when there are any

Tell it the footprint is a guess: it follows the code where the two disagree, and records that drift in its `## Outcome` so its successors inherit the correction.

Require of it: **green before it finishes** — every project on its footprint's `Projects:` line, or the whole suite when that line names more than one, and the whole suite again on the last step. A step confined to one project is checked where it can break things; anything wider is checked everywhere. It then appends its `## Outcome` to its step file, sets that file's `Status: done`, and commits its code and its step file together in one commit.

Its entire response is three lines:

```
status: done | blocked
built: <one sentence on what now works>
deviations: <what contradicts the spec or changes a later step, or "none">
```

Then **check the step structurally** — the step file reads `Status: done`, and `git log` shows a new commit. That is the whole check; the next step's green gate and the review in step 4 cover the rest.

Report one line to the user — `Step <NN>/<total> — <title>: done` — plus the deviations line when it is not `none`, and carry those deviations into the next dispatch.

A `blocked` report or a failed structural check earns exactly one retry: `git reset --hard && git clean -fd`, then re-dispatch the same step with the failure appended to its prompt. A second failure **halts** the run.

Done when every file in `.agents/steps/<slug>/` reads `Status: done`.

### 4. Review and improve

**Run `/code-review` yourself**, with `master` as the fixed point. You pin the fixed point, the spec, and the standards sources in your own context, and its two axes report back to you. A sub-agent that owned this read the diff its own two children had just read; holding the findings here is the same job you already do for deviations.

Summarise each axis for the user in a short paragraph of your own words — never the reports verbatim, and never the raw shape a tool handed you. Then keep going without waiting; the run lands unattended.

Two sub-agents follow, in this order, each reporting in the same three lines and subject to the same retry-then-halt rule:

1. **Fixes every finding**, both axes, from the findings you paste into its prompt. One agent for both — the fixes land in the same files, and the shared worktree serialises them anyway. Nothing re-reviews its work; the retry-then-halt rule is the whole check.
2. Runs `/improve-data-structures` **and applies what it finds**.

Each commits its own work.

### 5. Land the branch

Delete the spec, any idea or issue document it came from, and the whole `.agents/steps/<slug>/` directory — the work they describe is now in the code. Commit anything still uncommitted; `git rebase` refuses a dirty tree, so the branch cannot land until this is clean.

Each remaining command runs where its branch is checked out, and that constraint fixes the order:

1. From the worktree, still on the branch: `git rebase master`, resolving any conflicts. (The branch lives here, so only the worktree can rebase it.)
2. Call `ExitWorktree` with `action: "keep"` to return the session to the original directory, preserving the branch and its commits.
3. From the original directory: `git merge --ff-only <branch>`. (master lives here, so only the original directory can fast-forward it.) The rebase above makes this a fast-forward; if it errors, master moved during the session — re-enter the worktree, rebase again, and retry.
4. `git worktree remove <path>` and `git branch -d <branch>`.

With the worktree waived there is none to exit or remove: check out master yourself before the fast-forward, then delete the branch.

## Halting

A halt is non-destructive and it is the end of the session. Leave the spec, the step files, the branch, and the worktree exactly as they are — the completed steps are committed, and the run is resumable only because nothing was cleaned up. Report the step's number, its title, and what blocked it.

Re-invoking `/implement` with the same argument picks the run back up at that step.
