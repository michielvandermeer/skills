# Verify skill

`/setup verify` writes the repo's **Verify skill**, a project skill at `.claude/skills/verify/` that drives the app the way a user does and captures evidence. When one already exists, follow [VERIFY-UPKEEP.md](VERIFY-UPKEEP.md) in place of the Create steps below. In a repo with a `CONTEXT-MAP.md`, each context with a running surface keeps its own at `<context folder>/.claude/skills/verify/`: work on the contexts the user names, or ask which.

The skill is named `verify` so that it replaces Claude Code's bundled `/verify`, and both a session and `/implement`'s Verifier reach it. Its frontmatter has no `disable-model-invocation`, so an agent can load it. Write it for the next agent, who reads it cold, mid-task, and has never seen the app.

## Create

### 1. Read the repo

Answer these from the code and its docs, and ask the user only what you cannot observe. An old Run recipe at `.agents/refs/run-recipe.md`, or under a context folder, is the first source to read. The commit at step 5 deletes it.

- **Surface**: what a user touches: a web UI, a command-line tool, a desktop app, an HTTP API, a mobile app, a library. A repo can have several. Pick the main one and note the rest.
- **Run**: how the app starts locally, from the repo's own scripts, Makefile, or README. Note ports, environment variables, seed data, and sign-in.
- **Drive**: how an agent can work it from a script. Existing harnesses come first: Playwright or Cypress specs, expect scripts, HTTP endpoints, a debug port. Only then a generic one: a browser over CDP for web and Electron, a PTY or tmux session for a command-line tool, plain HTTP for a service.
- **Observe**: what evidence a run can capture: screenshots, terminal transcripts, response bodies, logs, exit codes, database rows.
- **Isolate**: whether two instances can run side by side, with their own ports, data folders, and profiles. When they cannot, the skill says so and refuses to drive an instance it did not start.

A checkout that does not build or start as it is gets fixed first, or reported precisely. A missing file the app does not need but trips over at startup, such as a sample config, may be created by the skill, marked as verification setup, and removed in its cleanup.

Done: each of the five has an answer from the repo or from the user.

### 2. Write the skill

Write `.claude/skills/verify/SKILL.md`, with frontmatter `name: verify` and a `description` that names the app, its surface, and when to reach for it. Fill every section from what step 1 found, with real commands, paths, and handles from this repo:

- **Launch**: the exact command that starts the app for a run, how to tell it is ready, and how to stop it. Launch reaches a usable state from an empty data folder, migrations and seed data included. Ready means usable: a health check can pass while the database is still loading. A short-lived command-line tool has nothing to keep running: build it once, then give each drive its own PTY session.
- **Doctor**: one read-only check of whether this instance is worth driving: the process is up, the build is the right one, the port is ours, the sign-in works. An agent runs it first, and again whenever something looks wrong.
- **Drive**: the harness, with stable handles from this repo, such as ARIA roles and names, data attributes, prompt strings, and routes, in place of coordinates or tab order.
- **Evidence**: what a proof captures and where it goes. A proof drives the real user path, never a test-only endpoint or an internal setter. It captures the action and the state it left, not only the last screen, and it checks side effects: files written, rows stored, messages sent. A mock stands only where a production boundary already isolates the outside system. A dry-run mode is checked for what it really skips, by watching files, the network, and git refs.
- **Cleanup**: how to stop what the run started, by the process or container it started, never by name. Cleanup removes instances and scratch state and keeps the evidence, in a place the skill names.
- **Helpers**: every script the skill ships is executable, and the skill shows how to call it.

Every command is a plain shell command that runs on any host, and a browser drive lives in a script the skill ships. Nothing in the skill touches a live system ([ADR-0028](../../docs/adr/0028-implement-claims-its-issue-and-pushes-only-what-lands.md)).

Done: every section is written, with no placeholder left.

### 3. Seed the feature map

Write `.claude/skills/verify/features/README.md` and one file per user-facing feature, three to five to start, picked from the routes, commands, menus, or docs. The README holds the baseline preconditions, the driving conventions, the proof and skip rules, and an index with one line per feature file. Each feature file follows [VERIFY-EXAMPLE.md](VERIFY-EXAMPLE.md): an H1, one paragraph on what the user sees, then four H2s in this order:

1. `Sub-features`: short ids, one line each.
2. `How to get to it (user POV)`: every way a user reaches it.
3. `Driving it with <harness>`: `Preconditions:`, then one bullet per action, each with the exact command and what it shows.
4. `Gotchas`: what can waste or spoil a run.

A journey whose precondition the seed data lacks fails, and the reason goes in that feature's Gotchas. The journey stays whole. A proof of a feature drives every entry point its file lists.

Done: the README indexes every feature file, and each has the four sections.

### 4. Prove it

Follow the new skill end to end once: launch, doctor, drive one mapped feature, capture its evidence, clean up. Then check the evidence is still where the skill says. Fix what fails, and run the skill's cleanup after every failed attempt so nothing is left running. A run in a stand-in, such as a container in place of a fresh machine, lists every setup step the stand-in did that the real target will not. Those steps stay unproven.

Done: one full pass succeeded, and its evidence survived the cleanup.

### 5. Commit and report

Commit the skill's folder, any startup fix from step 1, and the deletion of an old Run recipe, staged by name, in one commit. Report the surface, the features mapped, the feature the proof drove with its evidence path, and what stayed unproven. Say that `/setup verify` run again is the upkeep pass.

Done: the commit exists, and the report names the proof's evidence.
