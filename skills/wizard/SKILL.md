---
name: wizard
description: Wizard generation for steps only a person can perform. Use when provisioning infrastructure, setting up credentials or CI secrets, walking an unfamiliar third-party dashboard, or running a one-off migration or cutover.
---

# Wizard

Generate a Wizard from [template.sh](template.sh). The library above the `STAGES` marker is identical in every Wizard; author Stages below it. A Wizard is ephemeral by default: built for one run, saved to a scratch or `scripts/` path, deleted when the job is done. Commit it only when the user wants a repeatable setup path that should live in the repo. Those scripts do not go under `.agents/`.

The Driving session writes the script. The person runs it in their own terminal.

## Process

### 1. Scope the procedure

Work out every manual step the person must take and every value that gets captured along the way. Read the repo first:

- For setup: `.env`, `.env.example`, `.env.*`, `README`, `docker-compose*`, framework config, and `.github/workflows/*` (every `secrets.*` / `vars.*` reference is a value the Wizard must produce).
- For a migration or transition: the current state, the target state, and the irreversible actions between them.

Then show the user the ordered list of Stages and the values each produces, at the bar the `/plain-language` skill sets, and confirm: they may add, drop, or reorder.

**Done when:** every Stage is named in order, and for each captured value you know (a) where the person gets it, (b) where it is written (`.env`, a GitHub secret, both, or nowhere; some Stages are pure actions), and (c) whether it is secret (hidden entry) or public.

### 2. Map each Stage's journey

For each Stage, write the precise path a person follows: which URL to open, what to do there, where a value is shown, which variable it fills — e.g. "Dashboard → Developers → API keys → Reveal test key → copy". Where you do not know the current UI or the exact command, ask the user or check the docs.

**Done when:** every Stage traces to concrete instructions a stranger could follow.

### 3. Author the Wizard

Ask whether this is a one-off or a repeatable setup path. Copy `template.sh` to a scratch or `scripts/` path in the open repo (repeatable paths go under `scripts/`). Replace the example Stage with one `stage` per confirmed Stage, in dependency order. Use the library helpers: `stage`, `say`/`step`, `open_url`, `ask`/`ask_secret`, `write_env`, `set_secret`/`set_var`, `pause`/`confirm`. Set `TOTAL_STAGES` to the number of Stages you wrote. Leave the library above the marker unchanged.

Hold the bar the template sets: open the URL before asking for its value, use `ask_secret` for anything secret, `write_env` every persisted value, `set_secret` only the values CI actually needs, and `confirm` before any irreversible action. Each `stage` clears the screen so only the current Stage is visible: keep a Stage to one focused task so nothing the person needs scrolls away.

**Done when:** the script has one `stage` per confirmed Stage, `TOTAL_STAGES` matches, and the library above the marker is unchanged.

### 4. Verify and hand off

- `bash -n <script>`; run `shellcheck` if available.
- `chmod +x <script>`.
- Trace it statically: every value from scoping is captured and lands where scoping said, and every `set_secret` name exactly matches a `secrets.*` reference in CI.

Trace statically; do not run the Wizard end to end yourself — it opens browsers and blocks on human input.

Tell the user how to run it, at the bar the `/plain-language` skill sets. A key pasted into chat while scoping still enters the session, like any other pasted text. If this is a repeatable setup path, commit the script and link it from the README so the next person runs the script instead of asking an agent.

**Done when:** the script is executable, the static trace holds, and the person has the command to run it.
