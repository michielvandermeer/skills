# Implement yolo

`/skills:implement-yolo` builds an Issue's Spec as a poteto-mode run on the current checkout and branch: the driving session reads `poteto-mode`, routes the Spec to a playbook, keeps a `todo.md` in `.agents/runs/<slug>/`, dispatches `skills:poteto-agent` delegates to build, a fresh one to verify, and `interrogate`'s reviewers to review, then folds the run into one commit that closes the Issue. It is the cheaper of the two implement commands to drive, and it runs `skills/implement/SKILL.md` with the worktree waived.

## Sub-features

- `yolo-land` lands the Issue as exactly one commit on the starting branch, whose tree deletes the Issue file (the Tracker's "close as done" ran as a unit commit before the fold).
- `yolo-route` generates `.agents/runs/<slug>/todo.md` with `skills/implement/scripts/open-todo.mjs`: the playbook's steps verbatim with the overlay applied, the three gate items, a `## Landing` section, and skips `how` and `architect` with an indented `skip:` line when the Spec fixes the shape and touches one or two files.
- `yolo-agents` runs `skills:poteto-agent` delegates for the build and any fix round (descriptions starting `Build:` or `Fix:`), one fresh `skills:poteto-agent` as the Verifier (`Verify:`) after the review, and `interrogate`'s `general-purpose` reviewers (four on the default sheet).
- `yolo-report` reports in poteto-mode's reply shape: what was built, the design or the skip reason, the Verifier's verdict per item, the landing commit, the push, and the Attention section.
- `yolo-run-dir` leaves `.agents/runs/<slug>/` in the checkout, ignored by git, with `todo.md` fully checked or skipped above `## Landing`, a `Landed: <sha>` header, and `trail.tsv` present.
- `yolo-halt` halts on a detached HEAD or an open blocker and leaves everything in place for a resume.
- `yolo-no-push` skips the push when `git remote` lists nothing.

## How to get to it (user POV)

- Type `/skills:implement-yolo <Issue path or slug>`.
- Type `/skills:implement-yolo <a description of what to build>`.
- A `/goal` that names `/implement-yolo` starts it; the model reaches it only when the command is named.

## Driving it with verify.py

Preconditions:

- A run through [setup](setup.md)'s local journey.
- One Issue committed at `.agents/issues/<slug>.md`, with `Status: ready-for-agent` and a small Spec in the template from `skills/to-spec/SKILL.md`, including a `## How to Check It` list and Implementation Decisions that name the data shape. Example: a `greet(name)` function in `greet.py` returning `Hello, <name>!`, tested with `python -m unittest`. The [grill-with-docs](grill-with-docs.md) journey produces such an Issue; writing it by hand is quicker.
- Note the starting commit: `git -C <scratch> rev-parse HEAD`.

- **Run.** Run `verify.py turn <run> "/skills:implement-yolo <slug>" --timeout 3600`. The run needs no further turn.
- **Agents.** The summary lists `skills:poteto-agent` at least twice, a `Build:` and a `Verify:` description, and `general-purpose` reviewers from `interrogate`, with the `Verify:` agent starting after the reviewers finished. On the example Spec no `how` explorers or `arena` runners appear, because the design-skip rule fires; `todo.md` holds the two indented `skip:` lines under steps 1 and 2.
- **Report.** The final message names the landing commit, says the push was skipped for having no remote, gives the Verifier's verdict per Hand check with an evidence path under `.agents/runs/<slug>/evidence/`, and ends with an Attention section that names its reviewer's model.
- **Proof.** In `scratch-01.txt`: `git log` shows one landing commit after the start, plus at most one `/retro` commit; `git show --stat` of the landing commit adds the code and test and deletes `.agents/issues/<slug>.md`; status is clean; `git branch -a` shows only `main`; `git worktree list` shows only the scratch repo. In the scratch repo, `node <checkout>/skills/implement/scripts/check-run.mjs .agents/runs/<slug>/todo.md` exits 0, `todo.md` starts with `Playbook: Feature`, `Landing: in-place`, `Start: <the starting commit>`, and holds a `Landed: <the landing commit>` line, `.agents/runs/<slug>/trail.tsv` exists, and `git check-ignore .agents/runs/<slug>/todo.md` names it as ignored. The steps were not retyped: `node <checkout>/skills/implement/scripts/open-todo.mjs feature --root <scratch> --landing in-place --start <the starting commit>` regenerates the checklist, and `diff` against the run's `todo.md` shows only `[x]` marks, the indented `skip:` lines, the run items, and the `Landed:` line. Run the Spec's test in the scratch repo and see it pass.
- **Halt.** In another run, `git -C <scratch> checkout --detach` before the turn. The run halts, names the detached HEAD, and leaves no commit.

## Gotchas

- Expect 6 to 12 agents and well over the default `--budget` of 10 dollars for anything bigger than the example; raise `--budget` and `--timeout` to match. A Spec that does not fix its shape also runs `how` and `architect`, which adds four `arena` runners.
- Delegate models come from the user's `~/.claude/pstack-models.md`, which the session loads as the real user path; the driving session itself is pinned to Opus at high.
- The Verifier drives the Spec's `## How to Check It` as the named person would, and skips checks that need live systems; a Spec whose only checks need the network verifies nothing here.
- To measure what a change costs across `/implement` runs, use `benchmark/` instead. One verify run proves behaviour, not cost.
