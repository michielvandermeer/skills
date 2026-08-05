# The two documents

A `/refine` session writes two markdown documents into `.agents/refinements/<slug>/`. The Session document is resume infrastructure the agent fills as the session runs; the Complete document is the user-facing picture the room signs off and that may be written back to Jira. Both templates live here, beside the mapping between them.

## Session document — `session.md`

Not user-facing. Shaped for live append and for a resume to re-open the change without re-deriving today. Section order is fixed, but sections fill as their content arrives: `Intent` is settled while `How it works today` is still provisional.

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

User-facing. All six sections are always present, in this order, carrying `None` where the session settled nothing: a missing heading reads as an oversight, `None` reads as a decision the room made.

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

Constraints and implications of today that bind the change, plus anything useful to know before picking this up that the sections above leave unsaid. A constraint of today passes; a chosen approach belongs in a Spec ([ADR-0005](../../docs/adr/0005-refinement-is-terminal-and-functional-only.md)).
```

## The mapping

The Complete document is synthesised, not renamed. Four of its sections come straight across; two draw from `How it works today` or are written fresh:

| Complete section | Comes from |
|---|---|
| Introduction | `Intent`, plus today's pain in a sentence or two — that pain *is* the why |
| Open Questions | `Open Questions` verbatim |
| Use cases | `Use Cases` verbatim, `Differs from today` included |
| Scope | `What changes`, restated as work items |
| Out-of-scope | `Out of Scope`, plus links to any split-off stubs |
| Notes | Constraints and implications of today from `How it works today`, plus what the room knows that no section above carries |

`How it works today` feeds Complete without appearing as its own section: pain to `Introduction`, constraints to `Notes`. The full read-from-code account stays only in `session.md` — which survives the close, so a settled change can be reopened and every today-claim still traces to the code.
