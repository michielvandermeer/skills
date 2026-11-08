# Implement

`/skills:implement` implements an Issue in a worktree on branch `<slug>`. A planner slices its Spec into Steps, then a loop of up to three Iterations runs: implementers write and commit it, one per Step on the first Iteration, a Standards reviewer judges it against the coding standards and design principles, and a verifier checks it against the Spec, the test suite, and the Hand checks. A Hard violation or a Verify finding sends it back to a fresh implementer; a Judgement call waits for that implementer, or the final report. From Iteration 2 on, the reviewer reads only that Iteration's fix. The run lands on the branch it started from as one commit that closes the Issue, then removes its worktree and branch.

## Sub-features

- `implement-land` lands the Issue as exactly one commit on the starting branch and closes the Issue.
- `implement-plan` runs `skills:planner` once, which commits `plan: <slug>` with one Step file per Step under `.agents/runs/<slug>/`; a small Spec gets one Step.
- `implement-agents` runs `skills:implementer` once per Step on Iteration 1 and once per later Iteration, one `skills:reviewer` on the Standards axis, and `skills:verifier`, once each per Iteration.
- `implement-loop` reports a `Step <NN>/<total> — <title>: done` line per Step, then `Iteration <N>/3 — review:` lines (`passed`, or the count of hard violations and judgement calls) and `— verify:` lines, each Standards report ends with a closing `Standards:` count line, and the final report says how many Steps and Iterations the run took and lists the judgement calls that land unfixed.
- `implement-cleanup` deletes `.agents/runs/<slug>/`, the worktree, and branch `<slug>` once it has landed.
- `implement-halt` halts on a detached HEAD or an open blocker and leaves everything in place for a resume.
- `implement-resume` resumes from a Halt record at `.agents/runs/<slug>/halt.md`: one Implementer fixes its findings, Review reads only what came after it, and Verify runs in full.
- `implement-resume-issue` resumes a run from its existing Steps without asking, and `skills/implement/resume.py` prints one line naming a changed Issue when the Issue's body differs from the Spec copy; with an unchanged body it prints no such line.
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
- **Proof.** In `scratch-01.txt`: `git log` shows one landing commit after the start; the landing commit adds the code and test and closes `.agents/issues/<slug>.md`; status is clean; `git branch -a` shows only `main`; `git worktree list` shows only the scratch repo; no `.agents/runs/` or `.agents/worktrees/<slug>` folder remains. Run the Spec's test in the scratch repo and see it pass.
- **Review report.** In the run's transcript, the Standards report the reviewer returned ends with `Standards: <h> hard violations, <j> judgement calls`. The counts match the findings opened with `Hard violation:` and `Judgement call:` above it, and match the `review:` progress line the run printed.
- **Zero findings.** In another run, a Spec whose change breaks no Coding standard of the scratch repo gives a Standards report with no findings that still ends with the line, reading zero of each. The run prints `review: passed` and goes on to Verify.
- **Incomplete reply.** Not staged: the reviewer is a live model and verify.py cannot inject a reply. Read `skills/implement/SKILL.md` instead: a Review report with no closing line reruns the Review once without a new Iteration, a second one halts, the halt message says the Review returned no report, and the halt makes no `halt:` commit.
- **Halt.** In another run, `git -C <scratch> checkout --detach` before the turn. The run halts, names the detached HEAD, and leaves no commit.
- **Resume.** In another run, hand-build branch `<slug>` before the turn: `spec.md` and a `Status: done` Step file under `.agents/runs/<slug>/`, code that misses one Spec requirement, and a `halt.md` commit (`halt: <slug>`) naming that miss as a Verify finding. Run the same turn. The `resume.py` command's output in `turn-01.jsonl` holds `Resuming from the Halt record: 1 findings`; the run dispatches no `skills:planner`, sends one `skills:implementer` that names the finding, passes a `Standards` Review of the fix alone, then a `skills:verifier`, and lands.
- **Resume after an Issue edit.** In another run, hand-build branch `<slug>` and its run worktree `.agents/worktrees/<slug>`, as a stopped run leaves them, before the turn: a `spec:` commit holding `spec.md` and the Step files under `.agents/runs/<slug>/`, no `halt.md`. Give `.agents/issues/<slug>.md` a body that differs from the Spec copy by one added sentence that asks for a behaviour the Spec copy does not, such as an empty name returning `Hello, stranger!`. Run the same turn and let it land; every check reads what the session printed or what landed, never the deleted branch. Assert four things. In `turn-01.jsonl` the output of the `resume.py` command is `The Issue changed after this run started. This run builds the text it started with. To build the new text, delete branch <slug> and its worktree, then run /implement again.`, with the run's branch name in place of `<slug>`. The session asks no question: it uses no question tool and dispatches no `skills:planner`, resuming from the existing Steps. It never writes `.agents/runs/<slug>/spec.md`: no Write or Edit call in the transcript names that path. The one landing commit holds code for the old Spec copy only: the added sentence's behaviour is absent from it. Check only what the user sees and what lands in git, never the session's wording of its reasoning. This scenario fails on a skill that never prints the line. Run it three times; all three must pass with no re-run, because the bug passed in only 1 of 3 runs before.
- **Resume from a Halt record after an Issue edit.** Hand-build the Resume scenario's branch and run worktree, and give `.agents/issues/<slug>.md` a body that differs from the Spec copy. Run the same turn. The `resume.py` output in `turn-01.jsonl` holds both `Resuming from the Halt record: 1 findings` and the Issue-changed line, each on its own line, and the run starts its fixing Iteration without a question.
- **Resume with an unchanged Issue.** Hand-build the same branch and run worktree, with the Issue's body equal to the Spec copy's body. Run the same turn. The run resumes from the existing Steps and `turn-01.jsonl` holds no `The Issue changed after this run started` text anywhere. The expected result comes from the Issue's body in the Tracker, which the change does not produce. Run it three times; all three must pass with no re-run.
- **Resume with no Spec copy.** Hand-build branch `<slug>` and its run worktree `.agents/worktrees/<slug>` with no `spec.md` under `.agents/runs/<slug>/` and no Step files, and give `.agents/issues/<slug>.md` any body. Run the same turn and let it land; read only the transcript and the landed commit. `turn-01.jsonl` holds no `The Issue changed after this run started` text, and shows the session writing `.agents/runs/<slug>/spec.md` as the Issue's title as an H1 followed by its body and committing it as `spec: <slug>`. Run it three times; all three must pass with no re-run.

## Gotchas

- Expect 4 to 10 agents and well over the default `--budget` of 10 dollars for anything bigger than the example; raise `--budget` and `--timeout` to match.
- The Verifier runs `## How to Check It` as the named person would, and skips checks that need live systems; a Spec whose only checks need the network proves nothing here.
- The worktree sits under the scratch repo at `.agents/worktrees/<slug>`, and the run adds that path to an ignore file; `verify.py cleanup` removes it with the scratch repo.
- To measure what a change costs across `/implement` runs, use `benchmark/` instead. One verify run proves behaviour, not cost.
