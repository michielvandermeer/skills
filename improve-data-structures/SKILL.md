---
name: improve-data-structures
description: Review recent spike/work for data structures or organizing models that would materially simplify the code.
---

Review the work we have just been doing and look specifically for cleanup opportunities where a better data structure or organizing model would make the code simpler, safer, or easier to extend.

Focus on whether the current code is carrying accidental complexity that could be reduced by something like:
- A state machine instead of scattered booleans, phases, or lifecycle checks.
- A typed object/model instead of loose parameters or repeated shape assumptions.
- A map, registry, lookup table, or discriminated union instead of branching spread across files.
- A reducer or command/event model instead of ad-hoc state mutations
- A small module boundary that gathers repeated behavior, ownership, or invariants.
- A queue, cache, index, graph/tree, or normalized collection where the data access pattern calls for it.

Prefer boring code when the current shape is already clear, local, and unlikely to grow — don't force an abstraction it doesn't need. Be especially skeptical of abstractions that add indirection without removing branches, duplicated rules, invalid states, or lifecycle risk.

Evaluate:
1. What complexity appeared during the spike: repeated conditionals, mirrored state, unclear ownership, invalid intermediate states, awkward data flow, fragile ordering, or duplicated transformations.
2. Whether a data structure or organizing model would encode the real domain more directly.
3. The smallest useful cleanup that would improve the code without changing behavior.
4. The risk: files touched, behavior affected, test impact, and whether this should wait.

If there is a clear, low-risk cleanup that fits the current task scope, make it and run the relevant checks. If the cleanup is larger, speculative, or would distract from the current goal, do not implement it; instead return a concise recommendation with the proposed shape and why it is worth or not worth doing.

Return:
1. Verdict: `implement`, `recommend`, or `skip`.
2. Opportunity: the concrete data structure or organizing model, or `none`.
3. Why: the complexity it removes and the invariants it makes clearer.
4. Scope: the smallest credible change.
5. Validation: tests/checks run or the checks that would be needed