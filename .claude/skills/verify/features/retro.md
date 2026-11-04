# Retro

`/skills:retro` reads a Window of past sessions, acts only on a Lesson at least three of them show, applies High-priority changes to the repo's own files in one commit, files each Structural fix as an Issue, and lists what it applied and what it left.

## Sub-features

- `retro-structural` turns a Correction whose fix a shared module could rule out into a `needs-triage` Issue naming the fix and every other copy of the pattern, plus an interim Coding standards rule.
- `retro-nothing` ends in one line saying it found nothing.
- `retro-too-few` stops when the Window holds fewer than three sessions, and says how many it held. Driven on 2026-11-04.

## How to get to it (user POV)

- Type `/skills:retro` in a clean session; it reads the last 100 sessions in the repo.
- Type `/skills:retro past week` or `/skills:retro last 50` to name another Window.
- No skill runs it. It is user-only (`disable-model-invocation: true`).

## Driving it with verify.py

`verify.py turn` resumes one session, so a run holds one session and reaches `retro-too-few` only. `retro-structural` needs three earlier sessions in the same scratch repo, each fixing one copy of the bug, and `verify.py` has no way to start them yet. It was last driven on 2026-10-19, against the one-session skill.

Preconditions for `retro-structural`:

- A fresh run with `skills/setup/LOCAL.md` copied to `.agents/refs/tracker.md`, and four source files committed that share one bug, such as `src/cart.js`, `src/invoice.js`, `src/quote.js`, and `src/refund.js` all summing `parseFloat(price) * quantity`.

- **Corrections.** Three sessions each fix one file, such as "The cart total is wrong: ... Fix cartTotal in src/cart.js, add a test, and commit.". `src/refund.js` stays unfixed.
- **Retro.** Run `verify.py turn <run> "/skills:retro"`. The summary shows the body loaded from `<checkout>/skills/retro`.
- **Proof.** One new commit adds `.agents/issues/<slug>.md` with `Status: needs-triage`, `Category: enhancement`, the shared-module fix, and `src/refund.js` named as a copy, and adds the interim rule to `.agents/refs/coding-standards.md`. The Issue names that rule for deletion. The final message's applied list names the Issue.

## Gotchas

- The retro runs on Sonnet, the model the skill's frontmatter pins. Driven on 2026-10-19 for about $0.50.
- With short sessions the logs are small, so the retro reads them fast. Longer sessions make it slower, not different.
