# Skills other skills follow are read by path

A skill that is a step of other skills is read by path: the caller's step links the skill's `SKILL.md` with the path as the link text, says to read the file and follow it, and says the skill does not load as one. How a person or the agent can start the skill on its own depends on who needs it.

- **Library skills**, which only other skills need, set `disable-model-invocation: true` and `user-invocable: false`, so nobody starts them: `/grilling`, `/domain-modeling`, `/technical-writing`, `/to-spec`, and `/validate-spec`. The host registers none of them, so none of their descriptions sits in a session's context and none appears in the slash menu. In the 60 days before this change, nobody typed any of the five except once each for `/to-spec` and `/validate-spec`. Of the agent's 309 loads of `/grilling`, `/domain-modeling`, and `/technical-writing`, all but two came from another skill telling it to.
- **`/retro`** stays typed-only (`disable-model-invocation: true`), because a person also runs it on its own, such as over every session in the past week. The skills that end in it run it on the current session.
- **`/resolving-merge-conflicts`** is model-invoked and unpinned, so a plain "merge main and resolve the conflicts" loads it. `/implement` and `/hillclimb` still read it by path when a rebase conflicts.

A step whose link text was the bare `/to-spec` or `/retro` was still often loaded as a skill: the day after the path became the link text, 33 of 50 such steps were refused, and each was dropped.

## Considered Options

- **Keeping the Library skills model-invoked.** Rejected: each description sat in context on every turn for a request that almost never came, and a prompt could start a Spec on its own.
- **Making the Library skills typed-only, as `/retro` is.** Rejected: they would stay in the slash menu for commands nobody types, and each would need a model pin for when someone did ([ADR-0049](0049-agents-are-pinned-in-their-agent-files.md)).
- **`user-invocable: false` alone.** Rejected: it hides a skill from the slash menu but leaves the agent free to load it.
- **Moving the Library skills out of `skills/`.** Rejected: Tracker refs already copied into other repos name `skills/domain-modeling/CONTEXT-PATHS.md`, and every relative link between skills would change.
- **Copying each into its callers.** Rejected: four skills would carry copies of `/to-spec`, and fifteen of `/technical-writing`.

## Consequences

- A plain "grill me on this plan" request loads nothing. `/grill-with-docs`, `/triage`, `/wayfinder`, and `/prototype` reach `/grilling` and `/to-spec` through their own steps.
- A caller that follows a skill by path keeps its own model. A Library skill carries no `model:` pin.
- A sub-agent gets an absolute path, because an agent file has no folder to resolve a relative link from: `/to-spec` hands the Validator `/validate-spec`'s path, and `/code-review` and `/research` hand their agents `/technical-writing`'s.
- A skill that starts from a plain request that never names it stays model-invoked, such as `/prototype`, `/code-review`, `pr`, `/writing-for-agents`, and `/why`, which a "why does this work this way" question starts and which `/triage` and `/grilling` also run. So does `/implement`, which a `/goal` starts ([ADR-0067](0067-implement-is-model-invoked-so-a-goal-can-start-it.md)).
