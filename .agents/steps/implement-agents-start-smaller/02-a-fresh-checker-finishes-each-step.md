# 02 — A fresh Checker finishes each Step

Status: done

## What to build

In `/implement` step 3, each Step is now finished by two agents in turn, both sent by the Driving session: the Step agent builds and commits it, then a fresh **Checker** (`skills:checker`) verifies, reviews, fixes, and marks it done. See [ADR-0051](../../../docs/adr/0051-a-fresh-checker-finishes-each-step.md).

**The Checker agent file.** A new `agents/checker.md`, frontmatter `name: checker`, a `description` saying it is dispatched explicitly by `/implement` to finish one Step and is not a general coding agent, and `effort: medium` (ADR-0049). Its body follows the shape of `agents/implementer.md`: the prompt is the contract; the Spec wins over the Step file and a disagreement is a Deviation; it has no user; the Coding standards bind every line it commits; read code in few, wide turns; builds and tests run in the foreground; a red test also red on `master` at the merge-base is a Deviation; stop every process it started before reporting; its turn ends with the three-line report and nothing else. It may start sub-agents only for the reviewers `/code-review` starts. Its work, in order:

1. Run any verification the repo's conventions demand for the surface touched, such as a browser pass or smoke run, from the run worktree. Skip it when the repo has none — never invent one.
2. Run `/code-review` on the Step's commit, both axes: the fixed point is the one the prompt names, the spec is the Step file, and both axes are told that later Steps build the rest of the Spec and that the Step file is run bookkeeping. The reviewers' reports are its to act on, not to present.
3. Fix every finding, and any failed verification. Where a finding and the Spec disagree, the Spec wins and the finding goes on the deviations line.
4. Re-run the tests of the Footprint's projects, or the whole suite on the last Step, and the verification from 1 again, until green against `master` (ADR-0029).
5. Set the Step file's `Status:` to `done`, add to its `## Outcome` anything a later Step needs from the fixes, and fold everything into the Step's commit with `git commit --amend` — even when there was nothing to fix, because the status flip must land. A `blocked` report commits nothing.

**The Driving session's Checker dispatch.** Right after a Step agent's report and structural check pass, the Driving session sends the Checker. Its prompt is paths and section names: the Spec, the Step file, the parent of the Step's commit as the review's fixed point (the Driving session resolves it as a SHA with `git rev-parse HEAD~1` before dispatch), the Coding standards, `CONTEXT.md` and the ADRs for the area, the Spec's Testing Decisions, the deviations reported by earlier Steps and by this Step's agent verbatim, its Step number and the total, and the same three-line report format. It gets no earlier Outcomes. After it returns, the Driving session checks that `grep '^Status:'` on the Step file reads `done`. The Checker is under the same retry-then-halt rule as a Step agent: one retry (resume once, or `git reset --hard && git clean -fd` and re-dispatch the Checker — the Step agent's commit survives the reset), and a second failure halts the run. The per-Step user line `Step <NN>/<total> — <title>: done` is reported once, after the Checker's check passes, with any non-`none` deviations from either report; both reports' deviations are carried verbatim into later dispatches.

**The Step agent.** Its "review your commit" line goes from `agents/implementer.md`, and so does its permission to start the reviewers' sub-agents; it keeps sub-agents for reading a part of the codebase too large to hold. In `/implement` step 3, its green is the tests of its Footprint's projects, or the whole suite on the last Step, measured against `master`; the browser-pass-or-smoke-run bullet moves out of the Step agent's requirements into the Checker's. It sets `Status: built`, not `done`, in the one commit that holds its code, its Step file, and its Outcome. The Driving session's structural check after it becomes `Status: built` and a new commit. A Step is **Green** only once both agents have passed.

**Resume.** A run resumes at the lowest-numbered Step not `done`: a Step at `built` resumes at its Checker, a Step at `pending` at its Step agent. This is said in step 1's in-flight branch and in the Halting section's re-invoke sentence.

**Around it.** The slicing rules' sentence that the Outcome and the `done` flip belong to the Step agent becomes: the Step agent writes the Outcome and sets `built`; the Checker sets `done`. `/implement`'s opening paragraph names the Checker beside the Step agents, at reduced effort, and links ADR-0051. The README's repository layout lists `agents/checker.md`, and its spec-bound list of `effort: medium` agents gains `skills:checker`.

## Footprint

Projects: none

- `agents/checker.md` — new file
- `agents/implementer.md` — the sub-agent bullet, the `/code-review` bullet
- `skills/implement/SKILL.md` — opening agent paragraph; step 1 in-flight resume bullet; step 3 requirements, green bullets, structural check, user line, retry paragraph, done-when line; the new Checker dispatch in step 3; Halting's re-invoke sentence
- `skills/implement/STEPS.md` — the sentence under the Step file template about `## Outcome` and `Status:`
- `README.md` — `## Repository layout` agents list, `## Sub-agent cost tiers` spec-bound list
- `docs/adr/0051-a-fresh-checker-finishes-each-step.md` — already written; link it, do not rewrite it
- `CONTEXT.md` — already carries **Checker**, **Step agent**, **Green**; read for vocabulary

## Acceptance criteria

- [ ] `agents/checker.md` exists with `name: checker`, a description, and `effort: medium`, and its body lays out the five-part order above and the three-line report
- [ ] `agents/implementer.md` no longer reviews its own commit and no longer starts reviewer sub-agents
- [ ] `/implement` step 3 requires `Status: built` from the Step agent, its green covers only its Footprint's tests (whole suite on the last Step), and the browser pass or smoke run is the Checker's
- [ ] `/implement` step 3 dispatches the Checker after each Step agent with the prompt contents above, checks for `Status: done`, and applies one retry then halt
- [ ] Resume restarts a `built` Step at its Checker and a `pending` Step at its Step agent, in step 1 and in Halting
- [ ] `skills/implement/STEPS.md` says the Step agent sets `built` and the Checker sets `done`
- [ ] `/implement`'s opening paragraph and `README.md` name `skills:checker` among the effort-pinned agents; README's layout lists `agents/checker.md`
- [ ] Every edited or new agent and skill file matches `skills/writing-for-agents/SKILL.md`, and `/writing-for-agents` has been run on them
- [ ] `CHANGELOG.md` is untouched

## Outcome

- New `agents/checker.md` (`skills:checker`, `effort: medium`): the five-part order (verify, review, fix, re-green, then set `Status: done` and `git commit --amend`) and the implementer's working habits. It starts sub-agents only for the `/code-review` reviewers.
- `agents/implementer.md`: the `/code-review` bullet and the reviewer sub-agent clause are gone.
- `skills/implement/SKILL.md`: the opening paragraph names the Checker and links ADR-0051, and the context paragraph now counts both reports per step. Step 3 requires `Status: built` and passing Footprint tests from the Step agent, and the browser-pass bullet is gone from its requirements. After the `built` check, the Driving session resolves `git rev-parse HEAD~1`, dispatches the Checker, then checks for `done`. The user line comes after the Checker, and retry-then-halt covers both agents. Step 1's in-flight bullet and Halting resume a `built` Step at its Checker and a `pending` one at its Step agent.
- `skills/implement/STEPS.md`: the Outcome/`Status:` sentence now says the step agent sets `built` and the Checker sets `done`.
- `README.md`: the layout lists `checker.md`, and the spec-bound list gains `skills:checker`.
- For Step 03: step 4 of `skills/implement/SKILL.md` is untouched and still describes one fixer; `agents/oneshot.md` still has its `/code-review` bullet.
- Footprint drift: `CONTEXT.md` changed after all. **Deviation** now names the Checker, and **Step** names the `pending` → `built` → `done` lifecycle. ADR-0051 needed no edits.
- Review fixes kept on purpose: `checker.md` repeats the implementer's working habits, because the Step file asks for that shape. Step 1 and Halting in `SKILL.md` both state the `built`/`pending` resume rule, because the Step file asks for both.
