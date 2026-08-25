# The two documents

Templates and the mapping a `/refine` session uses when writing `.agents/refinements/<slug>/`. **`session.md`** is resume infrastructure; **`complete.md`** is user-facing (what the room signs off and may write back to the Jira ticket or source markdown file).

Both documents share these headings. Section order is fixed; session sections fill as content arrives. Session `How it works today` is full fidelity, including code anchors, and carries `(provisional — from the documents)` until the code walk confirms it. Complete `How it works today` is behaviour.

```markdown
# <Change title>

Source: <Jira key / markdown path / conversation>

## Intent

Why we want this and whose problem it solves.

## How it works today

What the affected area does today.

## In scope

What is part of this project, as user-facing outcomes.

## Out of scope

- <thing>, and why

## Prototype

Path, the question it answered, and what playing with it settled for Scope. `None` if the room declined a Prototype.

## Open Questions

- <question> — owed by <who>
```

On Complete, every section is always present, carrying `None` where the session settled nothing: a missing heading reads as an oversight, `None` reads as a decision the room made.

## The mapping

Synthesise Complete from the Session document — rename nothing. Restate `How it works today` as behaviour. Constraints of today live there, not in a Notes section.

| Complete section | Comes from |
|---|---|
| Intent | `Intent` |
| How it works today | `How it works today`, restated as behaviour |
| In scope | `In scope` |
| Out of scope | `Out of scope`, plus links to any split-off stubs |
| Prototype | `Prototype` — path `.agents/refinements/<slug>/prototype/`, the question, what playing settled for Scope |
| Open Questions | `Open Questions` verbatim |

The full read-from-code account stays only in `session.md`.
