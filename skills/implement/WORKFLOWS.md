# Workflows

Every Step names one **Workflow** on its `Workflow:` line. The Workflow sets the Step agent's first move, what the Safety fact names, the Outcome's **workflow line**, and what the Checker checks beyond the Proof ([ADR-0068](../../docs/adr/0068-a-step-names-its-workflow.md)). A Step file with no `Workflow:` line is `feature`.

Read this file by section: `grep -n '^#'` it, then read [Every workflow](#every-workflow) and the one section your Step's `Workflow:` line names. The Planner, and a Driving session that writes its own Step file, read only the table below.

| Workflow | Pick it when the Step | First move | Workflow line |
|---|---|---|---|
| `feature` | adds or changes behaviour | name the data shape | `Shape:` |
| `bug-fix` | corrects behaviour a report says is wrong | a repro that goes red on the reported symptom | `Root cause:` |
| `refactor` | changes structure and holds behaviour: a prefactor, each stage of a Wide refactor | pin the behaviour | `Reader load:` |
| `perf` | moves a measured number past a target and holds behaviour | measure the baseline | `Measure:` |
| `visual-parity` | must render identically to a baseline: a styling migration, a port of a screen | capture the baseline | `Diff:` |

## Every workflow

**The starting code** is the code as it stood at the Step's fixed point, the parent of the Step agent's commit. Before the Step agent changes anything, it is the tree in front of it. After the commit, run a command against it in place, before any change of your own and only while `git status` is clean: `git diff --binary <fixed point> HEAD -- <each path the Step changed outside its tests> | git apply -R --index`, run the command, then `git reset --hard HEAD` puts the Step back, files it added or deleted included.

The Step agent and the Checker keep these on every Step, and a breach in the Step's diff is a Checker finding. The Coding standards win where they differ.

- **Subtract first.** Delete the dead code, one-caller wrappers, and redundant checks on your path before you add the new shape.
- **One wave.** A changed internal API moves every caller and deletes the old form in the same Step. A Wide refactor the Planner sequenced as expand–contract is the one exception.
- **Root causes.** Fix a failure where it starts. A guard that silences a symptom, such as a null check, a catch-all, or a retry, without the reason the symptom happened, is a finding.
- **Guards at the boundary.** Parse and validate input where it enters: a request, the command line, config, a file, an external API. Trust internal types past that point. Where the language lets you, make illegal states unrepresentable in the types.
- **Tests test behaviour.** Call the code the way its callers do, and assert a literal expected value. A test that would still pass if the code under test returned nothing is rewritten or deleted. Mock only at the system boundary.
- **Comments say why.** A comment carries a non-obvious reason the code cannot show. A comment that narrates the next line is deleted.

## feature

**Shape first.** Before any logic, name the data shape and the structure that organizes it. Take it from the Spec's Implementation Decisions. Where the Spec leaves it open, pick the structure that encodes the domain: a state machine over scattered booleans, a table or registry over branching spread across files, a typed model over a repeated shape assumption, a discriminated union over flags. Plain code stays when the shape is already clear and local.

- **Workflow line**: `Shape: <the data shape and the structure that organizes it>`, or `Shape: existing — <the shape it extends>`.
- **Checker**: the code holds the shape the `Shape:` line names. Branching the shape should have absorbed is a finding.

## bug-fix

Every line the Step ships traces to runtime evidence.

1. **Repro first**, before you read code for a theory. Build a *tight* command that goes red on the reported symptom on the starting code, by the ways [diagnosing-bugs](../diagnosing-bugs/SKILL.md) lists under Ways to construct one and Non-deterministic bugs; read only those two parts. A symptom seen through a running surface is reproduced there, through the Run recipe. Save the red output in the Proof folder. When no way goes red, report `blocked` and name each way you tried: a bug that never went red cannot be proven fixed.
2. **Find the cause.** When the Spec names the cause, one probe that confirms it is enough. Otherwise rank three to five falsifiable hypotheses and test each. A probe changes one variable: a debugger, or a log line tagged `[DEBUG-<four hex digits>]`. Revert everything a disproved hypothesis motivated.
3. **Regression test, then fix.** Turn the repro into a test at a seam that reaches the real bug pattern, and watch it fail. Make the smallest change the evidence justifies, watch the test pass, and re-run the original repro. When no seam reaches the pattern, the repro script is the Proof and the missing seam goes on the deviations line.
4. Remove every `[DEBUG-` line. A search for the tag finds none.

- **Safety fact**: the reported symptom no longer occurs, naming the input that showed it. Its Proof is the regression test or the repro, and the excerpt also names the red output saved in step 1.
- **Workflow line**: `Root cause: <the mechanism, and the runtime evidence that confirmed it>`.
- **Checker**: runs the Proof against the starting code and sees it fail on the symptom's assertion. A build error is not red: a test that calls what the fix added cannot build there, so run the step 1 repro instead. A Proof that passes without the fix proves nothing, so produce one that goes red. A line of the fix that the `Root cause:` line does not explain is a finding.

## refactor

A missing feature or a real bug the Step uncovers goes on the deviations line, not into this Step.

1. **Pin first.** Before structure moves, hold the behaviour with a pin that calls the real code: a characterization test, a snapshot, or an equivalence script that diffs old and new output. The pin passes on the starting code. Existing tests are the pin only where a change of behaviour would fail them. A type check or a lint is no pin.
2. **Name the target shape**: the module layout, the types, and the call graph you would build today, from the domain rather than from the code it replaces.
3. **Move in small steps.** Subtract, then move, keeping the pin green after each move. Check a rename with a search over strings, docs, and config as well as code.
4. **Reader load.** The Step leaves fewer layers, branches, wrappers, or pieces of hidden state between a question and its answer. Revert a move that lowers none of them. The expand and migrate stages of a Wide refactor are exempt: their reader load is counted at its contract Step.

- **Safety fact**: behaviour is unchanged on the path the pin covers. Its Proof is the pin.
- **Workflow line**: `Reader load: <what got simpler, counted in layers, branches, wrappers, or files>`, or `Reader load: counted at Step <NN>` for an expand or migrate stage.
- **Checker**: runs the pin against the starting code as well, where the pin's calls exist there. It passes on both sides, or behaviour moved. New behaviour in the diff is a finding.

## perf

Each change is tied to a measurement. A Spec that names no target takes any gain past noise as the target.

1. **Baseline first.** Write the measuring command the way [hillclimb/MEASURE.md](../hillclimb/MEASURE.md) writes its script: a median of at least three runs, with the work count and the error count, after a sensitivity check. Run it on the starting code before any change.
2. **Find the limiter** before you pick a change, as MEASURE.md's Finding the limiter says.
3. **Try the cheapest idea first**, in this order, and stop at the first that meets the target: don't do it; do it, but don't do it again; do it less; do it later; do it when nobody is waiting; do it concurrently; do it cheaper.
4. **Measure after**, alternating the starting code and yours, as MEASURE.md's Judging a pair says. A gap smaller than the run-to-run spread is no change, and a changed work or error count means work was skipped. Revert either.

Measure the starting code in its own copy, so both sides can run in turn: delete `<proof>/before` if it is there, create it, and run `git archive <fixed point> | tar -x -C <proof>/before`. Deleting the Proof folder removes it.

- **Safety fact**: the behaviour the optimisation could break, such as a cache that must invalidate or an order that must hold. The number is not the Safety fact.
- **Workflow line**: ``Measure: `<command>` — <before median> → <after median> <unit> (<runs> runs per side, work and error counts equal)``.
- **Checker**: measures both sides again, alternating, and writes its own numbers on the `Measure:` line. A gain that no longer separates from noise fails the target, which is the Checker's to fix like any acceptance criterion.

## visual-parity

The baseline is the spec, and an image diff shows parity.

1. **Baseline first.** Before any change, capture a screenshot of each state of each component the Step touches, through the Run recipe, on the starting code. When the Step matches two implementations, capture the target. Use the repo's visual-regression harness when it has one. Otherwise write a script in the Proof folder that drives each state and diffs two sets of screenshots pixel by pixel.
2. **Freeze it.** Once captured, the harness and the baseline stay as they are, and no component is restructured to make a diff pass. A baseline that looks wrong is a `blocked` report that names it.
3. **One component at a time.** Migrate shared primitives first, then each component, and diff after each until the diff reads zero.

- **Safety fact**: each named state renders identically to its baseline. Its Proof is the diff command, at rung 4.
- **Workflow line**: `Diff: <the states compared> — <pixels that differ in each, 0 for parity>`.
- **Checker**: first recaptures the baseline on the starting code, or on the target, and diffs it against the saved one. Any difference means the saved baseline is not the starting code's, which is red. Then it re-runs the Step's diff. Any pixel that differs is red.
