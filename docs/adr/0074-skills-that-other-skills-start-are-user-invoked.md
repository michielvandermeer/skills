# Skills that other skills start are user-invoked

`/to-spec`, `/validate-spec`, `/retro`, and `/resolving-merge-conflicts` are steps of other skills. `/triage`, `/grill-with-docs`, `/wayfinder`, and `/prototype` end in `/to-spec`. The Validator runs `/validate-spec`. The Named session skills end in `/retro`. `/implement` and `/hillclimb` hand a rebase conflict to `/resolving-merge-conflicts`. As model-invoked skills, the agent could also start any of them on a plain request, outside the skill whose step it is. So they are user-invoked, and a caller's step reaches one by path: it links the skill's `SKILL.md` and says to read and follow it. The host refuses to load a user-invoked skill for the agent, so a bare `/to-spec` in a step would never fire.

## Considered Options

- **Keeping them model-invoked.** Rejected: a prompt could start a Spec, a Retrospective, or a conflict resolution on its own, and each description sat in context on every turn.
- **`user-invocable: false`.** Rejected: it hides a skill from the slash menu but leaves the agent free to load it, the opposite of what is wanted.
- **Copying each into its callers.** Rejected: four skills would carry copies of `/to-spec`, and a person could no longer type it.

## Consequences

- A caller that follows a skill by path keeps its own model. The skill's `model:` pin applies only when a person types it ([ADR-0049](0049-agents-are-pinned-in-their-agent-files.md)).
- `/to-spec` hands the Validator `/validate-spec`'s absolute path, because an agent file has no folder to resolve a relative link from.
- A skill that starts from a plain request that never names it stays model-invoked, such as `/grilling`, `/prototype`, `/code-review`, and `pr`. So does `/implement`, which a `/goal` starts ([ADR-0067](0067-implement-is-model-invoked-so-a-goal-can-start-it.md)).
