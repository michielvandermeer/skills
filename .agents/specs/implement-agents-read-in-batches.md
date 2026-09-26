# Implement agents read code in fewer, larger batches

Status: ready-for-agent

## Problem Statement

`/implement` runs use up the maintainer's 5-hour and 7-day rate limits fast. Almost all of the cost is cache reads: on every turn, an agent re-reads its whole context.

Step agents (`skills:implementer`) spend much of that on reading code. In 48 hours of transcripts (2026-09-24 to 2026-09-26), reading turns were 48% of implementer spend: 3,787 turns at about 158k tokens of context each. Most reads were small `sed -n` slices of about 1.2k tokens, with about 1.1 reads per turn. At that context size, one turn costs about 100 times the slice it returns. The agent pays for a whole turn to see a few dozen lines.

`skills:oneshot` does the same work for a whole Spec, in one agent, for `/implement-oneshot` and `/implement-yolo`. Nothing in its instructions steers it away from the same habit.

## Solution

Both agents read code in fewer turns. They find the place they need with a search that prints line numbers. Then they read a whole file at once when it is a few hundred lines or less, or one wide range around each place they found in a larger file. Reads that do not depend on each other go out together in one turn, as parallel tool calls.

The agents see the same code as before. Only the number of turns they spend getting it goes down. The estimated saving is about 10–15% of total `/implement` spend.

## User Stories

1. As the maintainer, I want Step agents to use fewer turns to read code, so that an `/implement` run uses less of my rate limit.
2. As the maintainer, I want `/implement` to build the same thing it builds today, so that saving tokens costs no quality.
3. As the maintainer, I want `/implement-oneshot` and `/implement-yolo` to read the same way, so that all three commands get the saving.
4. As a Step agent, I want to find a symbol's line number before I read, so that I know which part of a file to open.
5. As a Step agent, I want to read a short file whole, so that I do not come back for the next slice a turn later.
6. As a Step agent, I want to read one wide range around each hit in a long file, so that I get enough around the hit without reading the whole file.
7. As a Step agent, I want to read several files in one turn when none of the reads depends on another, so that each file does not cost its own turn.
8. As a Step agent, I want to keep reading a file again after I edit it when I need its new content, so that the batching rule never makes me work from stale code.
9. As the maintainer, I want to re-run the same transcript measurement after the change, so that I can see whether reading turns went down.

## Implementation Decisions

- The change is one new working-habit bullet in the "How you work" list of the `skills:implementer` agent file, and the same bullet in the `skills:oneshot` agent file. The two agents do the same kind of work, so they get the same wording.
- The bullet says three things:
  - Find the place first with a search that prints line numbers.
  - Read a whole file when it is a few hundred lines or less. In a larger file, read one wide range around each hit instead of many small slices.
  - Put reads that do not depend on each other in one turn, as parallel tool calls.
- The bullet gives its reason in one clause: every turn re-reads the whole context, so a turn spent on a small slice costs far more than the slice. An agent that knows the reason can apply the rule to cases the bullet does not name.
- The bullet does not ban small reads. A small read is still right when the agent needs exactly those lines, for example to check an edit it just made.
- The bullet names no tool. It describes the behaviour, so it holds on any host and with any file-reading tool.
- The `/implement`, `/implement-oneshot` and `/implement-yolo` skill files do not change. The Driving session already hands paths and does not read code itself.
- No ADR. This is a working habit inside the agents' own "How you work" lists, not a decision about how the skills fit together.
- Both edited agent files match `skills/writing-for-agents/SKILL.md`, and `/writing-for-agents` runs on them after the edit, as this repo's `CLAUDE.md` requires.

## Testing Decisions

- This repo is prose, so there are no automated tests. A good check looks at what agents do, not at the wording.
- The check is the transcript measurement from the Issue this Spec came from, re-run on the `/implement` runs after the change lands. Look at three numbers for `skills:implementer`: reading turns per Step, reads per turn, and the share of implementer spend on reading turns. Before the change they were about 47 reading turns per Step (3,787 over 81 Steps), about 1.1 reads per turn, and 48%.
- The measurement method: take transcripts under `~/.claude/projects/*/` (`<session>.jsonl`, and `<session>/subagents/*.jsonl` with their `.meta.json`). Group assistant messages by message id, and price each one's `usage` at Opus rates. Label each turn by the tools it called.
- The build itself is not measured here. Whether runs still land green is seen in normal use.

## Out of Scope

- The Planner (`skills:planner`), `skills:explorer`, the step 4 fixer, and the `/code-review` reviewers. The measurement covered Step agents, so the change starts there.
- Doing verification in a fresh agent, splitting the fixer, passing only the Outcomes a Step depends on, and running read-only agents on Sonnet. Each is parked as its own Issue in `.agents/issues/implement-token-cost/`.
- Host setup, such as turning off plugins and connectors a repo does not use.

## Further Notes

- The full 48-hour measurement is in the Issue this Spec came from. It was deleted at triage, and git keeps it in commit `5d4d45e`.
- These are not problems, according to the measurement: reading the same file twice (1%), build and test output (about 2%), and screenshots (about 1%). The change does not target them.
