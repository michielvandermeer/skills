# Bound the implement Planner walk

Status: ready-for-agent

## Problem Statement

When you type `/implement`, you wait on the Planner before any Step starts. On fourteen Grok runs from 12–13 September 2026, that wait was two to five minutes for a one-Step spec and nine to thirteen minutes for a two-Step spec. One Planner spent thirteen minutes, wrote no Step files, and returned a long design note instead of the index. The Driving session then tried to write the files itself.

The Planner already has a job: walk the code, write a Footprint on each Step, commit the files, return the index. It has no rule for when the walk is done. It keeps opening tests, neighbouring features, and documents the host already put in its context. Later rounds then think over everything already read, so each extra read makes the next one slower.

[ADR-0010](../../docs/adr/0010-steps-record-their-footprint.md) accepted a slower Planner as the cost of writing the Footprint down. It paid for a second pass over what the Planner already found. It did not ask the Planner to keep reading past the point where every Footprint can be filled.

## Solution

The Planner's walk ends when it can write every Step file, including each Footprint and each `Blocked by` line. It then writes those files, commits them once, and returns only the index.

A file is opened only if it might belong on a Footprint, or to settle a slice or blocker the Spec left to the code. Documents already in the Planner's context are not opened again. Step files from other runs are not a template.

The Driving session treats a missing or empty steps directory, or a reply that is not the index, as a failed Planner and halts. It does not dispatch a second agent to write the files.

The Footprint stays. The Planner still fills silence the Spec left. Independent Ready Steps still run together. The Planner still uses the session's own model and effort.

## User Stories

1. As a developer, I want the Planner to finish in a few minutes on a small Spec, so that `/implement` starts building soon after I type it.

2. As a developer, I want a two-Step Spec to plan in minutes rather than ten or more, so that a medium change does not stall on reading.

3. As a developer, I want the Planner to stop once every Footprint can be filled, so that extra reading does not make later rounds slower.

4. As a developer, I want each Step to still carry a Footprint, so that the Step agent starts from the Planner's map.

5. As a developer, I want a Footprint that still names files, symbols, and projects, so that Green is still scoped per Step.

6. As a developer, I want the last Step to still wait on every other Step and leave the whole suite Green, so that landing is still one Green run.

7. As a developer, I want overlapping Footprints to remain a blocking edge, so that two editors do not touch the same files at once.

8. As a developer, I want a chain of Steps to still work, so that a Spec that must run in order still does.

9. As a developer, I want a thin source to still yield coarse Steps, so that a bug note does not become a ten-Step plan.

10. As a developer, I want a small Spec to still yield one Step, so that the bound does not force extra slices.

11. As a developer, I want step `01` to remain a prefactor when the current shape fights the Spec, so that later Steps still land Green.

12. As a developer, I want a Wide refactor to stay expand–contract, so that a mechanical rename is not forced into a vertical slice.

13. As a developer, I want silence in the Spec to still be filled in `What to build`, so that every Step agent shares one reading.

14. As a developer, I want that fill to use the walk already done, so that filling silence is not a reason to keep reading.

15. As a developer, I want the Planner to skip documents the host already put in its context, so that it does not re-read rules it already holds.

16. As a developer, I want the Planner not to open historical Step files from other runs, so that the slicing rules stay the only template.

17. As a developer, I want the Planner not to read neighbouring features that will not appear on any Footprint, so that the walk stays on this Spec.

18. As a developer, I want a test file opened only when it belongs on a Footprint or names a project that must be Green, so that tests are not studied as a second codebase.

19. As a developer, I want the Planner to write every Step file before it returns, so that a retry cannot delete a plan that was never on disk.

20. As a developer, I want those files committed in one `plan:` commit, so that resume still finds them.

21. As a developer, I want the Planner's whole reply to be the index, so that the Driving session is not handed a long write-up.

22. As a developer, I want a reply that is not the index to halt the run, so that a long write-up cannot be mistaken for a plan.

23. As a developer, I want an empty or missing steps directory to halt the run, so that the Driving session does not invent the files.

24. As a developer, I want the Driving session not to dispatch a writer after a failed Planner, so that a bad plan does not cost a second wait.

25. As a developer, I want a failed Planner to leave the worktree and the Spec in place, so that I can re-invoke `/implement` and try again.

26. As a developer, I want Ready Steps to still run together after a successful plan, so that bounding the walk does not serialize the run.

27. As a developer, I want a Step agent to still treat the Footprint as a guess, so that drifted paths do not become a contract.

28. As a developer, I want a project missing from `Projects:` to remain a miss until the last Step, so that the Planner still names every project it touches.

29. As a developer, I want work in another repository to stay planned last, so that the bound does not change where that work sits.

30. As a developer, I want `/implement-oneshot` unchanged, so that I can still skip the Planner when I want one agent to build the whole Spec.

31. As a maintainer, I want ADR-0010 to say the paid slowness is recording the Footprint, so that a later edit does not restore an unbounded walk as "what 0010 asked for".

32. As a maintainer, I want the Planner glossary entry to name the bound, so that other skills describe the same stop.

33. As a developer, I want the Planner to keep using this session's model and effort, so that this change does not quietly downgrade judgement the pinning ADR left at session settings.

34. As a developer, I want one Planner agent, not a fan of Explorers, so that nesting does not spend the time this bound saves.

35. As a developer, I want the index line to still name title, blockers, and a short deliverable, so that the Driving session can dispatch without opening Step bodies.

36. As a developer, I want a Planner that already has enough to write the files to stop even if it could keep searching, so that extra context is not treated as progress.

37. As a developer, I want a large Spec that truly spans many files to still get a long enough walk, so that the bound does not starve a Footprint that needs those files.

38. As a developer waiting on `/implement`, I want planning to end in building, not in a second agent that writes the files, so that I can tell a stuck run from a live one.

## Implementation Decisions

- The planner slicing rules gain a completion criterion for the walk: the walk is done when every Step file can be written, including Footprint and `Blocked by`. Reading after that is not the walk.

- A file is opened only if it might belong on a Footprint, or to settle a slice or blocker the Spec left to the code. That is the whole permission to read.

- Documents the host already placed in the Planner's context are not opened again. Historical Step files from other runs are not opened as a template. The slicing rules document is the template.

- Filling Spec silence stays in `What to build` and uses the walk already done. It is not a second explore.

- The Footprint stays advisory and complete: files, symbols, every project. [ADR-0010](../../docs/adr/0010-steps-record-their-footprint.md) is unchanged on that. An amendment records that the paid slowness is writing the Footprint down, not an unbounded extra walk.

- Write every Step file, commit once, return only the index. That order stays. The index line still names title, blockers, and a short deliverable. A reply that is not the index is a failed Planner, the same shape as a Step agent that does not return the three-line report.

- The implement skill's plan step already halts when the Planner fails or returns no Steps. It now also halts when the steps directory is missing or empty, or when the reply is not the index. It does not dispatch another agent to write or commit the files. The existing fallback that commits an already-written dirty directory stays. That covers a Planner that wrote the files and forgot the commit.

- Slicing rules other than the walk bound stay as they are: tracer bullets, prefactor first, Wide refactor as expand-contract, overlapping Footprints as a blocking edge, the last Step blocked by every other Step, a thinner source yielding coarser Steps, another repository planned last.

- The Planner remains one agent at the Driving session's model and effort. No Explorer fan-out. No new Planner agent type. No change to Spec-bound dispatch.

- The Planner glossary entry names the bound. No new term is coined.

## Testing Decisions

A good check is external: after this change, a Planner run on a Spec like the ones measured in this triage returns the index, leaves committed Step files on disk, and does not open a pile of files that appear on no Footprint.

The seam is the session trace, the same one this triage used. Count wall time, the number of reading rounds, and reads whose path is not the Spec, not the slicing rules, not CONTEXT or an ADR in the area, and not a path that lands on some Step's Footprint. The last class is the miss.

There is no automated harness for skill prose. Do not add one. The prior art is the five-run count that settled ADR-0010, and the fourteen-run count in this triage.

Do not assert a minute cap. Hosts and models differ. Assert the stop and the artifacts.

A one-Step Spec still yields one Step file. A Planner that returns a design note and no files is a fail, even if the note is accurate.

## Out of Scope

- Pinning the Planner's model or effort. That contradicts [ADR-0007](../../docs/adr/0007-pinned-subagent-model-tiers.md) as written and is parked as `.agents/issues/implement/01-planner-session-effort.md`.

- Fanning Explorers under the Planner. ADR-0010 rejected that.

- Skipping the Planner. `/implement-oneshot` already does that.

- The minute or two the Driving session spends opening the run worktree before the Planner starts.

- Host hangs where a Planner is dispatched and makes zero tool calls.

- Changing what a Footprint contains, or how Step agents treat it.

- Speeding Step agents, review, or land.

- A new Planner agent type or a host-specific `plan` dispatch.

## Further Notes

Measured on Grok, 12–13 September 2026, fourteen completed Planner runs in `mvdmio-suite`, all `grok-4.6` or `grok-4.5` at high effort, one turn each.

Typical one-Step plans: two to five minutes, ten to twelve model rounds, about twenty file reads, 300–400k input tokens.

Slow two-Step plans: nine to thirteen minutes, twenty to twenty-three rounds, 87–115 tools, 1.3–1.6M input tokens. Mean round time rose from about 13s to 25–35s as the window grew. Last rounds on the slowest runs took one to three minutes.

The thirteen-minute Audit Log Planner returned a 154-line design note, wrote no files, and triggered a 6.4-minute "write the step files" follow-up that was then cancelled.

One Claude `/implement` in the same window planned in about six minutes with 47 tools.

Fast Planners already stop near the bound this Spec writes down. Slow ones do not. The slicing rules currently say "explore the codebase" with no stop.
