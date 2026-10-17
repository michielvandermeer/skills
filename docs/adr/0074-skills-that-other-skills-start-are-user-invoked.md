# Skills that other skills start are user-invoked

`/to-spec`, `/validate-spec`, `/retro`, and `/resolving-merge-conflicts` are steps of other skills. `/triage`, `/grill-with-docs`, `/wayfinder`, and `/prototype` end in `/to-spec`. The Validator runs `/validate-spec`. The Named session skills end in `/retro`. `/implement` and `/hillclimb` hand a rebase conflict to `/resolving-merge-conflicts`. As model-invoked skills, the agent could also start any of them on a plain request, outside the skill whose step it is. So they are user-invoked, and a caller's step reaches one by path: it links the skill's `SKILL.md` with the path as the link text, says to read the file and follow it, and says the skill does not load as one. The host refuses to load a user-invoked skill for the agent, and its refusal tells the agent not to follow the skill any other way. A step whose link text was the bare `/to-spec` or `/retro` was still often loaded as a skill: the day after this change, 33 of 50 such steps were refused, and each was dropped.

## Considered Options

- **Keeping them model-invoked.** Rejected: a prompt could start a Spec, a Retrospective, or a conflict resolution on its own, and each description sat in context on every turn.
- **`user-invocable: false`.** Rejected: it hides a skill from the slash menu but leaves the agent free to load it, the opposite of what is wanted.
- **Copying each into its callers.** Rejected: four skills would carry copies of `/to-spec`, and a person could no longer type it.

## Consequences

- A caller that follows a skill by path keeps its own model. The skill's `model:` pin applies only when a person types it ([ADR-0049](0049-agents-are-pinned-in-their-agent-files.md)).
- `/to-spec` hands the Validator `/validate-spec`'s absolute path, because an agent file has no folder to resolve a relative link from.
- A skill that starts from a plain request that never names it stays model-invoked, such as `/grilling`, `/prototype`, `/code-review`, `pr`, and `/why`, which a "why does this work this way" question starts and which `/triage` and `/grilling` also run. So does `/implement`, which a `/goal` starts ([ADR-0067](0067-implement-is-model-invoked-so-a-goal-can-start-it.md)).
