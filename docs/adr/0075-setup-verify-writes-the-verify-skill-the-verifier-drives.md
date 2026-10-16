# /setup verify writes the Verify skill the Verifier drives

A consuming repo's app is driven through its **Verify skill**, a project skill at `.claude/skills/verify/` with Launch, Doctor, Drive, Evidence, and Cleanup sections and a feature map that holds one recipe per user-facing feature. `/setup verify` writes it, proves it with one full drive before committing it, and on a later run keeps it current: one explorer per feature reads the source for drift, then every feature is driven live. `/implement`'s Verifier follows it for a Hand check on a running surface, and `/pr` follows it for a screenshot. Both come from pstack's `create-verification-skill` and `maintain-verification-skill`.

The skill is named `verify`. A project skill by that name replaces Claude Code's bundled `/verify`, so a person, a session, and the Verifier all reach the same one.

## Considered Options

- **Keeping the Run recipe**, `.agents/refs/run-recipe.md`, written by the first Verifier that needed the app. Replaced: a Verifier wrote it in the middle of a run, nobody proved it before it was used, and it held one flow, where a feature map holds one recipe per feature with every way a user reaches it.
- **Both, the Run recipe for the Verifier and the Verify skill for people.** Rejected: two records of how to run the app drift apart, and each fix lands in one of them.
- **The Verifier writes the Verify skill when the repo has none.** Rejected: writing one well takes a full proving drive, which is a setup task with a person present, not a step inside an unattended run.
- **Two skills, as pstack has them.** Rejected: creating and keeping the skill current are one job on one folder, and `/setup` already updates what it wrote when it finds it there.

## Consequences

- A repo with no Verify skill gets its Hand checks on a running surface skipped, each with the deviation `no Verify skill: run /setup verify`.
- The Verifier corrects the Verify skill only where it steered it wrong, as its one commit. `/retro` treats that edit as a Correction and adds a doctor check when one could have caught it ([ADR-0050](0050-retro-learns-from-corrections.md)).
- In a repo with a `CONTEXT-MAP.md`, each context with a running surface keeps its own Verify skill under its folder.
- `/setup verify` reads an old Run recipe first and deletes it in its commit.
