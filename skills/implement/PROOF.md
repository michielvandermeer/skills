# Proof

The Step agent, the Checker, the Prover, and the Proof fixer read this. A Step is **Green** only with a **Proof** of its **Safety fact** that the Checker re-ran and saw ([ADR-0053](../../docs/adr/0053-green-needs-a-proof.md)). Before the run lands, a **Prover** re-runs every Proof once more, on the code that lands ([ADR-0058](../../docs/adr/0058-a-prover-re-proves-the-code-that-lands.md)).

## Safety fact

One per Step: the one fact the change is safe because of, naming what breaks if it is false. "It compiles" names nothing that breaks. A Step that changes no code that runs — docs, comments — has none.

## Merge risk

One per Step, beside its Safety fact: how hard the change is to undo once it lands, and what it would affect if it went wrong. It is `easy` when reverting the Step's commit restores the old behaviour, and `hard` when something stays changed after the revert — data written, a migration run, a file format or API others already read, a release published. It informs the final report and a pull request description; it never stops the run.

## The ladder

1. Stated, or read in the code. Not Proof.
2. The existing tests pass.
3. A test or throwaway script calls the real code on the risky path and would fail if the fact were false.
4. Reproduced in the running app through the **Run recipe**.

A Step needs rung 3, and rung 4 when it changes what a person or client sees through a running surface — a web page, a command-line tool, an HTTP service. A library tops out at rung 3. When rung 4 is out of reach — the app needs a live system, credentials, or a paid account to start, or how to launch it cannot be worked out — rung 3 stands and the deviations line says why.

## What counts as Proof

- Command-line tool: the command, its exit code, an output excerpt.
- HTTP service: the request and a response excerpt.
- Web page: a saved screenshot and the steps driven.
- Library: the throwaway script's output.

A Proof names the narrowest command that shows its Safety fact: one test, a test run filtered to the tests that exercise the fact, or the throwaway script. A run of a whole project or the whole suite is the Checker's Green check, not a Proof, and the Prover never re-runs it as one.

Every script, screenshot, and transcript goes in the Proof folder the prompt names, `<git common dir>/proof/<slug>/` — outside every working tree, so no commit sweeps it in. The folder is run scratch: the run's final cleanup deletes it, and a halt leaves it for the resume.

## The Outcome entry

Three lines in the Step file's `## Outcome`, exactly:

```
Safety fact: <the fact, naming what breaks if it is false> (rung <N>)
Proof: `<command>` exit <code> — <excerpt of at most three lines, or the file in the Proof folder>
Merge risk: <easy | hard — what stays changed after a revert>; affects <who or what would notice if it went wrong>
```

A Step with no Safety fact writes `Safety fact: none — <why no code that runs changed>`, and still writes its `Merge risk:` line. The Checker overwrites the first two lines with what its own re-run showed, and corrects the third where the commit shows something it missed, such as a migration. The Prover re-runs the `Proof:` line at the end of the run, after its author has gone, so the line names a command or a file in the Proof folder that runs on its own.

The Proof fixer retires a fact that a later Step changed as the Spec asks, by rewriting its line as `Safety fact: retired — Step <NN> changed it as the Spec asks: <the old fact>`. The Prover skips a retired fact.

## Re-running a Proof

A Proof that fails on a re-run — the Checker's or the Prover's — is re-run once. One that passes on the second run counts, and the flake goes on the deviations line. A flake the Run recipe caused — a readiness wait too short — is the recipe steering you wrong: the Checker corrects it, and the Prover names it on its deviations line.

## Run recipe

It lives at `.agents/refs/run-recipe.md`. In a repo with a `CONTEXT-MAP.md`, each context with a running surface keeps its own at `<context folder>/.agents/refs/run-recipe.md`, and a Step follows the recipe of each context whose code it changed. A repo with several apps and no `CONTEXT-MAP.md` keeps one root recipe, a section per app.

```markdown
# Run recipe

## Check
<commands that confirm what the app needs before launch; each exits 0 when it holds>

## Launch
## Ready
<how to tell the app is up>

## Drive
## Evidence
<what to save in the Proof folder, and how>

## Clean up
```

Every section is plain shell commands that work on any host. A host's own browser tools may help write it; a browser drive goes in a script the recipe runs. Nothing in it touches a live system ([ADR-0028](../../docs/adr/0028-implement-claims-its-issue-and-pushes-only-what-lands.md)).

- **No recipe yet**, and the Step needs rung 4: the agent that first has to drive the app writes it, from what the repo already says — README, `AGENTS.md`, package scripts, a project skill that launches the app.
- **A recipe exists**: follow it as written. Edit it only where it steered you wrong.

A new or corrected recipe goes in the Step's commit, and the Outcome says so in one line: `Run recipe: written` or `Run recipe: corrected — <what was wrong>`.
