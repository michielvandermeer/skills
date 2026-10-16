# A benchmark run writes nothing outside its checkout

`/implement` run by the `benchmark/` runner is in **benchmark mode**: the runner exports `SKILLS_BENCHMARK=1` and `SKILLS_BENCHMARK_LOG`, and names the first in the session's system prompt. Every write that would leave the local checkout becomes a no-op that appends one line to the log. A benchmark pass runs the same Spec many times on both sides of a skills change, so a real claim, push, comment, or close would repeat against live Issues and branches.

The run's outward writes are the claim in step 1 and the push in steps 4 and 5. The closing reference in the landing commit reaches the Tracker only through a push. No agent file holds a write: the Implementer and the Verifier halt rather than reach outside, and `/code-review`, `/retro`, and `/resolving-merge-conflicts` write nothing outward. The driving session therefore skips the claim and the pushes, and adds one line to every sub-agent prompt.

The skill is not the only guard. The runner also rejects pushes in the worktree, shims `gh` so only reads pass, starts Claude Code with no MCP servers, and denies the write commands as tools. A guard that trips is logged as `BLOCKED`, and the scorer counts it: a run that needed one did not follow benchmark mode.

## Considered Options

- **Reading the env var with a tool call in every run.** Rejected: one call at the driving session's context size, paid by every real run, to serve a mode only the benchmark uses.
- **Guards only, no skill change.** Rejected: the claim would be blocked, so the run's first outward act would fail.
- **A benchmark prompt that differs from `/implement #N`.** Rejected: the run must start the way production does.

## Consequences

- Both skills commits under comparison must contain benchmark mode; the runner refuses a checkout that lacks `SKILLS_BENCHMARK` in `skills/implement/SKILL.md`.
- A new outward write in `/implement` or its agents gets a `bench-log` branch in the same change.
