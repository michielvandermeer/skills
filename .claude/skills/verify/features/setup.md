# Setup

`/skills:setup` writes the repo's Tracker ref, `.agents/refs/tracker.md`, from one of the plugin's Tracker templates, shows the draft, and commits it once the user says yes. Every Tracker-reading skill depends on that file, so most other recipes start from a run that has been through this one.

## Sub-features

- `setup-local` writes the local Markdown template, unchanged, and commits it.
- `setup-update` reads an existing ref, shows its settings, and asks what should change.
- `setup-move` offers to move old local work (`.agents/issues/`, `.agents/ideas/`, `.agents/specs/`) into the new Tracker.
- `setup-github` and `setup-jira` fill in their template's settings and, on GitHub, create labels.
- `setup-verify` writes the repo's Verify skill at `.claude/skills/verify/`, proves it with one drive, and commits it. Run again, it is the upkeep pass.

## How to get to it (user POV)

- Type `/skills:setup` with no argument; the skill suggests a Tracker and asks to confirm.
- Type `/skills:setup local`, `/skills:setup github`, or `/skills:setup jira`; the argument is the pick.
- It is user-only (`disable-model-invocation: true`): a plain request never reaches it.

## Driving it with verify.py

Preconditions:

- `doctor` reports `doctor: ok`.
- A fresh run from `new`: an empty repo with one commit and no remote.

- **Start.** Run `verify.py turn <run> "/skills:setup local"`. The summary shows `slash commands this session: ['/skills:setup local']` and the skill body loaded from `<checkout>\skills\setup`. The final message names the Tracker as local Markdown, shows the draft, says nothing will be moved, and asks to go ahead. The scratch repo is unchanged.
- **Approve.** Run `verify.py turn <run> "yes"`. The final message reports the ref path and that no labels, moves, or offers applied.
- **Proof.** `scratch-02.txt` shows exactly one new commit touching only `.agents/refs/tracker.md`, and a clean status. The file matches the template line for line: `diff <(tr -d '\r' < <scratch>/.agents/refs/tracker.md) <(tr -d '\r' < skills/setup/LOCAL.md)` prints nothing.
- **No argument.** In a fresh run, `turn <run> "/skills:setup"`. With no remote, the skill suggests local Markdown and asks to confirm before drafting.
- **Update.** In the run above, before cleanup, `turn <run> "/skills:setup"` again. The skill shows the existing ref's settings and asks what should change.
- **Verify skill.** In a fresh run, commit a small command-line script, then `turn <run> "/skills:setup verify"`, answering any question in later turns. The scratch repo ends with one commit adding `.claude/skills/verify/SKILL.md` (frontmatter `name: verify`, no `disable-model-invocation`), `features/README.md`, and one file per feature with the four H2s. The final message names the evidence path of the proving drive, and that path exists after cleanup.

## Gotchas

- The session runs on Sonnet, the model the skill's frontmatter pins, whatever `--model` the turn passed.
- `setup-github` needs a real GitHub remote and `gh` signed in, and step 4 creates labels on it. `verify.py` denies `gh label *`, so the label step shows up under `denied tool calls`. That is the guard working; it does not prove label creation. Leave `setup-github` unverified rather than pointing a scratch repo at a real repository.
- The ref carries the template's CRLF line endings on Windows; compare with `\r` stripped.
