# Idea — Re-measure Step size once Step agents start smaller

## Motivation

In 48 hours of `/implement` transcripts (2026-09-24 to 2026-09-26), Step agents ran 100–175 turns and grew to 350–590k tokens of context. Turns above 200k context took 54% of Step agent spend. The slicing rules say only that a Step "fits in a single fresh context window", which the 1M window stretches a long way.

Slicing Steps smaller would keep each one under about 200k tokens. But each extra Step pays setup: about 34k tokens of fixed baseline, plus the Spec and the Outcomes it reads. And the Planner cannot count tokens before any code exists, so any rule would use a stand-in, such as how many files a Footprint lists.

Two Specs shrink the same number first: `implement-agents-start-smaller` moves the per-Step review and browser pass into a fresh Checker, and `implement-agents-read-in-batches` cuts reading turns. A size rule set now would be tuned to runs that no longer exist.

## Goal

Once both Specs have landed, re-run the transcript measurement from commit `5d4d45e`. Then decide whether the slicing rules need a size target, and what stand-in the Planner could judge.

## Decisions (locked)

- No size target goes into the slicing rules before the re-measurement. A grilling session on 2026-09-26 settled this.

## Out of scope

- The Checker, the split final fixers, and the `Depends on:` line. They landed on 2026-09-26 with the Spec `implement-agents-start-smaller`.

## Open questions

- What share of Step agent spend is still above 200k context after both Specs land?
- Does a smaller Step save more than its extra setup costs?
- Which stand-in can the Planner judge before code exists: files in the Footprint, acceptance criteria, something else?
