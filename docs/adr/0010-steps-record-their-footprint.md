# Steps record their footprint, and it scopes their test run

[STEPS.md](../../skills/implement/STEPS.md) used to tell the planner to "write behaviour, not file paths or code snippets — those go stale between planning and execution." Every Step file therefore described *what* to build and never *where*, so each Step agent found the code again from scratch. We now have the planner write a **Footprint** into every Step file — the files and symbols that Step is expected to touch, plus the projects that must be green when it finishes — and we use that project list to decide how much test suite the Step runs.

Measuring five `/implement` runs across three repos settled it. Step agents did 342 reads before their first edit; 250 of those were source code, and the whole time between dispatch and first edit came to 139 minutes — a quarter of all Step-agent wall clock. The planner had already walked that same code to slice the Spec and then threw the walk away.

## Considered Options

Keeping the rule and accepting the re-discovery was the incumbent, and its reason is sound at the timescale it was written for. It fails at the timescale that actually applies: planning and execution inside one run are minutes apart, not weeks, so the only code that moves under a Step is code an *earlier Step of the same run* moved. That is a bounded, knowable drift rather than open-ended rot.

Recording the footprint only in each Step's `## Outcome`, so the map accrues as the run goes, was the other candidate. It is stale-proof by construction but arrives too late: it covers ground already walked, and says nothing to step `01`. We do both instead — the planner writes the guess, and each Outcome corrects it.

Making the footprint binding was rejected outright. A Step agent that trusts a stale map edits the wrong place and cannot tell. Advisory costs nothing when the map is right and degrades to today's behaviour when it is wrong.

## Consequences

- **The planner gets slower to make Step agents faster.** On the measured runs it costs the planner a second pass over what it already found, against 139 minutes of re-discovery. The trade only holds while the planner stays one agent; fanning explorers out beneath it would spend the saving on nesting.
- **Snippets are still banned, for the original reason.** The staleness argument was never wrong about code — only about paths. A footprint that starts explaining *how* has become a plan.
- **Per-Step green is now narrower than it reads.** A Step confined to one project no longer runs the whole suite. This codifies what was already happening: across 34 Step agents we counted 89 project-scoped test runs and 9 whole-solution ones, every one of the latter an error. The rule now matches the practice, and the whole suite runs where the risk actually is — a footprint spanning projects, or the last Step.
- **A project missing from a `Projects:` line is a project nobody checks** until the last Step. That is the sharp edge of scoping verification by a guess, and it is why the planner is told to name every project it touches.
