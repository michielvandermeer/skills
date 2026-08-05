# The two documents

Templates and the mapping a `/refine` session uses when writing `.agents/refinements/<slug>/`. **`session.md`** is resume infrastructure; **`complete.md`** is user-facing (what the room signs off and may write back to Jira).

## Session document — `session.md`

Shaped for live append and for a resume to re-open the change without re-deriving today. Section order is fixed; sections fill as content arrives: `Intent` may settle while `How it works today` is still provisional.

```markdown
# <Change title>

Source: <Jira key / `.agents/ideas/<slug>.md` / conversation>

## Intent

Why we want this and whose problem it solves.

## How it works today

What the affected area does today, read from the code — full fidelity for resume, including code anchors. Headed `(provisional — from the documents)` until the code walk confirms it.

## What changes

The delta, functionally — short enough to skim.

## Use Cases

1. As an <actor>, I want <capability>, so that <benefit>
   - **Scenario:** given <state>, when <the actor does this>, then <observable outcome>
   - **Scenario:** <the non-happy path>
   - *Differs from today:* <what the room does instead now>

## Open Questions

- <question> — owed by <who>

## Out of Scope

- <thing>, and why
```

## Complete document — `complete.md`

All six sections always present, in this order, carrying `None` where the session settled nothing: a missing heading reads as an oversight, `None` reads as a decision the room made.

```markdown
# <Change title>

Source: <Jira key / `.agents/ideas/<slug>.md` / conversation>

## Introduction

What this change is about and why we are doing it — today's pain in a sentence or two, since that is the why.

## Open Questions

- <question> — owed by <who>

## Use cases

1. As an <actor>, I want <capability>, so that <benefit>
   - **Scenario:** given <state>, when <the actor does this>, then <observable outcome>
   - **Scenario:** <the non-happy path>
   - *Differs from today:* <what the room does instead now>

## Scope

What we are doing as part of this project, as work items. The one place work carrying no user-facing story lands — migrations, removals, configuration.

## Out-of-scope

- <thing>, and why

## Notes

Constraints and implications of today that bind the change, plus anything useful before pickup that the sections above leave unsaid. A constraint of today belongs here; a chosen approach belongs in a Spec ([ADR-0005](../../docs/adr/0005-refinement-is-terminal-and-functional-only.md)).
```

## The mapping

Synthesise Complete from the Session document — rename nothing.

| Complete section | Comes from |
|---|---|
| Introduction | `Intent`, plus today's pain in a sentence or two — that pain *is* the why |
| Open Questions | `Open Questions` verbatim |
| Use cases | `Use Cases` verbatim, `Differs from today` included |
| Scope | `What changes`, restated as work items |
| Out-of-scope | `Out of Scope`, plus links to any split-off stubs |
| Notes | Constraints and implications of today from `How it works today`, plus what no section above carries |

`How it works today` feeds Complete without its own Complete heading: pain → `Introduction`, constraints → `Notes`. The full read-from-code account stays only in `session.md`.
