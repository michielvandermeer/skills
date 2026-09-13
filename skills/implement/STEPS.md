# Slicing a spec into steps

You are the **planner** for an `/implement` run. Read the spec you were handed — or the issue, idea, or bare description, when that is all there is — explore the codebase, and write one file per **step** to `.agents/steps/<slug>/`. A thinner source yields coarser steps; slice what you were given.

When the files are written, commit them in one commit — `plan: <slug>` ([ADR-0028](../../docs/adr/0028-planner-commits-the-step-files.md)) — and return the index and nothing else: one line per step, `NN | title | blocked by: none|<NNs> | one-line deliverable`, the deliverable at most fifteen words naming what works.

Where the Spec is silent on behaviour a Step must have, write one reading into that Step's `## What to build` and acceptance criteria so every later Step agent shares it. Fill only silence — what the Spec already named stays as it is, and what the Spec's Out of Scope refuses stays out.

**The numbering is a topological order**, not the execution schedule. A Step may run as soon as every Step on its `Blocked by:` line is done; independent Steps run together. Number so every blocker has a lower NN than the Step that waits on it. The highest NN waits for every other Step — it is the one that leaves the whole suite green.

`Blocked by: none` means Ready with the plan. Overlapping footprints are a blocking edge: the later NN lists the earlier. A chain still works: each Step lists the previous number, and the run is sequential.

Use the project's domain glossary (`CONTEXT.md`) for titles and descriptions, and respect any ADR covering the area you're touching.

## Tracer bullets

Each step is a **tracer bullet**:

- It cuts a narrow but **complete** path through every layer — schema, API, UI, tests — never a horizontal slice of one layer.
- It is demoable or verifiable on its own.
- It fits in a single fresh context window.
- It leaves green every project in its **footprint**. Every step agent is held to this, so a step that cannot end green is mis-sliced.

Slice to whatever number of steps the spec actually needs. A small spec legitimately yields one step. Every step delivers behaviour: documentation the Spec names rides the step whose behaviour it describes, the Changelog is `/document-changes`'s to write after review, and the last real step is the one that leaves the whole suite green.

## Prefactor first

"Make the change easy, then make the easy change." Where the current shape of the code fights the spec, step `01` is a pure prefactor: no user-visible behaviour, exempt from *demoable* but not from *green*. Any prefactoring goes before the work that depends on it.

## Wide refactors are the exception

A **wide refactor** is one mechanical change — rename a column, retype a shared symbol — whose **blast radius** fans across the codebase, so a single edit breaks thousands of call sites at once and no tracer bullet can land green. Sequence it as **expand–contract** instead of forcing it into a vertical slice:

1. **Expand** — add the new form beside the old, so nothing breaks.
2. **Migrate** — move call sites over in batches sized by blast radius (per package, per directory), one step per batch. Each stays green because the old form still exists.
3. **Contract** — delete the old form once no caller remains.

When even the batches cannot stay green alone, keep the sequence and let them share an integration branch that a final integrate-and-verify step brings together; green is promised only at that step, and each affected step file says so.

## Step file

One file per step at `.agents/steps/<slug>/<NN>-<step-slug>.md`, numbered from `01`, where `<step-slug>` is the step's own title in kebab case.

```markdown
# <NN> — <Step title>

Status: pending
Blocked by: none

## What to build

<the end-to-end behaviour this step makes work, from the user's perspective — not a layer-by-layer implementation list>

## Footprint

Projects: <the projects that must be green when this step finishes>

- `path/to/file` — `SymbolName`, `OtherSymbol`
- `path/to/other/file` — <what lives here that this step touches>

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2
```

`## Outcome` and the flip of `Status:` to `done` belong to the step agent — you write the file as shown above and it takes over from there.

Write behaviour, not code. The one exception is a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape): inline the decision-rich part in `## What to build` and say where it came from. Everything else goes stale between planning and execution.

## The footprint

You walked the codebase to slice these steps. The **footprint** is where that walk lands: the files each step is expected to touch, the symbols inside them that matter, and the projects that must stay green. Write it down and the step agent starts from your map instead of repeating your walk.

Three rules keep it honest:

- **A map, nothing more.** Where the work lands, and there it stops. A footprint that starts explaining *how* has turned into a plan the step agent will follow off a cliff.
- **A guess, not a contract.** Earlier steps move code, so a later step's footprint drifts. The step agent follows the code where the two disagree and records the drift in its `## Outcome`. Write your best guess and let it be corrected.
- **Name every project.** A project you leave off the `Projects:` line is a project nobody checks until the last step. `Projects: none` is for a change no project compiles.
- **Another repository is planned last.** A file there is named by absolute path and `Projects:` names that repository's projects ([ADR-0026](../../docs/adr/0026-implement-never-leaves-the-repository.md)).
