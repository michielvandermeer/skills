# `/doctor` moves documents into the `.agents/` layout

Status: ready-for-agent

## Problem Statement

Keeping a project's agent documents healthy currently takes two commands that behave differently. `/doctor` removes implemented Specs and Ideas and brings every ADR to state the decision in force. It never asks: it makes every change, commits once, and reports. `/migrate-doc-layout` moves documents that sit outside the canonical `.agents/` layout. It shows a plan and waits for approval, and it does not commit. A developer has to know that both exist, run them one after the other, and run `/migrate-doc-layout` first, or `/doctor` never sees a Spec that is still sitting in `.agents/plans/`.

`/migrate-doc-layout` has also fallen behind the layout it enforces:

- It still moves documents into `.agents/refinements/`, which `/refine` no longer writes and no skill reads (ADR-0039). An old Refinement that was never built stays in a folder nobody opens.
- It does not recognise Issues, Decision tickets, or Maps found anywhere except the old `.scratch/` tracker.
- Its `.scratch/` moves miss the `PRD.md` each feature folder held.
- It assumes a single root `docs/adr/`, even in a repo with a `CONTEXT-MAP.md`.
- It describes an ADR as "optionally with Status frontmatter", which contradicts `/doctor`, since `/doctor` strips status lines.

## Solution

`/doctor` takes over everything `/migrate-doc-layout` does, and `/migrate-doc-layout` is deleted. `/doctor` gets a layout pass that runs first. The pass moves every document it can place into its canonical location, without asking, in the same single commit as the rest of `/doctor`'s changes. It lists what it could not place in its report instead of asking about it.

The fold also closes the gaps listed above:

- An old Refinement becomes an Idea. Its demo becomes a Prototype folder.
- Issues, tickets, and Maps found outside `.agents/issues/` move there with their folder.
- The `.scratch/` tracker's `PRD.md` becomes a Spec.
- In a repo with several contexts, an ADR goes to the `docs/adr/` of the context it was found in.

## User Stories

1. As a developer, I want one command that keeps all of my project's agent documents healthy, so that I do not need to know which of two commands to run, or in what order.
2. As a developer, I want `/migrate-doc-layout` removed with no alias left behind, so that the list of skills shows one way to do this.
3. As a developer, I want `/doctor` to move misplaced documents before it checks Specs, Ideas, and ADRs, so that a Spec found in `.agents/plans/` is also removed when it has already been built.
4. As a developer, I want `/doctor` to move documents without asking me first, so that I can start it and walk away.
5. As a developer, I want the moves in the same single commit as `/doctor`'s other changes, so that I can review everything as one diff and undo it in one step.
6. As a developer, I want moves made with `git mv`, so that each file's history follows it.
7. As a developer, I want `/doctor` to classify a document by what it contains, not by its filename or folder, so that a document is placed correctly wherever it was left.
8. As a developer, I want the mechanical moves for known old layouts to run from the source path alone, so that a whole old tree moves without each file being classified.
9. As a developer, I want a document `/doctor` cannot classify left where it is and listed in the report, so that nothing moves on a guess.
10. As a developer, I want a move that would overwrite an existing file left undone and listed in the report, so that no document is lost.
11. As a developer, I want the report to say what moved, what stayed, and why, so that I know what to check in the diff.
12. As a developer, I want every link to a moved file fixed, in the same pass that fixes links to Folded, renamed, and deleted ADRs, so that nothing in the repo points at an old path.
13. As a developer with an old Refinement folder, I want it turned into an Idea at `.agents/ideas/<slug>.md`, so that a briefing nobody built yet sits where `/grill-with-docs` and `/refine` start from.
14. As a developer, I want that Idea made from `complete.md` when there is one, so that the signed-off briefing is what survives.
15. As a developer, I want a Refinement that has only `session.md` turned into an Idea from that file, so that an unfinished Refinement is not lost.
16. As a developer, I want `session.md` dropped when `complete.md` exists, and `complete.html` always dropped, so that I do not keep two copies of one briefing. Git still holds them.
17. As a developer, I want a flat old Refinement file turned straight into an Idea, so that it does not stop at a folder shape nothing reads.
18. As a developer, I want a Refinement's demo moved to `.agents/prototypes/<slug>/`, so that it sits where every other Prototype lives.
19. As a developer, I want the Idea to name that demo folder, so that I can find the demo from the Idea.
20. As a developer, I want the demo deleted when `/doctor` deletes its Idea as already built, so that no Prototype folder is left with nothing pointing at it.
21. As a developer, I want `.agents/refinements/` gone from the list of canonical places, so that `/doctor` never moves anything into it again.
22. As a developer, I want an Issue found outside `.agents/issues/` recognised by its `Category:` and `Status:` lines, so that `/triage` can see it.
23. As a developer, I want a Decision ticket recognised by its `Type:` line and its `## Question` section, so that `/wayfinder` can see it.
24. As a developer, I want a Map recognised as a `map.md` with Destination and Decisions so far, so that `/wayfinder` can pick its effort up again.
25. As a developer, I want an Issue, ticket, or Map moved together with its parent folder into `.agents/issues/<folder>/`, so that an effort's tickets stay together with their Map.
26. As a developer, I want an Issue or ticket found without an effort folder around it listed in the report rather than moved, so that `/doctor` does not invent an effort.
27. As a developer with an old `.scratch/` tracker, I want each feature's `PRD.md` moved to `.agents/specs/<slug>.md`, so that it becomes a Spec and the Spec pass can delete it once built.
28. As a developer with an old `.scratch/` tracker, I want its tickets and Maps moved and the emptied tree removed, as `/migrate-doc-layout` does today, so that nothing reads `.scratch/` any more.
29. As a developer with flat architecture-review files, I want them moved into a folder per review, as today, so that each review's files stay together.
30. As a developer in a repo with a `CONTEXT-MAP.md`, I want an ADR found inside a context's folder moved to that context's `docs/adr/`, so that context decisions stay with their context.
31. As a developer in a repo with a `CONTEXT-MAP.md`, I want an ADR found anywhere else moved to the root `docs/adr/`, so that the rule is predictable.
32. As a developer in a repo with a `CONTEXT-MAP.md`, I want Specs, Ideas, Issues, and every other document moved to the one root `.agents/`, because every skill reads only that root.
33. As a developer, I want a moved ADR to keep its number when that number is free in the target folder, so that links and conversations that name it stay valid.
34. As a developer, I want an ADR that has no number to get the next free number in its target folder, so that it fits the numbering.
35. As a developer, I want an ADR whose number is already taken in the target folder listed in the report rather than moved, so that two ADRs never share a number.
36. As a developer, I want the layout pass to recognise an ADR whether or not it has a status line, so that the ADR pass can then strip the line.
37. As a developer, I want `/doctor` not to hunt for Prototypes by content, so that it never mistakes real app code for a demo.
38. As a developer, I want research notes left alone, because they have no fixed place to move to.
39. As a developer mid-run, I want `/doctor` never to touch `.agents/steps/`, `.agents/worktrees/`, other worktrees, or branches, so that an `/implement` or `/prototype` run in progress is safe.
40. As a developer, I want `/doctor` still to run only when I type it, so that no skill moves my documents on its own.
41. As a developer, I want `/doctor`'s description and README row to say it moves documents too, so that I know it replaces `/migrate-doc-layout`.
42. As a reader of this repo's ADRs, I want every ADR that names `/migrate-doc-layout` to name `/doctor` instead, so that no ADR points at a skill that no longer exists.

## Implementation Decisions

- **`/migrate-doc-layout` is deleted.** Its skill folder goes, and it gets no alias. This follows the `/cleanup-specs` → `/doctor` rename, which also left none.
- **`LEGACY-MOVES.md` moves into the `/doctor` skill folder** as a supporting reference. It is updated as listed below.
- **`/doctor` gains a layout pass that runs before the Spec and Idea pass.** It keeps `disable-model-invocation: true`, its "act on your own judgement" mode, its single commit, and its closing report. It still starts no `/retro`.
  - The pass finds Markdown and near-Markdown (`.html`) documents. It skips `.git/`, `node_modules/`, `vendor/`, build output, and anything already in its canonical place.
  - It also skips `.agents/steps/` and `.agents/worktrees/`, and it works only on the checkout it runs in. It never touches other worktrees or branches.
  - Mechanical moves run from `LEGACY-MOVES.md`. Every other document is classified by content shape.
  - The approval step is removed. A document that matches no shape is **unclassified**. It stays where it is and appears in the report. A move whose destination already exists is a collision, and it is also reported and not made.
  - Moves use `git mv` and create folders as needed.
  - Each moved path joins `/doctor`'s existing link-fixing step, so one grep across the repo covers moves as well as Folded, renamed, and deleted ADRs. The step also searches for the bare filename, as `/migrate-doc-layout`'s step does today, and it includes `CLAUDE.md` and `AGENTS.md`.
- **Canonical locations** the layout pass enforces:
  - Spec (also plan and PRD): `.agents/specs/<slug>.md`
  - Idea: `.agents/ideas/<slug>.md`
  - ADR: `docs/adr/<NNNN>-<slug>.md`, or a context's own `docs/adr/` (see below)
  - Reference (coding standards, contribution guidelines, style guides): `.agents/refs/<slug>.md`
  - Issue, Decision ticket, and Map: `.agents/issues/<folder>/`
  - Architecture review: `.agents/architecture-reviews/<timestamp>/`, holding `report.md` and `report.html`
  - Codebase audit: `.agents/codebase-audits/<timestamp>/report.md`
  - Prototype: `.agents/prototypes/<slug>/`
  - `.agents/refinements/` is not a canonical place any more.
- **Content shapes.** Spec, Idea, Reference, Architecture review, and Codebase audit keep the shapes `/migrate-doc-layout` uses today.
  - **ADR:** the shape in the ADR format reference, with or without a status line. The words "optionally with Status frontmatter" are dropped. The ADR pass strips any status line afterwards.
  - **Refinement:** the legacy `/refine` shape, including the older variants `/migrate-doc-layout` already lists. It is now a source only, and it converts to an Idea (below).
  - **Issue:** a `Category:` line and a `Status:` line near the top.
  - **Decision ticket:** a `Type:` line and a `## Question` section.
  - **Map:** a file named `map.md` with `## Destination` and `## Decisions so far` sections.
  - An Issue, ticket, or Map moves with its whole parent folder, which becomes `.agents/issues/<parent-folder-name>/`. One found without a folder of its own around it, such as a loose file at the repo root, is reported and not moved.
  - Prototypes get no content shape. A Prototype has no marker file and is plain app code or HTML, so a content match would risk moving real code.
- **Refinement to Idea**, applying both to Refinement folders and to Refinement-shaped documents found anywhere:
  - The Idea at `.agents/ideas/<slug>.md` is `complete.md` as it stands. When the folder has no `complete.md`, the Idea is `session.md` as it stands.
  - `session.md` is deleted when `complete.md` exists. `complete.html` is always deleted.
  - A `prototype/` folder inside the Refinement moves to `.agents/prototypes/<slug>/`. The Idea gains one line naming that path.
  - The emptied Refinement folder is removed, and so is `.agents/refinements/` once it is empty.
  - The slug is the Refinement folder's name, or the file's own name for a flat or loose document. An Idea or Prototype folder that already has that slug is a collision.
- **The Spec and Idea pass** is unchanged, except for one addition. When it deletes an Idea as already built and that Idea names a folder under `.agents/prototypes/`, it deletes that folder too, because no document would point at it any more.
- **`LEGACY-MOVES.md` changes:**
  - A flat Refinement goes straight to an Idea. `.agents/refinements/<slug>.md` becomes `.agents/ideas/<slug>.md`, and `.agents/refinements/<slug>.html` is deleted. The rule against fabricating a `session.md` goes, since nothing writes one now.
  - `.agents/refinements/<slug>/` folders follow the Refinement-to-Idea rule above.
  - The `.scratch/` tracker gains one move: `.scratch/<slug>/PRD.md` becomes `.agents/specs/<slug>.md`.
  - The flat architecture-review moves and the other `.scratch/` moves stay as they are.
  - The intro line that says these moves go through "present → confirm" becomes "move, then fix references". A collision is reported, as for classified documents.
- **Multi-context repos** (a root `CONTEXT-MAP.md` exists):
  - A context's folder is the folder holding a `CONTEXT.md` that the map links to. An ADR found inside a context's folder goes to that context's `docs/adr/`. Any other ADR goes to the root `docs/adr/`.
  - A moved ADR keeps its number when the number is free in the target folder. An ADR without a number gets the next free number in that folder, found by scanning it. A number already taken in the target folder is a collision and is reported.
  - Every non-ADR document goes to the root `.agents/`.
- **The report** adds what moved and where, and what stayed and why (unclassified, collision, no effort folder), to what it already lists: Folded, rewritten, deleted, and flagged ADRs.
- **`/doctor`'s description** grows to cover moving documents into the canonical layout.
- **README.** The `migrate-doc-layout` row goes. The `doctor` row's description grows to match. Past `CHANGELOG.md` entries stay as written.
- **ADRs.** ADRs 0002, 0003, 0008, 0017, and 0039 each named `/migrate-doc-layout`. They were rewritten in place in the same commit as this Spec (ADR-0050), and now name `/doctor`. ADR-0039 also now says that `/doctor` turns old Refinements into Ideas. No new ADR.
- **Glossary.** No new term.

## Testing Decisions

- This repo is prose, so there is no automated test. A good check looks only at what a user of the skill sees: the files `/doctor` leaves behind, its one commit, and its report.
- Check by hand, on a throwaway repo that holds one of each case:
  - a Spec in `.agents/plans/`
  - a `CODING_STANDARDS.md` at the root
  - a `.scratch/` tracker with a `PRD.md`, a ticket, and a `map.md`
  - a flat Refinement file
  - a Refinement folder with `complete.md`, `session.md`, `complete.html`, and `prototype/`
  - a Refinement folder with only `session.md`
  - a flat architecture-review pair
  - an unclassifiable Markdown file
  - a move that collides with an existing file
  - a loose Issue at the root
  - an `.agents/steps/` folder, which must stay untouched
  - a `CONTEXT-MAP.md` with an ADR inside one context's folder and one outside every context
- After one `/doctor` run, each case should sit where this Spec says. There should be one commit, no link in the repo should point at an old path, and every report line should match the diff.
- Run `/writing-for-agents` on every skill file this change edits, as `AGENTS.md` requires.

## Out of Scope

- Asking before any move. This was considered and rejected so that `/doctor` stays a command you can start and walk away from.
- Recognising Prototypes outside Refinement folders by their content.
- Removing Steps left behind by a halted `/implement` run, or pruning `prototype/*` and `research/*` branches.
- A fixed place for `/research` notes.
- Two ADRs sharing number 0050 in this repo. That is filed as the Idea `.agents/ideas/duplicate-adr-numbers.md`.
- Running `/doctor` on this repo as part of this change.

## Further Notes

Claude Code runs the installed plugin, not this checkout. `/doctor`'s new layout pass takes effect only after the plugin updates.
