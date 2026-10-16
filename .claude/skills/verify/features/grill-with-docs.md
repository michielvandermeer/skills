# Grill with docs

`/skills:grill-with-docs` interviews the user round by round about a plan, writes the glossary (`CONTEXT.md`) and ADRs as terms and decisions settle, and ends with a read-back. A confirmed read-back that names a change becomes a Spec on an Issue, committed with the docs; one that names no change writes no Spec.

## Sub-features

- `grill-rounds` asks the open questions as a numbered set with lettered options, and waits.
- `grill-docs` writes `CONTEXT.md` before the next round, and `docs/adr/NNNN-slug.md` when a decision passes the ADR tests.
- `grill-explorer` sends every question about the code to a `skills:explorer` agent instead of asking the user.
- `grill-spec` ends a confirmed change in a Spec on `.agents/issues/<slug>.md`, status `ready-for-agent`, in one commit with the docs, after a `skills:validator` check.
- `grill-no-change` ends without a Spec, closing the starting Issue as not planned.
- `grill-retro` runs `/retro` at the end.

## How to get to it (user POV)

- Type `/skills:grill-with-docs <the plan>` or `/skills:grill-with-docs <Issue path>`.
- It is user-only: a plain request reaches `/grilling`, not this skill.

## Driving it with verify.py

Preconditions:

- A run through [setup](setup.md)'s local journey, so the Tracker ref exists.
- A small, real plan the scratch repo can hold, such as "add a `greet(name)` function to a new `greet.py` that returns `Hello, <name>!`, with a unittest". A plan with one domain term ("greeting") gives the glossary something to record.

- **Start.** Run `verify.py turn <run> "/skills:grill-with-docs <plan>"`. The final message is round 1: questions numbered `Q1..Qn`, each with lettered options.
- **Answer rounds.** Run `verify.py turn <run> "Q1: a, Q2: b"` with the answer a user would give, one turn per round. After each turn, `scratch-NN.txt` shows `CONTEXT.md` once a term has settled.
- **Read-back.** When no question is left, the final message is a read-back asking whether understanding is shared. Run `verify.py turn <run> "yes"`.
- **Proof.** The scratch repo has one commit staging, by name, `CONTEXT.md`, any ADR, and `.agents/issues/<slug>.md` with `Status: ready-for-agent` and the Spec's sections. The summary shows a `skills:validator` dispatch. `/retro` may add one more commit.
- **No change.** In another run, answer the read-back with a plan that drops the work. No Spec is written; the final message says why.

## Gotchas

- The session runs on Opus at high effort and each round is a turn: a full run is slow and costs several dollars. Keep the plan small.
- The skill pulls first. The scratch repo has no remote, so the pull fails and the run continues; a failure here that stops the run is a finding.
- Answering more than the round asked steers the skill; answer only what is asked.
