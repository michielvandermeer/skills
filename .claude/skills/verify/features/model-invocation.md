# Model invocation

A skill without `disable-model-invocation: true` is reached when a plain request matches its description. The description is the trigger, so an edit to a description is proven by a request that should fire it and one that should not. A skill with the flag set is reached only by its slash name.

## Sub-features

- `invoke-fires` a request in a skill's own words loads that skill.
- `invoke-stays-quiet` a nearby request that is another skill's job loads the other skill, or none.
- `invoke-user-only` a request that matches a user-only skill's description does not load it.

## How to get to it (user POV)

- Type a request in plain words, with no slash command.

## Driving it with verify.py

Preconditions:

- A fresh run. For a skill that needs repo state, the state its feature file names.
- The skill's `description:` line, read from its `SKILL.md`.

- **Fires.** Run `verify.py turn <run> "<request in the description's terms>"`. The summary shows `skills:<name>` under `skills invoked by the model this turn`, and `skill bodies loaded from` names `<checkout>\skills\<name>`. Example: "the tests are failing with a null reference — debug this" fires `skills:diagnosing-bugs`.
- **Stays quiet.** In a fresh run, send a request near the edge of the description that another skill owns. The summary shows the other skill or none.
- **User-only.** In a fresh run, send a request that matches a user-only skill, such as "set up the issue tracker for this repo" for `/skills:setup`. No `skills:setup` appears under `skills invoked by the model`.

## Gotchas

- The user's other plugins load too and compete for the same request: pstack's SessionStart hook routes multi-file work to `pstack:poteto-mode`. A request that lands on a pstack skill is a real-path result, not a harness fault; record which skill won.
- One run of a routing check is one sample. Repeat a borderline request in fresh runs before calling a description fixed.
