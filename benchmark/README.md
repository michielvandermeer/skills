# Skills benchmark

Measures what a change to these skills costs or saves in an `/implement` run, in tokens and in quality. It runs `/implement` headless on a few frozen Specs, once per run on a baseline skills commit and once on a candidate, then compares them.

**Use it only for a skills change meant to cut cost** (fewer tokens, fewer agents, a cheaper model or effort). It is the check on that claim. A change meant to alter behaviour needs a review, not a benchmark.

## Cost warning

A full pass is **specs x runs x 2** real `/implement` runs. With the four Specs and five runs per side that is 40 runs. `ref/token-analysis.md` puts a run at about $20 to $30 of list-price tokens, so a pass is about **$800 to $1,200** API-equivalent and many hours. Read the dollars as relative weight, not money (see that file's caveats). To spend less, run `--specs` with one or two ids, but a verdict needs enough valid runs. On a single Spec the smallest possible rank-sum p is 0.029 with 4 valid runs per side and 0.1 with 3, so fewer than 4 can never leave "inconclusive". The runner prints this arithmetic and runs nothing until you add `--yes`.

## How to run

You need `claude` (logged in), `git`, `gh` (reads only), `dotnet`, `bun`, and Docker for the integration tests the scorer runs. Python 3 only, standard library; PyYAML is used when present.

1. **Both commits carry benchmark mode.** The baseline is a commit that has [benchmark mode](../docs/adr/0066-a-benchmark-run-writes-nothing-outside-its-checkout.md); the candidate is that commit plus your change, committed locally. The runner refuses a commit without `SKILLS_BENCHMARK` in `skills/implement/SKILL.md`. Nothing is pushed: the runner loads each commit as a plugin with `--plugin-dir`, not the installed plugin.
2. **Write the claim** in the words you would ship, such as "Pinning the Verifier to Haiku cuts the cost of an /implement run by 5% or more with the same quality."
3. **Plan, then run:**
   ```
   python benchmark/run.py --baseline <ref> --candidate <ref> --model sonnet --effort high \
       --claim "<the claim>" --runs 5          # prints the plan
   python benchmark/run.py ... --yes           # runs it
   ```
   `--model` and `--effort` are required and apply to both sides. Run one Spec once first (`--specs ui-bug-394 --runs 1 --yes`) and read `benchmark/runs/<run id>/`: `stream.jsonl` (the init event names the plugin path), `bench.log` (the `NOOP` lines), `transcripts/`, `score.json`.
4. **Compare:** `python benchmark/compare.py <baseline sha> <candidate sha>`. It prints the report and saves it to `benchmark/results/compare-<a>-<b>.md`. The exit code is 2 when the verdict is inconclusive.
5. **Test the tooling** (synthetic transcripts, a fake `claude`, no model): `python benchmark/test_benchmark.py`.

Runs go in order baseline, candidate, baseline, candidate, one at a time, Spec by Spec within each repeat. `benchmark/results/<sha12>.csv` holds one row per run of that skills commit and is rebuilt from `benchmark/runs/` after every run. Commit the CSVs and the report; `runs/` and `work/` are ignored.

## What a run does

Per run: a throwaway worktree of the target repo at the Spec's base, on its own branch (so `/implement` lands there and nowhere else), then `claude -p '/implement #N'` with `--plugin-dir` set to a worktree of the skills commit, `--permission-mode bypassPermissions`, and a fixed `--model` and `--effort`. The scorer then builds and tests the result, and the runner deletes the worktree and every branch.

It writes nothing outside the checkout, in layers:

| Outward write | In the skill | Guard |
|---|---|---|
| Claim of the Issue (step 1, `gh issue edit --add-assignee`) | benchmark mode runs `bench-log` instead | `gh` shim refuses writes; `Bash(gh issue edit *)` denied |
| Push (steps 5 and 6) | benchmark mode runs `bench-log` instead | `pre-push` hook, `pushurl` set to nothing, `Bash(git push *)` denied |
| Comment, close, label, PR, release | no step does them | `gh` shim, tool deny rules |
| Production Postgres and Stripe MCP servers (the target's `.mcp.json`) | no step uses them | `--strict-mcp-config` with an empty config |
| Agents | none of `planner`, `implementer`, `reviewer`, `verifier` holds a write, so none is edited; the skill adds one line to every sub-agent prompt | the same guards |

Every refusal is logged to `bench.log` as `BLOCKED`, and the scorer counts them: a run that tripped a guard did not follow benchmark mode. The `gh` shim lets read commands through (`issue view`, `api` without a write method or fields, `search`) so the run can read its Issue.

## What it measures

- **Tokens and cost** (`metrics.py`): input, cache-write (5-minute and 1-hour), cache-read and output tokens from the main transcript and every subagent transcript, deduplicated by message id and request id, split by model and by role (main session, `planner`, `implementer`, `reviewer`, `verifier`; any other agent counts as `other`), with the subagent count, wall time, largest context and cost at list prices. A model it has no price for is priced as Sonnet and flagged.
- **Quality** (`score.py`): the Spec's build and tests pass (`specs.yaml` lists the commands); the Verifier's last report says `status: passed` (`skipped` when no Verifier ran); the diff size against the real landing commit; tests that assert exact markup (tags, class names, attributes) or exact content text, found by a pattern scan of the added test lines, which is a heuristic and lists its hits in `score.json`; errors, guard trips and failed runs.
- **Did the work happen?** A run is **invalid** when it timed out or claude failed, no commit landed, no subagent ran, no test command appears in the transcript, the Spec's tests ran no tests, or the skills under test were not the plugin that loaded. Invalid runs are counted in the report and left out of every median.

## The verdict

The report states the claim, then one of **cheaper**, **costlier**, **no measurable difference** or **inconclusive**.

- The number is list-price cost per run, pooled over the Specs relative to each Spec's baseline median, with the sum of per-Spec medians as dollars for one pass. Tables give median and range per side for cost, tokens, subagents, wall time and largest context.
- A gap no bigger than the run-to-run spread (the larger range of the two sides) is **no measurable difference**. A bigger gap needs an exact rank-sum p below 0.05, else **inconclusive**.
- **Inconclusive** also when the two sides' build and tests were not scored, the Issue changed between runs (its hash is recorded), or no Spec has a valid run on both sides. Mismatched model or effort is refused with no table.
- The limiter is the role that dominates cost. A saving bigger than that role's share is called out as probably measuring something else.
- Quality regressions are listed under the verdict: build, tests or the Verifier passing less often, more tests asserting markup or text, more invalid runs, more API errors, a median diff size outside 0.67 to 1.5 times the baseline's.

## Mapping to the benchmark checklist

| Checklist | Here |
|---|---|
| Write the claim first | `--claim` is required; the report prints it first |
| Read what the script times | tokens and cost come from transcripts; wall time is reported but is machine-dependent |
| Machine load | sides alternate A,B,A,B; the report says whether they did; `load` is in `meta.json` where the OS gives it |
| 1. Why not double? | the Limiter line names the role and its share |
| 2. Was it tuned? | one `--model`/`--effort` for both sides, the plugin loaded from the checkout under test and verified from the init event, mismatches refused |
| 3. Did it break limits? | the saving is checked against the dominant role's share |
| 4. Did it error? | API errors, tool errors, failed runs, guard trips, build, tests, Verifier, counted per side |
| 5. Does it reproduce? | `--runs 5` alternating, median and range, exact rank-sum test |
| 6. Does it matter? | cost of a whole pass over the Specs, and each role's share |
| 7. Did it even happen? | landed commit, tests that ran, subagents; invalid runs flagged and excluded |
| Report | verdict first, number with unit, runs and range, limiter; inconclusive when 4 or 7 could not be checked or settings differ |

## Known limits

- Built and tested without a real `/implement` session. The first real run decides whether the transcript layout, the `stream-json` init event and `claude -p '/implement #N'` behave as assumed; a run where the skill did not start shows up as invalid (no subagent ran).
- The target Issues are live. A changed Issue body is detected, an added comment is not.
- `tests_ok` is strict: a test that also fails on the base counts against the run, on both sides alike.
- No browser pass: the target's Playwright MCP is off on both sides.
- Your own `~/.claude` settings and other installed plugins are part of the configuration; keep them the same for both sides.
- Paths in a Windows worktree run long; the runner sets `core.longpaths`.

## Files

`specs.yaml` the frozen Specs (base is the landing commit's parent) - `run.py` the runner - `guards.py` the `gh` shim, `pre-push` hook and `bench-log` - `metrics.py` transcript extractor - `score.py` quality scoring - `collect.py` CSV rows - `compare.py` the report - `test_benchmark.py` and `fixtures/` the tests.
