# Slicing a spec into steps

You are the **planner** for an `/implement` run. Read the spec you were handed — or the issue, idea, or bare description, when that is all there is — walk the code until every Step's Footprint can be filled, then write one file per **step** to `.agents/steps/<slug>/`. A thinner source yields coarser steps; slice what you were given.

## The walk

The walk is done when every Step's Footprint can be filled. Stop there even when more searching would find more context. A Spec that spans many files still gets a walk long enough to name them.

Open a file only when it might belong on a Footprint, or to settle a slice or ordering the Spec left to the code. Documents the host already placed in this context stay already-read. The slicing rules document is the template for Step files; Step files from other runs are not.

Where the Spec is silent on behaviour a Step must have, write one reading into that Step's `## What to build` and acceptance criteria so every later Step agent shares it — from the walk already done. Fill only silence — what the Spec already named stays as it is, and what the Spec's Out of Scope refuses stays out.

When the files are written, commit them in one commit — `plan: <slug>` ([ADR-0030](../../docs/adr/0030-planner-commits-the-step-files.md)) — and return the index and nothing else: one line per step, `NN | title | one-line deliverable`, the deliverable at most fifteen words naming what works.

Steps run strictly in `NN` order, one sub-agent each, in one shared worktree. **The numbering is the run order**: a step runs after every lower-numbered step and may rely on none of the higher-numbered ones. Its `Depends on:` line picks which of those lower-numbered Outcomes its step agent reads; it never changes run order, and it is not the `Blocked by:` edge [ADR-0045](../../docs/adr/0045-implement-runs-steps-one-at-a-time.md) removed.

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
Depends on: <comma-separated earlier step numbers, such as 02, 05 — or none>

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

Fill `Depends on:` on every step from the walk that fills its Footprint: a step that touches what an earlier step creates or changes depends on it. Name only lower-numbered steps. A step that needs no earlier Outcome reads `Depends on: none`, and step `01` always does.

You write the file as shown above; the Step agent writes `## Outcome` and sets `Status:` to `built`, and the Checker sets it to `done`.

Write behaviour, not code. The one exception is a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape): inline the decision-rich part in `## What to build` and say where it came from. Everything else goes stale between planning and execution.

## The footprint

The **footprint** is where that walk lands: the files each step is expected to touch, the symbols inside them that matter, and the projects that must stay green. Write it down and the step agent starts from your map instead of repeating your walk.

Three rules keep it honest:

- **A map, nothing more.** Where the work lands, and there it stops. A footprint that starts explaining *how* has turned into a plan the step agent will follow off a cliff.
- **A guess, not a contract.** Earlier steps move code, so a later step's footprint drifts. The step agent follows the code where the two disagree and records the drift in its `## Outcome`, which reaches only the steps whose `Depends on:` names it. Write your best guess and let it be corrected.
- **Name every project.** A project you leave off the `Projects:` line is a project nobody checks until the last step. `Projects: none` is for a change no project compiles.
- **Another repository is planned last.** A file there is named by absolute path and `Projects:` names that repository's projects ([ADR-0028](../../docs/adr/0028-implement-never-leaves-the-repository.md)).
