# Skills verification map

The maintained source for verifying what a user of this plugin sees. Read this index, then the feature file for the skill under test, and drive it with `verify.py` as [../SKILL.md](../SKILL.md) describes.

## Baseline preconditions

- `python .claude/skills/verify/verify.py doctor` reports `doctor: ok`.
- Each journey runs in a run from `verify.py new`: a scratch repo with one commit and no remote, and its own session.
- A Tracker-reading skill needs [setup](setup.md)'s local journey first.

## Driving conventions

- One user message per `verify.py turn`. Send the slash command or plain request a user types, then answer each question in its own turn.
- Answer as the user would: only what was asked, in the form asked.
- Prepare repo state, such as a file to review or an Issue to implement, by writing and committing it in the scratch repo before the first turn. State the skill should produce is left to the skill.

## Proof and skip reporting

- Every proof names the run folder, the plugin commit from `meta.json`, and whether the tree was dirty.
- Prove an end state by reading the scratch repo or the transcript, not the final message.
- Report a journey that could not reach its end state with the turn that stopped and the precondition that was missing. Never shorten the journey to make it pass.
- A journey not driven stays unverified, even when a neighbouring one passed.

## Feature entry contract

Each feature file has an H1, one paragraph on the user-visible behaviour, and four H2s in order: `Sub-features`, `How to get to it (user POV)`, `Driving it with verify.py` (starting with `Preconditions:`), and `Gotchas`.

## Features

- [Setup](setup.md) — writes and commits the Tracker ref, and writes pstack's model sheet. Driven end to end on 2026-10-15.
- [Grill with docs](grill-with-docs.md) — rounds, glossary and ADRs, a Spec on a confirmed read-back.
- [Implement yolo](implement-yolo.md) — a poteto-mode run on the current branch, landed as one commit.
- [Model invocation](model-invocation.md) — whether a description fires on a plain request.

Not yet mapped: the other skills, and `/implement`'s worktree path.
