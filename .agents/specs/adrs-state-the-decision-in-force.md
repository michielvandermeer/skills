# ADRs state the decision in force, and `/doctor` cleans up the rest

Status: ready-for-agent

## Problem Statement

Projects that use these skills collect ADRs that describe how things were a month ago. When a decision changes, the skills write a new ADR on top of the old one and mark the old one superseded, or partly superseded. The old ADR stays in `docs/adr/`. To learn how something works today, a reader has to walk a chain. For example, how a `/wayfinder` Map ends is spread across ADR-0011, ADR-0047, and ADR-0048. Even ADRs that nothing replaced tell history: 37 of this repo's 49 ADRs contain lines like "used to" or "ADR-0047 had…".

What people want from an ADR is why things are the way they are now, not how they got there. Git already keeps the history. Stale ADRs also cost every session that reads them: `/grilling` reads every ADR at the start of every session, and other skills read the ADRs "in the area" with no way to tell a replaced ADR from one in force.

## Solution

An **ADR** states a decision in force and the reason it holds, as things stand today. When a session changes a decision, it rewrites that ADR in place instead of adding a new one. When a decision is reversed with nothing in its place, its ADR is deleted.

For ADRs that already exist, `/cleanup-specs` is renamed to `/doctor`. It still removes implemented Specs and Ideas as it does today. It also brings every ADR to the new shape: it **Folds** each chain (merges the ADRs that record one decision at different times into one), rewrites ADRs that tell history, and fixes every link. It makes all its changes in one commit and reports what it did, without asking first.

The bar for writing an ADR does not change.

## User Stories

1. As a developer, I want each ADR to state the decision as it stands today, so that I can learn why things are the way they are without reading a chain of older ADRs.
2. As a developer, I want an ADR to carry no history, so that I do not have to separate what holds now from what used to hold.
3. As a developer, I want git to be the record of how a decision changed, so that the history is still there when I need it.
4. As a developer, I want a session that changes a decision to rewrite that decision's ADR in place, so that no new chain starts.
5. As a developer, I want a rewritten ADR to keep its number, so that links and conversations that name it stay valid.
6. As a developer, I want a rewritten ADR's file renamed when its title changes, so that the filename matches what the ADR says.
7. As a developer, I want every link to a renamed ADR updated in the same change, so that no link breaks.
8. As a developer, I want the ADR of a reversed decision with no replacement deleted, so that `docs/adr/` never holds a rule nobody follows.
9. As a developer, I want every link to a deleted ADR removed, so that no text points at a file that is gone.
10. As a developer, I want numbers never reused, so that an old number in git history or a commit message never means two decisions.
11. As a developer, I want an option that was once chosen and later dropped to stay only as a rejected option with its reason, so that nobody proposes it again without knowing why it failed.
12. As a developer, I want a dropped option left out when nobody is likely to propose it again, so that ADRs stay short.
13. As a developer, I want any ADR in `docs/adr/` to be in force, so that I never need to check a status line.
14. As a developer, I want the rewrite to happen at Spec time, in the same commit as the Spec, so that sessions planning the next change see the planned decision.
15. As a developer, I want the three tests for writing an ADR left as they are, so that the skills keep recording the decisions they record today.
16. As a developer, I want `/cleanup-specs` renamed to `/doctor`, so that one command keeps all of my project's decision documents healthy.
17. As a developer, I want `/doctor` to remove implemented Specs and Ideas exactly as `/cleanup-specs` does today, so that I lose nothing by the rename.
18. As a developer, I want `/doctor` to Fold each chain of ADRs about one decision into a single ADR, so that my existing ADRs match the new shape.
19. As a developer, I want a Folded ADR to keep the newest number in its chain, so that the links skills already use still point at it.
20. As a developer, I want `/doctor` to Fold only the parts of ADRs that overlap, so that an ADR keeps the parts no newer ADR replaced.
21. As a developer, I want `/doctor` to find replacements stated only in a newer ADR's body, so that a replacement nobody marked in a status line is still Folded.
22. As a developer, I want `/doctor` to rewrite every ADR that tells history, even when nothing replaced it, so that "used to" lines disappear everywhere.
23. As a developer, I want `/doctor` to keep my project's own ADR section layout, such as Context / Decision / Consequences, so that it changes what my ADRs say and not how they are laid out.
24. As a developer, I want `/doctor` to update links to Folded, renamed, or deleted ADRs across the whole repo, so that skills, READMEs, and code comments still point at the right ADR.
25. As a developer, I want `/doctor` to report an ADR the code contradicts, when no newer ADR explains why, and leave it alone, so that a bug in the code is not hidden by rewriting the rule it breaks.
26. As a developer, I want that same report to catch an ADR whose Spec was dropped, so that a decision that was never built does not stay in force.
27. As a developer in a repo with a `CONTEXT-MAP.md`, I want `/doctor` to cover every `docs/adr/` folder the map lists, so that context-specific ADRs are cleaned up too.
28. As a developer, I want `/doctor` to make all its changes, Specs and Ideas included, in one commit, so that I can review them as one diff and undo them in one step.
29. As a developer, I want `/doctor` to report what it Folded, rewrote, deleted, and flagged, so that I know what to look at in the diff.
30. As a developer, I want `/doctor` to act without asking first, so that a run on dozens of ADRs does not start with a long list to approve.
31. As a developer, I want `/doctor` to run only when I type it, so that no skill rewrites my ADRs on its own.
32. As a developer, I want `/migrate-doc-layout` to keep recognising ADRs that carry Status frontmatter, so that it can still find another project's ADRs as they are.

## Implementation Decisions

- **`/domain-modeling` and its ADR format reference.** The ADR rules change:
  - An ADR states the decision in force and why it holds. It tells no history.
  - A session that changes a decision an ADR records rewrites that ADR in place, at Spec time. It keeps the number, renames the file when the title changes, and updates every link.
  - A decision reversed with nothing in its place loses its ADR, and every link to it is removed.
  - Numbers are never reused, and deleted or Folded ADRs leave gaps.
  - A dropped option appears only as a rejected option with its reason, and only when someone might propose it again.
  - The Status section of the format reference is removed.
  - The three tests for offering an ADR stay word for word.
- **ADR-writing skills.** `/refine`, `/prototype`, and `/grill-with-docs` already defer to `/domain-modeling` for ADRs. None of their lines assumes an ADR is only ever created, so they need no change.
- **`/doctor`** replaces `/cleanup-specs`. The skill folder and its `name:` change. It keeps `disable-model-invocation: true`. The old name gets no alias.
  - Its description drops "Plan", because the skill has no Plans path, and adds ADRs.
  - The Spec and Idea cleanup stays as it is, including removing `Blocked by:` lines that name a removed Spec, and checking status in the codebase rather than trusting the document.
  - For ADRs, it reads every ADR in each `docs/adr/` folder: the root one, plus every folder a `CONTEXT-MAP.md` lists. It finds chains from `status:` lines and from newer ADR bodies that say they replace part of an older one.
  - It Folds each chain into the newest ADR's number, merging only the overlapping parts. It deletes the older files once nothing of theirs remains.
  - It rewrites every ADR whose text tells history so it states the decision as it stands. It keeps each project's section layout.
  - It updates every link across the repo to a Folded, renamed, or deleted ADR.
  - When the code contradicts an ADR and no newer ADR explains why, it lists the mismatch and changes nothing in that ADR.
  - It commits every change, Specs and Ideas included, in one commit, and ends with a report of what it Folded, rewrote, deleted, and flagged.
- **README.** The `cleanup-specs` row becomes `doctor`, with the new description. Past `CHANGELOG.md` entries stay as written.
- **`/migrate-doc-layout`** is unchanged. Its ADR recognition line still lists optional Status frontmatter, even though the format reference no longer has it, because it reads other projects' ADRs as they are.
- **Glossary.** `CONTEXT.md` already defines **ADR** and **Fold** (written in the session that produced this Spec).
- **ADR.** [ADR-0050](../../docs/adr/0050-an-adr-states-the-decision-in-force.md) records this decision.

## Testing Decisions

- This repo is prose, so there is no automated test. A good check looks only at what a user of the skill sees: the files `/doctor` leaves behind, its commit, and its report.
- The real test is the first `/doctor` run on this repo after the plugin updates. The 49 ADRs here hold every kind of chain: wholly replaced, partly replaced, replaced only in a newer body (ADR-0039 over part of ADR-0009, which has no `status:` line), a three-ADR chain (0011 → 0047 → 0048), and ADRs that tell history with nothing replacing them.
- After that run, a reader should find no `status:` lines, no "used to" narration, and no broken ADR links anywhere in the repo. Each report item should match a change in the single commit.
- Run `/writing-for-agents` on every skill file this change edits, as `AGENTS.md` requires.

## Out of Scope

- Raising the bar for writing an ADR. The three tests stay.
- Cleaning up this repo's own ADRs in this change. That happens when `/doctor` is first run here after the plugin updates.
- Rewriting ADRs when their Spec lands instead of at Spec time.
- Asking before `/doctor` changes anything.
- Glossary entries in `CONTEXT.md` and Changelog history, which `/doctor` does not touch.
- Reshaping another project's ADRs into this repo's ADR format.

## Further Notes

Claude Code runs the installed plugin, not this checkout. The new rules and `/doctor` take effect only after the plugin updates.
