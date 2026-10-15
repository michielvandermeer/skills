# Implement yolo

`/skills:implement-yolo` implements an Issue as one Step on the current checkout and branch: an implementer writes and commits it, a checker proves and reviews it, fixers close review findings, a prover re-proves it, and the run lands as one commit that closes the Issue. It is the cheapest of the three implement commands to drive, and shares their skill text in `skills/implement/`.

## Sub-features

- `yolo-land` lands the Issue as exactly one commit on the starting branch and closes the Issue.
- `yolo-agents` runs `skills:implementer`, `skills:checker`, the `/code-review` reviewers, any fixers, and `skills:prover`.
- `yolo-proof` reports `Safety fact:`, `Proof:`, and `Merge risk:` lines, and the Prover's notes.
- `yolo-cleanup` deletes `.agents/steps/<slug>/` and `.agents/proof/<slug>/` before landing.
- `yolo-halt` halts on a detached HEAD or an open blocker and leaves everything in place for a resume.
- `yolo-no-push` skips the push when `git remote` lists nothing.

## How to get to it (user POV)

- Type `/skills:implement-yolo <Issue path or slug>`.
- Type `/skills:implement-yolo <a description of what to build>`.
- A `/goal` that names `/implement-yolo` starts it; the model reaches it only when the command is named.

## Driving it with verify.py

Preconditions:

- A run through [setup](setup.md)'s local journey.
- One Issue committed at `.agents/issues/<slug>.md`, with `Status: ready-for-agent` and a small Spec in the template from `skills/to-spec/SKILL.md`, including a `## How to Check It` list. Example: a `greet(name)` function in `greet.py` returning `Hello, <name>!`, tested with `python -m unittest`. The [grill-with-docs](grill-with-docs.md) journey produces such an Issue; writing it by hand is quicker.
- Note the starting commit: `git -C <scratch> rev-parse HEAD`.

- **Run.** Run `verify.py turn <run> "/skills:implement-yolo <slug>" --timeout 3600`. The run needs no further turn.
- **Agents.** The summary lists `skills:implementer`, `skills:checker`, `skills:reviewer` (two, from the driving session's review), and `skills:prover`, plus any fixers.
- **Report.** The final message carries the `Safety fact:`, `Proof:`, and `Merge risk:` lines and says the push was skipped for having no remote.
- **Proof.** In `scratch-01.txt`: `git log` shows one landing commit after the start, plus at most one `/retro` commit; the landing commit adds the code and test and deletes `.agents/issues/<slug>.md`; status is clean; `git branch -a` shows only `main`; `git worktree list` shows only the scratch repo; no `.agents/steps/` or `.agents/proof/` folder remains. Run the Spec's test in the scratch repo and see it pass.
- **Halt.** In another run, `git -C <scratch> checkout --detach` before the turn. The run halts, names the detached HEAD, and leaves no commit.

## Gotchas

- Expect 6 to 10 agents and well over the default `--budget` of 10 dollars for anything bigger than the example; raise `--budget` and `--timeout` to match.
- The Prover runs `## How to Check It` as the named person would, and skips checks that need live systems; a Spec whose only checks need the network proves nothing here.
- To measure what a change costs across `/implement` runs, use `benchmark/` instead. One verify run proves behaviour, not cost.
