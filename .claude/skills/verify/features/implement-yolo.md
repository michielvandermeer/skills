# Implement yolo

`/skills:implement-yolo` implements an Issue on the current checkout and branch in a loop of up to three Iterations: an implementer writes and commits it, a Standards reviewer judges it against the coding standards and design principles, and a verifier checks it against the Spec, the test suite, and the Hand checks. A finding sends it back to a fresh implementer. The run lands as one commit that closes the Issue. It is the cheaper of the two implement commands to drive, and reads its loop from `skills/implement/`.

## Sub-features

- `yolo-land` lands the Issue as exactly one commit on the starting branch and closes the Issue.
- `yolo-agents` runs `skills:implementer`, one `skills:reviewer` on the Standards axis, and `skills:verifier`, once each per Iteration.
- `yolo-loop` reports `Iteration <N>/3 — review:` and `— verify:` lines, and the final report says how many Iterations the run took.
- `yolo-cleanup` deletes `.agents/runs/<slug>/` before landing.
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
- **Agents.** The summary lists `skills:implementer`, `skills:reviewer` (one per Iteration, Standards only), and `skills:verifier`, each once per Iteration.
- **Report.** The final message says how many Iterations the run took and that the push was skipped for having no remote.
- **Proof.** In `scratch-01.txt`: `git log` shows one landing commit after the start, plus at most one `/retro` commit; the landing commit adds the code and test and deletes `.agents/issues/<slug>.md`; status is clean; `git branch -a` shows only `main`; `git worktree list` shows only the scratch repo; no `.agents/runs/` folder remains. Run the Spec's test in the scratch repo and see it pass.
- **Halt.** In another run, `git -C <scratch> checkout --detach` before the turn. The run halts, names the detached HEAD, and leaves no commit.

## Gotchas

- Expect 3 to 9 agents and well over the default `--budget` of 10 dollars for anything bigger than the example; raise `--budget` and `--timeout` to match.
- The Verifier runs `## How to Check It` as the named person would, and skips checks that need live systems; a Spec whose only checks need the network proves nothing here.
- To measure what a change costs across `/implement` runs, use `benchmark/` instead. One verify run proves behaviour, not cost.
