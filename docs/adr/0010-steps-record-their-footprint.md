# Steps record their footprint, and it scopes their test run

The Planner writes a **Footprint** into every Step file: the files and symbols that Step is expected to touch, plus the projects that must be green when it finishes. That project list decides how much of the test suite the Step runs. The Footprint is advisory. Each Step's Outcome corrects it.

Planning and execution inside one run are minutes apart, not weeks, so the only code that moves under a Step is code an earlier Step of the same run moved. Measuring five `/implement` runs across three repos showed Step agents doing 342 reads before their first edit, 250 of them source code, and 139 minutes between dispatch and first edit — a quarter of Step-agent wall clock — re-walking code the Planner had already seen.

## Considered Options

Leaving the Footprint unwritten, so each Step agent finds the code again, fails at the timescale that applies: the drift is bounded and knowable, not open-ended rot.

Recording the footprint only in each Step's `## Outcome`, so the map accrues as the run goes, arrives too late. It covers ground already walked and says nothing to step `01`. The Planner writes the guess, and each Outcome corrects it.

Making the footprint binding was rejected. A Step agent that trusts a stale map edits the wrong place and cannot tell. Advisory costs nothing when the map is right and degrades to finding the code again when it is wrong.

Widening a Step to the whole suite whenever its footprint named more than one project was tried and dropped. A feature's footprint names several projects almost always, so the trigger would make every Step run the whole suite.

## Consequences

- The Planner spends a second pass over what it already found, against the re-discovery that pass removes. The trade holds while the Planner stays one agent.
- The walk ends when every Footprint can be filled. Reading neighbouring features, tests that will not appear on any Footprint, or documents the host already placed in context is not that pass.
- Snippets are banned from the Footprint. A footprint that starts explaining *how* has become a plan. A Step's `## What to build` may inline one snippet that encodes a decision more precisely than prose can — a state machine, reducer, schema, or type shape — and names where it came from.
- A Step runs the projects on its `Projects:` line and no more. Only the last Step runs the whole suite.
- A project missing from a `Projects:` line is a project nobody checks until the last Step. The Planner names every project the Step touches.
