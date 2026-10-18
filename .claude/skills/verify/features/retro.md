# Retro

`/skills:retro` reads the session it closes, applies High-priority changes to the repo's own files in one commit, files each Structural fix as an Issue, and lists what it applied and what it left.

## Sub-features

- `retro-structural` turns a Correction whose fix a shared module could rule out into a `needs-triage` Issue naming the fix and every other copy of the pattern, plus an interim Coding standards rule.
- `retro-nothing` ends in one line saying it found nothing.

## How to get to it (user POV)

- Type `/skills:retro` at the end of a session; it reads that session.
- Type `/skills:retro <session>` to read another one.
- A Named session skill, such as `/implement` or `/grill-with-docs`, runs it when it finishes. It is user-only (`disable-model-invocation: true`).

## Driving it with verify.py

Preconditions:

- A fresh run with `skills/setup/LOCAL.md` copied to `.agents/refs/tracker.md`, and two source files committed that share one bug, such as `src/cart.js` and `src/invoice.js` both summing `parseFloat(price) * quantity`.

- **Correction.** Run `verify.py turn <run> "The cart total is wrong: ... Fix cartTotal in src/cart.js, add a test, and commit."`. The agent fixes only `src/cart.js`.
- **Retro.** Run `verify.py turn <run> "/skills:retro"`. The summary shows the body loaded from `<checkout>/skills/retro`.
- **Proof.** One new commit adds `.agents/issues/<slug>.md` with `Status: needs-triage`, `Category: enhancement`, the shared-module fix, and `src/invoice.js` named as a copy, and adds the interim rule to `.agents/refs/coding-standards.md`. The Issue names that rule for deletion. The final message's applied list names the Issue.

## Gotchas

- The retro runs on Sonnet, the model the skill's frontmatter pins. Driven on 2026-10-19 for about $0.50.
- With only one turn of session work, the session log is small, so the retro reads it fast. A longer setup turn makes it slower, not different.
