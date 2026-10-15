# Setup

`/skills:setup` has two parts. Tracker writes the repo's Tracker ref, `.agents/refs/tracker.md`, from one of the plugin's Tracker templates, shows the draft, and commits it once the user says yes. Models writes the user's `<config>/pstack-models.md`, the sheet that picks each pstack role's model and effort and turns the SessionStart hook on or off, and adds an `@` include for it to `<config>/CLAUDE.md`. Every Tracker-reading skill depends on the Tracker ref, so most other recipes start from a run that has been through `setup-local`.

## Sub-features

- `setup-local` writes the local Markdown template, unchanged, and commits it.
- `setup-update` reads an existing ref, shows its settings, and asks what should change.
- `setup-move` offers to move old local work (`.agents/issues/`, `.agents/ideas/`, `.agents/specs/`) into the new Tracker.
- `setup-github` and `setup-jira` fill in their template's settings and, on GitHub, create labels.
- `setup-models` shows every pstack role with its model, asks for the default effort and the hook, and writes the sheet.

## How to get to it (user POV)

- Type `/skills:setup` with no argument; the skill runs Tracker, suggesting a Tracker and asking to confirm, then Models.
- Type `/skills:setup local`, `/skills:setup github`, or `/skills:setup jira`; the argument is the pick, and only Tracker runs.
- Type `/skills:setup models`; only Models runs.
- It is user-only (`disable-model-invocation: true`): a plain request never reaches it.

## Driving it with verify.py

Preconditions:

- `doctor` reports `doctor: ok`.
- A fresh run from `new`: an empty repo with one commit and no remote.
- For `setup-models`: a copy of `<config>/pstack-models.md` and `<config>/CLAUDE.md` as they were, or a note that they were absent.

- **Start.** Run `verify.py turn <run> "/skills:setup local"`. The summary shows `slash commands this session: ['/skills:setup local']` and the skill body loaded from `<checkout>\skills\setup`. The final message names the Tracker as local Markdown, shows the draft, says nothing will be moved, and asks to go ahead. The scratch repo is unchanged.
- **Approve.** Run `verify.py turn <run> "yes"`. The final message reports the ref path and that no labels, moves, or offers applied. It does not start Models.
- **Proof.** `scratch-02.txt` shows exactly one new commit touching only `.agents/refs/tracker.md`, and a clean status. The file matches the template line for line: `diff <(tr -d '\r' < <scratch>/.agents/refs/tracker.md) <(tr -d '\r' < skills/setup/LOCAL.md)` prints nothing.
- **No argument.** In a fresh run, `turn <run> "/skills:setup"`. With no remote, the skill suggests local Markdown and asks to confirm before drafting.
- **Update.** In the run above, before cleanup, `turn <run> "/skills:setup"` again. The skill shows the existing ref's settings and asks what should change.
- **Models.** In a fresh run, `turn <run> "/skills:setup models"`. The summary reads `plugin files read this turn` with `skills/setup/MODELS.md`. The final message lists every role in MODELS.md's sheet shape with its model and asks to accept or change them. Answer each question in its own turn, accepting the defaults and keeping the hook on. **Proof:** `<config>/pstack-models.md` matches the shape in MODELS.md's step 6, `<config>/CLAUDE.md` has one `@` line naming it, and the scratch repo has no new commit. Then put both files back as the precondition found them.

## Gotchas

- The session runs on Sonnet, the model the skill's frontmatter pins, whatever `--model` the turn passed.
- `setup-github` needs a real GitHub remote and `gh` signed in, and step 4 creates labels on it. `verify.py` denies `gh label *`, so the label step shows up under `denied tool calls`. That is the guard working; it does not prove label creation. Leave `setup-github` unverified rather than pointing a scratch repo at a real repository.
- `setup-models` writes the user's real config, not the scratch repo: the sheet changes every later session's models and hook. Restore both files after the run.
- The ref carries the template's CRLF line endings on Windows; compare with `\r` stripped.
