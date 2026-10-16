# Run recipe

The Verifier reads this when the change alters what a person or client sees through a running surface — a web page, a command-line tool, an HTTP service — and a Hand check, or the Spec, needs the app running. A library has no running surface; its Hand check is a throwaway script that makes the call the check names.

It lives at `.agents/refs/run-recipe.md`. In a repo with a `CONTEXT-MAP.md`, each context with a running surface keeps its own at `<context folder>/.agents/refs/run-recipe.md`, and the Verifier follows the recipe of each context whose code the run changed. A repo with several apps and no `CONTEXT-MAP.md` keeps one root recipe, a section per app.

```markdown
# Run recipe

## Check
<commands that confirm what the app needs before launch; each exits 0 when it holds>

## Launch
## Ready
<how to tell the app is up>

## Drive
## Evidence
<what to look at to see the result — an output excerpt, a response, a screenshot saved to the scratch folder>

## Clean up
```

Every section is plain shell commands that work on any host. A host's own browser tools may help write it; a browser drive goes in a script the recipe runs. Nothing in it touches a live system ([ADR-0028](../../docs/adr/0028-implement-claims-its-issue-and-pushes-only-what-lands.md)).

- **No recipe yet**, and the app must run: the Verifier writes it, from what the repo already says — README, `AGENTS.md`, package scripts, a project skill that launches the app.
- **A recipe exists**: follow it as written. Edit it only where it steered you wrong — a readiness wait too short, a launch command that moved.

When the app cannot start — it needs a live system, credentials, or a paid account, or how to launch it cannot be worked out — each Hand check that needs it is skipped, and the deviations line says what it needs.

A new or corrected recipe is the Verifier's one commit, and its deviations line says so: `Run recipe: written` or `Run recipe: corrected — <what was wrong>`.
