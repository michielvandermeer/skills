# Skill mechanics

The skill-specific branch of [`writing-for-agents`](SKILL.md): what changes when the document is a skill — frontmatter, the invocation choice, and router skills. Everything else about writing it is the universal reference in `SKILL.md`.

## Invocation

Two choices, trading the two loads:

- A **model-invoked** skill keeps a `description`, so the agent can fire it autonomously — and other skills can reach it. You can still type its name: model-invocation always _includes_ user reach; a description only ever adds agent discovery, never removes the human's. The description is the skill's top-level context pointer, forced to stay loaded at all times — permanent context load in exchange for discoverability. A model-invoked skill whose content is all reference is also one home for shared reference: another skill can invoke it, so reference needed by several skills lives in one place. Mechanics: omit `disable-model-invocation`, and write a model-facing description carrying the trigger branches (the pointer-writing rules in `SKILL.md` apply in full).
- A **user-invoked** skill strips the description from the agent's reach: the host loads it only when the human types its name. Zero context load, but it spends cognitive load — you are the index that must remember it exists. Mechanics: set `disable-model-invocation: true`; the `description` becomes human-facing — a one-line summary, trigger lists stripped.

Pick model-invocation only when the agent must reach the skill on its own — its work starts from a plain request that never names it, as with `pr` and `/hillclimb` — or a `/goal` must start it by name, as with `/implement`. A skill that fires by hand, or only from another skill's step, is user-invoked and pays no context load.

Another skill reaches a user-invoked skill **by path**: its step links the skill's `SKILL.md` with the path as the link text, says to read the file and follow it, and says the skill does not load as one — "read [`retro/SKILL.md`](../retro/SKILL.md) and follow it — `/retro` does not load as a skill". The host refuses to load a user-invoked skill for the agent, and its refusal tells the agent not to follow the skill any other way, so the step is dropped. A step that shows only `/retro`, even as the text of a link to the file, is often loaded as a skill: on 2026-10-17, 33 of 50 such steps were. Following by path also keeps the caller's model, where loading a skill would apply that skill's `model:` pin. The same link is how two skills share reference: a plain file one skill holds and the other links, such as `to-spec/PRINCIPLES.md`.

## Splitting by invocation

The invocation cut of splitting (the sequence cut lives in `SKILL.md`): split off a model-invoked skill when you have a distinct leading word that should trigger it on its own — a trigger word you actually use in your prompts. You pay context load for the new always-loaded description, so that independent reach has to be worth it.

## Router skills

When user-invoked skills multiply past what you can remember, that piled-up cognitive load is cured by a **router skill**: one user-invoked skill that names the others and when to reach for each, so the human has one skill to remember instead of many. It names them, and the human runs the one it points to.
