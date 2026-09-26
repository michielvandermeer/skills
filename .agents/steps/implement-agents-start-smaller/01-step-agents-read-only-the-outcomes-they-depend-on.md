# 01 — Step agents read only the Outcomes they depend on

Status: pending

## What to build

The Planner writes a `Depends on:` line on every Step file, and a Step agent reads only the Outcomes of the Steps that line names.

- The Step file format in the slicing rules gains a `Depends on:` line directly under `Status:`. It lists the two-digit numbers of the earlier Steps whose Outcomes this Step needs, comma-separated (`Depends on: 02, 05`), or `Depends on: none`. Step `01` always reads `Depends on: none`.
- The slicing rules tell the Planner to fill the line on every Step, from the same code walk it already does for the Footprint: a Step that touches what an earlier Step creates or changes depends on it. A Step may only name lower-numbered Steps.
- The slicing rules say plainly that the line picks which Outcomes a Step reads and never changes run order: Steps still run strictly in `NN` order, and the line is not the `Blocked by:` edge that [ADR-0045](../../../docs/adr/0045-implement-runs-steps-one-at-a-time.md) removed. The existing sentence "a step may rely on every lower-numbered step" stays true of order and is reworded only as far as needed to sit beside the new line.
- The slicing rules gain no Step size target.
- In `/implement` step 3's dispatch list, "read the `## Outcome` of every lower-numbered step file" becomes: read the `## Outcome` of each Step on its Step file's `Depends on:` line, or of every lower-numbered Step when the line is missing. `Depends on: none` means no Outcomes are read. The missing-line fallback keeps Step files from runs planned before this change working.

This Step leaves the Step agent's review, its green, and its `Status: done` as they are; Step 02 changes those.

## Footprint

Projects: none

- `skills/implement/STEPS.md` — the "Steps run strictly in `NN` order" paragraph, the `## Step file` template block, and the paragraph under it that says what the Planner writes
- `skills/implement/SKILL.md` — step 3's dispatch list, the Outcome-reading bullet
- `CONTEXT.md` — already carries the updated **Planner**, **Step agent**, and **Outcome** entries; read for vocabulary, edit only if a term this Step uses is missing
- `docs/adr/0045-implement-runs-steps-one-at-a-time.md` — already carries the `Depends on:` consequence; link it, do not rewrite it

## Acceptance criteria

- [ ] The Step file template in `skills/implement/STEPS.md` shows a `Depends on:` line under `Status:`, and the rules say how the Planner fills it, including `none`
- [ ] `skills/implement/STEPS.md` says the line never changes run order and is not a `Blocked by:` edge, and links ADR-0045
- [ ] `skills/implement/STEPS.md` gains no size target
- [ ] `/implement` step 3 tells each Step agent to read the Outcomes of the Steps on its `Depends on:` line, none for `none`, and every lower-numbered Step's when the line is missing
- [ ] Every edited skill file matches `skills/writing-for-agents/SKILL.md`, and `/writing-for-agents` has been run on them
- [ ] `CHANGELOG.md` is untouched
