# 03 — Final review sends two fixers and the Oneshot agent stops self-review

Status: done

## What to build

The final review in all three commands splits its one fixer into two that each start fresh, and the Oneshot agent no longer reviews its own work because that final review covers the same changes.

**Two fixers, in all three commands.** In step 4 of `/implement`, and in step 3 ("Review and improve") of `/implement-oneshot` and `/implement-yolo`, the single "fixes every finding, both axes" sub-agent becomes two fixers sent in turn, before the `/improve-data-structures` pass:

1. The **Spec fixer** gets the Spec axis's findings, pasted as the reviewers wrote them.
2. After it, the **Standards fixer** gets the Standards axis's findings the same way, and is told to skip a finding whose code is gone (the Spec fixer may have removed it) and name that finding on its deviations line.

The Spec fixer goes first because a Spec fix can remove code a Standards finding points at. A fixer whose axis reported nothing is skipped, and the Driving session tells the user so. Each fixer is `general-purpose` at the session's own model and effort, gets the same hand-off as today (Spec path or that there is none, the Coding standards, that leftover choices are its to close), keeps the rule that where a finding and the Spec disagree the Spec wins and the finding goes on the deviations line, reports in the same three lines, leaves the projects it touched green, commits its own work, and gets its own one retry; a second failure of either halts the run. The "A schema, migration, or ADR change … goes to the user as a deviations line" rule covers both fixers and the data-structures pass. The opening paragraph of each command that says "the fixer and the data-structures pass" names the two fixers instead. The post-rebase fixer at land is unchanged.

**The Oneshot agent stops self-review.** `agents/oneshot.md` loses its "run `/code-review` on your commits and fix every finding" bullet, and its sub-agent bullet no longer mentions the reviewers `/code-review` starts (it keeps sub-agents for reading a part of the codebase too large to hold). Its browser pass or smoke run stays part of its green. In `/implement-oneshot` step 2 the dispatch-list bullet "`master` as the fixed point for its own `/code-review`" goes; in `/implement-yolo` step 2 the bullet "`<start>` as the fixed point for its own `/code-review`" goes. `<start>` remains the fixed point of the Driving session's own review in `/implement-yolo`.

## Footprint

Projects: none

- `skills/implement/SKILL.md` — opening agent paragraph ("The fixer and the data-structures pass"), step 4's numbered sub-agent list and the paragraph around it
- `skills/implement-oneshot/SKILL.md` — opening agent paragraph, step 2 dispatch list (own `/code-review` fixed-point bullet), step 3's numbered sub-agent list
- `skills/implement-yolo/SKILL.md` — opening agent paragraph, step 2 dispatch list (`<start>` own-review bullet), step 3's numbered sub-agent list
- `agents/oneshot.md` — the sub-agent bullet, the `/code-review` bullet
- `CONTEXT.md` — read for vocabulary; add a term only if this Step coins one the glossary lacks

## Acceptance criteria

- [ ] All three commands' final review sends a Spec fixer, then a Standards fixer, then the data-structures pass, each fixer with only its own axis's findings
- [ ] The Standards fixer is told to skip a finding whose code is gone and name it on its deviations line
- [ ] A fixer whose axis reported nothing is skipped and the user is told; each fixer has its own one retry and a second failure halts
- [ ] `agents/oneshot.md` no longer reviews its own commits, and its browser pass or smoke run is still part of its green
- [ ] `/implement-oneshot` and `/implement-yolo` step 2 no longer hand the Oneshot agent a fixed point for its own review
- [ ] The post-rebase fixer at land is unchanged in `/implement` and `/implement-oneshot`
- [ ] Every edited agent and skill file matches `skills/writing-for-agents/SKILL.md`, and `/writing-for-agents` has been run on them
- [ ] `CHANGELOG.md` is untouched

## Outcome

- `skills/implement/SKILL.md` step 4, and step 3 of `skills/implement-oneshot/SKILL.md` and `skills/implement-yolo/SKILL.md`: the one fixer is now three sub-agents in order: the Spec fixer, the Standards fixer, then the data-structures pass. Each is on its own retry. A new paragraph under the list says why the Spec fixer goes first, keeps the Spec-wins rule for both fixers, and skips a fixer whose axis reported nothing, telling the user. The Standards fixer is told to skip a finding whose code is gone and name it on its deviations line. The schema, migration, or ADR rule now covers all three. Each command's opening paragraph names the two fixers.
- `agents/oneshot.md`: the `/code-review` bullet is gone, and the sub-agent bullet no longer names the reviewers. Its browser pass or smoke run is still in its green, through the dispatch lists of both commands.
- The step 2 dispatch lists in `/implement-oneshot` and `/implement-yolo` no longer give a fixed point for the agent's own review. `<start>` stays the fixed point of `/implement-yolo`'s own review.
- The post-rebase fixer at land is unchanged. Footprint held. `CONTEXT.md` needed no edits, because "fixer" was never a glossary term.
- Review fixes: the fixer names are plain text, not bold, so they coin no glossary term. List item 3 now names the data-structures pass. Kept on purpose: no new ADR, because the Spec's ADR list does not ask for one. The fixer text is also still repeated in all three commands, because the Spec puts the change in each of them and each already had its own copy of that step.
