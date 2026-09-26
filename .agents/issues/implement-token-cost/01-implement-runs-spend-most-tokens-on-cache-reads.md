# /implement runs spend most of their tokens re-reading large contexts

Category: enhancement
Status: needs-triage

## Problem

`/implement` runs use up the maintainer's 5-hour and 7-day rate limits fast. A review of 48 hours of
session transcripts (2026-09-24 to 2026-09-26: 40 sessions, 296 transcript files, mostly in
mvdmio-suite) shows where the tokens go. The goal is to use fewer tokens without building less.

Figures are API-price equivalents at Opus rates ($5 input, $25 output, $0.50 cache read per million
tokens). They stand in for how fast the rate limits drain.

| Where | 48 hours | Share |
|---|---|---|
| Total | ~$1,340 | |
| Sub-agents | $1,206 | 90% |
| – `skills:implementer`, 81 Steps | $906 | 68% |
| – fixers ("Fix all review findings") | $122 | 9% |
| – per-Step and final reviews, 93 agents | $100 | 7% |
| – Explore and explorer walks | $81 | 6% |
| Main sessions | $133 | 10% |

One run, `/implement compliance-rest-api-v1` (25 Steps), cost $518 on its own.

## What drives the cost

Output tokens are small. Almost all of the cost is **cache reads**: every turn re-reads the whole
context. No model is pinned, so agents run on Opus with the 1M context window. Implementers run
100–175 turns and grow to 350–590k tokens of context.

- **Turns above 200k context:** 54% of implementer spend.
- **Work after the code is written:** 29% of implementer spend. This is the per-Step `/code-review`,
  the fix loop, and the browser pass, and all of it runs at peak context. Playwright turns average
  288k context.
- **Reading turns:** 48% of implementer spend, over 3,787 turns at about 158k context. Most reads
  are small `sed -n` slices of about 1.2k tokens, with about 1.1 reads per turn. At that context, one
  turn costs about 100 times the slice it returns.
- **The fixed baseline:** about 34k tokens of system prompt, tools and skill listings on every
  sub-agent turn. That is 21% of sub-agent cache reads.
- **Earlier Outcomes in every prompt:** each implementer reads the full Spec (about 11k tokens) and
  the `## Outcome` of every lower-numbered Step (about 20k tokens by Step 20). The cost grows with
  the square of the Step count.
- **One long fixer:** a single fixer ran 285 turns, up to 586k context, and cost $57.

These are **not** problems: duplicate reads of the same file (1%), build and test output (about 2%),
and screenshots (about 1%).

## Possible changes, ranked

Savings are shares of the 48-hour total.

1. **Read in fewer, larger batches** (about 10–15%). In `agents/implementer.md`: find the spot with
   `grep -n`, then read whole files of up to a few hundred lines at once. Put independent reads in
   parallel in one turn instead of one slice per turn. This cuts turns, not what the agent sees.
2. **Do verification in a fresh agent** (about 7–10%). Once the implementer's commit is green, a new
   agent does the browser pass, and maybe the review-and-fix loop. It starts at about 35k context
   with the diff, not at 300–400k.
3. **Split the fixer** (about 4%). One fixer per review axis or per area of code, not one fixer for
   every finding.
4. **Give each Step only the Outcomes it depends on** (about 3%). The Planner writes a
   `Depends on:` line in each Step file, and the driver passes only those Outcomes.
5. **Run reviewers and explore agents on Sonnet** (about 5%, more if the plan counts Sonnet against
   a separate limit). These agents only read, and they cost $181. For the Spec reviewers this goes
   against ADR-0049, which keeps agents bound to a Spec on the session's model.
6. **Trim the fixed baseline** (about 2–3%). Turn off plugins and connectors a repo does not use.
   This is host configuration more than a skill change.
7. **Drop the per-Step Standards review** (about 3%) and let the final review cover it. This loses
   the early catch, so it costs some quality.

Changes 1–4 together should roughly halve what an `/implement` run costs without changing what it
builds. They touch `agents/implementer.md`, `skills/implement/SKILL.md` and `agents/planner.md`.

## Open questions

- Is change 2 a new agent, or does the implementer start a sub-agent for its own verification? What
  does the verify agent receive: the diff, the Step file, the Spec?
- For change 4: does `Depends on:` belong in the Step format (`skills/implement/STEPS.md`)? Can the
  Planner judge dependencies well enough, or should the driver fall back to all Outcomes?
- Should Steps be sliced smaller so each one stays under about 200k context? Smaller Steps also pay
  for more orientation, at about 34k per agent plus Spec and Outcome reads.
- Should any of changes 2, 4 or 5 get an ADR, or amend ADR-0049 and ADR-0045?
- Do `/implement-oneshot` and `/implement-yolo` need the same read and verify changes?

## How this was measured

Transcripts under `~/.claude/projects/*/` (`<session>.jsonl` and `<session>/subagents/*.jsonl` with
their `.meta.json`), files changed in the last 48 hours. Assistant messages were grouped by message
id, and each one's `usage` was priced. Each tool result's cost was estimated as its tokens times the
turns left in that agent, and each turn was labelled by the tools it called. Re-run the same
measurement after a change to compare.
