# `/doctor` brings ADRs in line with the code

Status: ready-for-agent

## Problem Statement

`/doctor` is a skill you type to tidy a repository's agent documents. One of its jobs is to make every ADR state the decision in force. When the code disagrees with an ADR, though, `/doctor` always assumes the code is wrong. It lists the mismatch in its report and leaves the ADR as written. It does the same with an ADR whose Spec was dropped before it was built.

In practice most of these mismatches are decisions that moved on: a migration dropped a field the ADR still lists, or someone added streaming to a client that the ADR says does not stream. A run in one app repository flagged eight such ADRs and changed none of them. The documentation stays stale, and every later session reads decisions that no longer hold.

`/doctor` also has no method for finding these mismatches. It catches them only when it happens to notice one.

## Solution

`/doctor` checks every ADR against the code, using read-only explorer sub-agents. For each mismatch it decides which side is right:

- When there is evidence that someone chose the new behaviour on purpose, the decision has moved on. The evidence is a migration, a commit whose message states the change, or a newer Spec or ADR that covers it. `/doctor` rewrites the ADR to state what the code does. It deletes the ADR when nothing of the decision is left.
- When there is no such evidence, the ADR wins. `/doctor` leaves it as written and reports the mismatch as a bug in the code, with its evidence and a suggestion to take it to `/triage`.

An ADR whose Spec was dropped is judged against the code the same way. `/doctor` deletes it when nothing was built. When part was built, it rewrites the ADR to describe that part.

`/doctor` still makes one commit, never asks you anything, and never edits application code.

## User Stories

1. As a developer who runs `/doctor`, I want every ADR checked against the code, so that stale ADRs are found even when nobody suspects them.
2. As a developer, I want `/doctor` to rewrite an ADR whose decision moved on, so that the ADR says what the code does today.
3. As a developer, I want `/doctor` to count only real evidence as a decision moving on — a migration, a commit that states the change, or a newer Spec or ADR — so that it does not guess.
4. As a developer, I want `/doctor` to make the smallest edit that makes a partly outdated ADR true, so that the parts that still hold keep their wording.
5. As a developer, I want `/doctor` to delete an ADR when the code has no trace left of its decision, and remove every link to it, so that a reversed decision stops reading as one in force.
6. As a developer, I want a rewritten ADR to keep a reason, taken from the commit that changed the code, so that the ADR still says why.
7. As a developer, I want a rewritten ADR to say plainly that the reason was not recorded when git gives none, so that no reason is invented.
8. As a developer, I want `/doctor` to leave an ADR as written when the code breaks it with no sign anyone chose to, so that a real bug is never recorded as a decision.
9. As a developer, I want leftovers — old code the decision already removed but that is still there — treated as bugs, so that dead code does not rewrite the rule that removed it.
10. As a developer, I want each bug listed in the report with its evidence and a suggestion to take it to `/triage`, so that I have what I need to act on it.
11. As a developer, I want `/doctor` to file no Issue or Idea for a bug, so that `/triage` stays the only place Issues are born.
12. As a developer, I want `/doctor` never to edit application code, so that a documentation tidy-up never changes behaviour.
13. As a developer, I want an ADR whose Spec was dropped deleted when nothing was built, so that a plan nobody built does not read as a decision.
14. As a developer, I want an ADR whose Spec was dropped rewritten to describe the part that was built, when part was, so that the built part keeps its record.
15. As a developer, I want the report to list every ADR changed or deleted because of the code, with the evidence used, so that I know what to check in the diff.
16. As a developer, I want these changes inside `/doctor`'s single commit, so that I can review or revert the whole tidy-up at once.
17. As a developer, I want `/doctor` to keep running without asking me anything, so that a larger ADR pass adds no pauses.
18. As a developer in a repository with several contexts, I want every context's ADRs checked against that context's code, so that no context is skipped.
19. As a developer whose repository has no ADRs, I want the check to cost nothing, so that `/doctor` stays quick there.
20. As a maintainer of this repository, I want ADR-0050 to state the new rule and list "report and leave the ADR alone" as a rejected option, so that nobody proposes it again without its reason.

## Implementation Decisions

- The change lives in the ADRs pass of the `/doctor` skill. Its step that flags contradictions becomes a step that checks and aligns. The rule that a contradiction is always a bug in the code, which forbids rewriting the ADR, is removed.
- The dropped-Spec rule changes the same way. `/doctor` still finds an ADR's Spec with `git log --follow` as today. It no longer only reports the ADR; it judges the ADR against the code.
- `/doctor` dispatches read-only explorer sub-agents (`skills:explorer`) to compare ADRs with the code. Each explorer gets a batch of ADRs and returns, for each claim that the code contradicts, the evidence on both sides, including any migration, commit, Spec, or ADR that shows a deliberate change. `/doctor` carries the reports and makes the judgement itself. This follows the precedent in `/grilling` and `/codebase-audit`. How the ADRs are batched is up to the implementer. In a repository with several contexts, an ADR is checked against its own context's code. When a repository has no ADRs, no explorer is dispatched.
- The judgement rule, in `/doctor`'s words: a mismatch is a decision that moved on when a migration, a commit whose message states the change, or a newer Spec or ADR covers it. Otherwise the ADR wins, and the mismatch is a bug in the code. Leftover code the decision already removed counts as a bug.
- The alignment follows `ADR-FORMAT.md`: the ADR is rewritten in place under the same number, the file is renamed if the title changes, and every link is updated. When nothing of the decision is left, the ADR is deleted, every link to it is removed, and its number stays unused.
- A rewritten ADR carries a reason, taken from the commit that changed the code. When git records no reason, the ADR states the decision and says the reason was not recorded.
- The done condition of the ADRs pass becomes: every ADR you keep has no `status:` line, states the decision in force, and agrees with the code — or disagrees only where the code has a bug that the report names.
- The report's ADR part lists what was folded, rewritten, and deleted, now including each ADR changed because of the code with its evidence. It also lists the bugs found, each with its evidence and a suggestion to take it to `/triage`. The report still runs `/plain-language`.
- `/doctor` never edits application code, and it files no Issue or Idea for a bug.
- ADR-0050 was already rewritten in place in this Spec's commit, as ADR-0050 itself requires. It now states the alignment rule. It lists "report and leave the ADR alone", "the code always wins", and "ask the user about each mismatch" as rejected options.
- The skill's frontmatter description and the README line already say `/doctor` "brings every ADR to state the decision in force". That stays true and needs no change.
- The skill file edit must match `/writing-for-agents`, and `/writing-for-agents` runs on it afterwards, as `AGENTS.md` requires.

## Testing Decisions

- This repository has no automated tests. Every change is prose in a skill file.
- A good check looks at what `/doctor` would do from the outside. Read the edited ADRs pass and walk the eight mismatches from the motivating run through it:
  - A dropped field backed by a migration, and a streaming client added on purpose, are rewritten.
  - A seventh register the code allows gets the smallest edit.
  - An error message shown to a user against an ADR that forbids it is reported as a bug, and the ADR is left alone.
  - Leftover attributes and unused columns are reported as bugs.
- Grep the `/doctor` skill for any remaining line that says a contradiction is always a code bug, or that a dropped-Spec ADR is only reported. None should remain.
- Read ADR-0050 next to the edited skill. They must not contradict each other.

## Out of Scope

- `CONTEXT.md`, the README, `AGENTS.md`, and any document other than ADRs. `/doctor` does not check those against the code.
- Fixing code bugs. `/doctor` only reports them.
- Filing Issues or Ideas for code bugs.
- Any change to `/triage`.
- The `doctor-runs-retro` Spec. It also edits `/doctor`'s Report section, but neither Spec has to land first.
- The duplicate ADR number 0050, which `.agents/ideas/duplicate-adr-numbers.md` already covers.

## Further Notes

The request came from a `/grill-with-docs` session. It started from a `/doctor` run in an app repository that flagged eight ADRs the code contradicted and changed none of them. The user's view was that stale documentation is not acceptable.
