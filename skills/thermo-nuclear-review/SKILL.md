---
name: thermo-nuclear-review
description: Harsh two-pass review of a branch's changes, correctness and security plus code quality, run in parallel and merged into one verdict. Use for thermo nuclear, thermonuclear, or deep review requests, or an especially harsh audit of a branch or PR diff.
---

# Thermo Nuclear Review

Two fresh subagents review the same diff at once, each against its own rubric, and you merge their findings into one verdict. Both review only code the branch adds or changes.

| Pass | Agent | Looks for |
|---|---|---|
| Correctness | `skills:thermo-nuclear-review-subagent` | bugs, broken features, security holes, devex regressions, feature-flag leaks |
| Code quality | `skills:thermo-nuclear-code-quality-review-subagent` | structural regressions, missed code-judo simplifications, spaghetti branching, files pushed past 1000 lines, leaky boundaries |

## Workflow

1. Fix the scope: the PR or branch the user names, else the current branch against its merge-base with the default branch. The review directory is `/tmp/<project>-thermo/`.
2. Gather `git diff <base>...HEAD` and the full contents of every changed file, through the `Explore` agent when the set is large.
3. Launch both passes in one message with `run_in_background: true`. Give each the same prompt: `### Git / diff output`, `### Changed file contents`, the PR number when there is one, and the path of its detail report in the review directory, `01_correctness.md` or `02_code-quality.md`.
4. When both finish, merge. Dedupe findings across the passes, weight a finding both raised more heavily, and settle a disagreement by reading the code yourself. Done when every finding in either detail report is in the summary, merged with its duplicate, or dropped with a stated reason.
5. Write `summary.md` in the review directory, then reply.

## Report

The review is layered, never one monolithic file. Each pass's detail report carries the depth: measurements, the commands that produced them, verification status, and worked code-judo proposals. `summary.md` reads in one sitting, around 200 lines: the verdict, each finding as a short narrative paragraph naming the file and the evidence, a proposed fix order, and a pointer to the detail report that holds the finding's full evidence.

Your reply, at the bar the `/technical-writing` skill sets, gives the unified verdict, the highest-signal findings, any uncertainty left, and the review directory's path. When the passes' own summaries are already visible to the user, point to them rather than restating them.
