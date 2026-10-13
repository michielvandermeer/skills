# List-price cost of one /implement run (USD, lower is better)

Measured by `measure.py`: alternating baseline/candidate pairs of `benchmark/run.py` (`claude -p '/implement #394'` on the frozen Spec `ui-bug-394`, `--model sonnet --effort high`, target clone `C:\Users\MichielvanderMeer\work\mvdmio-suite`), judged by `benchmark/compare.py` (verdict first, median and range, invalid runs counted, exact rank-sum test). It reads `claude -p /usage` before every pair and stops at 80% of the week used or 25 points spent.

## Ideas not yet tried

Supplied with the request (from `ref/token-analysis.md`); no profiling Explorer was dispatched, because profiling runs would spend the weekly budget the Attempts need.

- Smaller Steps from the Planner (~15-20 tool calls each, `skills/implement/STEPS.md`) — Implementer context ~125k -> ~70k. Little to gain on ui-bug-394, which is probably one or two Steps.
- Haiku for the Prover and the data-structures pass — mechanical roles; Prover is only ~2% of cost.
- No browser pass for test-only or doc-only Specs — PNG proofs read into context. Not measurable on ui-bug-394 (a UI Spec, and the target's Playwright MCP is off in the benchmark).
- Per-agent cache TTL (5m for short-lived agents) — no host setting known; probably a wash.
- Split `testing.md` / `coding-standards.md` into a core plus topic files — **cannot be tested as asked**: the refs live in `mvdmio-suite/.agents/refs`, the clone is read-only, and each benchmark run starts from a worktree of the Spec's base commit, so a ref edit would not reach the run. Attempt 1 tries the skill-side equivalent: agents read refs by section.

## Hillclimb 2026-10-13

Started from: reduce the list-price cost per /implement run, measured with `benchmark/` against `889e5cd` (base branch `hillclimb-implement-tokens`). Target: 30% cheaper with no quality regression. Minimum Attempts: none fixed; the budget decides. Deadline: none, but the weekly budget (57% used at the start; stop starting runs at 80% or 25 points) ends it.
Baseline: measured as the baseline side of Attempt 1's pairs, not alone first (a separate baseline run costs budget the Attempts need; the alternation is the fairer baseline anyway). Already failing: none known (target build and tests checked by the user before the start).
Spec scope: `ui-bug-394` only (a UI bug with a 56-line landing commit). The result says nothing about larger Specs.
Skipped from the skill: the sensitivity check of MEASURE.md (it would cost a pair of real runs; the first pair stands in for it, and compare.py's spread and rank-sum rules decide) and the profiling Explorer.
Result: (written in step 7)

| # | Idea | Change | Before | After | Tests | Verdict | Note |
|---|------|--------|--------|-------|-------|---------|------|
| 1 | Bundle: Reviewer pinned to Sonnet (final whole-diff review the one Opus), one reviewer carrying both axes, one merged fixer, quiet and bounded build/test output, refs read by section (skill-side stand-in for splitting the refs), Checker at medium effort, data-structures pass at medium effort and skipped for diffs of 120 changed lines or fewer, `/retro` only after a deviation, retry, fixer or Prover failure | `agents/{checker,implementer,prover,reviewer}.md`, `skills/code-review`, `skills/implement` (candidate `88fdc31`) | $3.95 ($3.05-$4.36), 6 valid of 6 runs, 8 subagents (8-9) | $2.42 ($2.29-$3.66), 5 valid of 5 runs, 5 subagents (5-9) | build, tests, Proof held on all valid runs of both sides; `benchmark/test_benchmark.py` OK | kept | Verdict **cheaper**, -39% median, rank-sum p < 0.05, no regressions listed. 6 baseline and 5 candidate runs, alternating (one pair at a time, 5 alternating pairs plus the baseline run of a sixth whose candidate run was cut off while being scored and is not counted). Limiter note: the saving exceeds the reviewer role's share (33%), which is expected here because the bundle touched Checker, reviewers, fixers, data-structures pass and retro. Reviewer cost fell most (-$0.71 per run). Two traits of this Spec: the data-structures skip applies because the landing is 56 lines, and one Step means the final review overlaps the Checker's. The refs were not split (the clone is read-only); only the agents' reading of them changed. Machine shared with nothing else known; alternation spreads any drift. |
