# Implement

`/skills:implement` implements an Issue in a worktree on branch `<slug>`. A planner slices its Spec into Steps, then a loop of up to three Iterations runs: implementers write and commit it, one per Step on the first Iteration, a Standards reviewer judges it against the coding standards and design principles, and a verifier checks it against the Spec, the test suite, and the Hand checks. A Hard violation or a Verify finding sends it back to a fresh implementer; a Judgement call waits for that implementer, or the final report. From Iteration 2 on, the reviewer reads only that Iteration's fix. The run lands on the branch it started from as one commit that closes the Issue, then removes its worktree and branch.

## Sub-features

- `implement-land` lands the Issue as exactly one commit on the starting branch and closes the Issue.
- `implement-plan` runs `skills:planner` once, which commits `plan: <slug>` with one Step file per Step under `.agents/runs/<slug>/`; a small Spec gets one Step.
- `implement-agents` runs `skills:implementer` once per Step on Iteration 1 and once per later Iteration, one `skills:reviewer` on the Standards axis, and `skills:verifier`, once each per Iteration.
- `implement-loop` reports a `Step <NN>/<total> — <title>: done` line per Step, then `Iteration <N>/3 — review:` lines (`passed`, or the count of hard violations and judgement calls) and `— verify:` lines, and the final report says how many Steps and Iterations the run took and lists the judgement calls that land unfixed.
- `implement-cleanup` deletes `.agents/runs/<slug>/`, the worktree, and branch `<slug>` once it has landed.
- `implement-halt` halts on a detached HEAD or an open blocker and leaves everything in place for a resume.
- `implement-no-push` skips the push when `git remote` lists nothing.

## How to get to it (user POV)

- Type `/skills:implement <Issue path or slug>`.
- Type `/skills:implement <a description of what to build>`.
- A `/goal` that names `/implement` starts it; the model reaches it only when the command is named.

## Driving it with verify.py

Preconditions:

- A run through [setup](setup.md)'s local journey.
- One Issue committed at `.agents/issues/<slug>.md`, with `Status: ready-for-agent` and a small Spec in the template from `skills/to-spec/SKILL.md`, including a `## How to Check It` list. Example: a `greet(name)` function in `greet.py` returning `Hello, <name>!`, tested with `python -m unittest`. The [grill-with-docs](grill-with-docs.md) journey produces such an Issue; writing it by hand is quicker.
- Note the starting commit: `git -C <scratch> rev-parse HEAD`.

- **Run.** Run `verify.py turn <run> "/skills:implement <slug>" --timeout 3600`. The run needs no further turn.
- **Agents.** The summary lists `skills:planner` once, `skills:implementer` once per Step and once per later Iteration, and `skills:reviewer` (Standards only) and `skills:verifier` once per Iteration.
- **Plan.** The land deletes the run's branch, so the plan shows in `transcripts/`: the Planner's reply is the index, it commits `plan: <slug>`, and each Step's Implementer appends `## Outcome` to its Step file and sets `Status: done`. A run with more than one Step lists each Step's title in the landing commit's body.
- **Report.** The final message says how many Steps and Iterations the run took and that the push was skipped for having no remote.
- **Proof.** In `scratch-01.txt`: `git log` shows one landing commit after the start, plus at most one `/retro` commit; the landing commit adds the code and test and closes `.agents/issues/<slug>.md`; status is clean; `git branch -a` shows only `main`; `git worktree list` shows only the scratch repo; no `.agents/runs/` or `.agents/worktrees/<slug>` folder remains. Run the Spec's test in the scratch repo and see it pass.
- **Halt.** In another run, `git -C <scratch> checkout --detach` before the turn. The run halts, names the detached HEAD, and leaves no commit.

## Gotchas

- Expect 4 to 10 agents and well over the default `--budget` of 10 dollars for anything bigger than the example; raise `--budget` and `--timeout` to match.
- The Verifier runs `## How to Check It` as the named person would, and skips checks that need live systems; a Spec whose only checks need the network proves nothing here.
- The worktree sits under the scratch repo at `.agents/worktrees/<slug>`, and the run adds that path to an ignore file; `verify.py cleanup` removes it with the scratch repo.
- To measure what a change costs across `/implement` runs, use `benchmark/` instead. One verify run proves behaviour, not cost.
