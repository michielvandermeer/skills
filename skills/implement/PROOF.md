# Proof

The Step agent and the Checker read this. A Step is **Green** only with a **Proof** of its **Safety fact** that the Checker re-ran and saw ([ADR-0053](../../docs/adr/0053-green-needs-a-proof.md)).

## Safety fact

One per Step: the one fact the change is safe because of, naming what breaks if it is false. "It compiles" names nothing that breaks. A Step that changes no code that runs — docs, comments — has none.

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

Every script, screenshot, and transcript goes in the Proof folder the prompt names, `<git common dir>/proof/<slug>/` — outside every working tree, so no commit sweeps it in. The folder is run scratch: the run's final cleanup deletes it, and a halt leaves it for the resume.

## The Outcome entry

Two lines in the Step file's `## Outcome`, exactly:

```
Safety fact: <the fact, naming what breaks if it is false> (rung <N>)
Proof: `<command>` exit <code> — <excerpt of at most three lines, or the file in the Proof folder>
```

A Step with no Safety fact writes `Safety fact: none — <why no code that runs changed>`. The Checker overwrites both lines with what its own re-run showed.

## Re-running a Proof

A Proof that fails on the Checker's re-run is re-run once. One that passes on the second run counts, and the flake goes on the deviations line. A flake the Run recipe caused — a readiness wait too short — is the recipe steering you wrong: correct it.

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

Every section is plain shell commands that work on any host. A host's own browser tools may help write it; a browser drive goes in a script the recipe runs. Nothing in it touches a live system ([ADR-0028](../../docs/adr/0028-implement-claims-its-issue-and-stays-local.md)).

- **No recipe yet**, and the Step needs rung 4: the agent that first has to drive the app writes it, from what the repo already says — README, `AGENTS.md`, package scripts, a project skill that launches the app.
- **A recipe exists**: follow it as written. Edit it only where it steered you wrong.

A new or corrected recipe goes in the Step's commit, and the Outcome says so in one line: `Run recipe: written` or `Run recipe: corrected — <what was wrong>`.
