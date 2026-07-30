---
name: refine
description: A round-by-round session with Product, QA, and Development that settles a change functionally — intent, use cases, and the delta against today.
disable-model-invocation: true
---

# Refine

Run a refinement session: several people in one **room**, one keyboard, working out *what* we want to change in the application. The outcome is a **Refinement** — intent, use cases, and the **delta** against **today** — deliberately silent on implementation.

## 1. Take the input

A Jira ticket key or URL, an Idea at `.agents/ideas/<slug>.md`, or a sentence typed into the invocation. Retrieve a ticket through whatever MCP tools this session has; an Idea is read and left in place.

Derive a kebab-case slug from the change itself rather than the ticket key. If `.agents/refinements/<slug>.md` already exists, this is a **resume**: read it, replay what it has settled as declarations, and grill only what is open — everything absent from the document is open.

## 2. Establish today

**Today** is yours to establish from the code, never the room's to supply. A Dev in the room will volunteer it; it reaches the document once you have read the code yourself. Explore with a `skills:explorer` sub-agent, and a resume re-establishes today because the code may have moved.

Two findings are surfaced before round 1 rather than grilled around:

- **Already built** — the change exists. Say where it lives.
- **Contradiction** — the room's account of today disagrees with the code. Name it.

Done when `How it works today` is written from the code and both findings are surfaced or ruled out.

## 3. Grill at functional altitude

Run the `/grilling` skill with the subject pinned to **functional**, and hold it there for the whole session however far the room wants to drop. Run the `/domain-modeling` skill alongside it: terms the room settles land in `CONTEXT.md` as they settle, ADRs offered on the three-part test.

The frontier decides the rounds, with one gate: **intent first**. No use-case or delta question until the room has agreed *why* the change is wanted — a room that hasn't agreed why produces use cases encoding three different goals.

Hunt edge cases: every use case leaves the session carrying at least one scenario that is not the happy path.

Any question can be **parked** — the room says "later, not this session", it lands under `Open Questions` naming who owes the answer, and that branch of the frontier closes.

Done when every branch of the frontier is settled or parked.

## 4. Write live

Append to `.agents/refinements/<slug>.md` as the session runs, so an interrupted one leaves something for a resume to pick up. Each round's answers are in the document before the next round's questions go out.

```markdown
# <Change title>

Source: <Jira key / `.agents/ideas/<slug>.md` / conversation>

## Intent

Why we want this and whose problem it solves.

## How it works today

What the affected area does today, read from the code.

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

## 5. Offer the split

When the change turns out to be several changes, name the split out loud and let the room decide.

If they split it, finish the current document on the change the room came for, and create `.agents/refinements/<other-slug>.md` for each split-off change carrying its intent and nothing else: a resumable Refinement, not a note. Link to them from `Out of Scope`. A stub gets no HTML **twin** — the twin is a session output.

## 6. Close

1. Read the settled picture back to the room and wait for their confirmation.
2. Render the twin at `.agents/refinements/<slug>.html` and open it — `start <path>` on Windows, `open` on macOS, `xdg-open` on Linux — reporting the absolute path. Render mid-session too, whenever the room asks for the picture. See [HTML-REPORT.md](HTML-REPORT.md).
3. If the session started from a Jira ticket, offer write-back — a comment or a replacement of the description, the room's choice. Show what it would replace and wait for a yes. Send the markdown converted to Jira markup, with a line pointing at the repo path of the twin.
4. Commit both files.

The markdown is the source of truth: the twin is rendered from it and never parsed, so no fact lives only in the picture.

Then stop — a Refinement is terminal. A Spec may be grilled out of it later with `/grill-with-docs` or `/to-spec`, the user's call in a session with a different room.
