# Subsystem review brief

Your assignment names the subsystem's ID, name, ownership boundary, key files, interfaces, call sites, and tests.

Inspect only. Return findings.

Review the assigned subsystem for at most two **material** simplifications in its data structures, state representation, or organizing model.

Inspect its implementation, public interfaces, major call sites, and existing tests. Stay inside the assigned ownership boundary. You may name a cross-subsystem concern; leave it unsolved.

Look for:

- scattered booleans or nullable fields that permit invalid combinations and should become a state machine or discriminated union
- repeated assumptions about object shape that need a shared typed model
- duplicated branching that a small map, registry, reducer, or command model would remove
- unclear state or behavior ownership that a small module boundary would clarify
- repeated scans, transformations, or lookups where a more appropriate collection or index would materially simplify behavior
- lifecycle, concurrency, or async states whose representation permits stale or contradictory state

Prefer boring local code when it is already clear. Recommend only a change that removes invalid states, duplicated rules, unclear ownership, or lifecycle risk — not a restyle, a hypothetical extension point, a smaller line count, or the same branches behind a new type.

Return at most two opportunities. If nothing clearly meets the bar, return `skip`.

For every recommendation provide:

- **Verdict:** `recommend` or `skip`
- **Evidence:** exact file and line references
- **Current complexity or invalid states**
- **Proposed representation** and why it is simpler
- **Smallest credible implementation scope**, including affected files and interfaces
- **Regression risks and migration concerns**
- **Existing and additional validation required**
- **Confidence:** `high`, `medium`, or `low`
