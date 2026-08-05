---
name: refine
description: A round-by-round session with Product, QA, and Development that settles a change functionally — intent, use cases, and the delta against today.
disable-model-invocation: true
---

# Refine

Run a refinement session: several people in one **room**, one keyboard, working out *what* we want to change in the application. The outcome is a **Refinement** — intent, use cases, and the **delta** against **today** — deliberately silent on implementation.

**The room's clock** is the scarce resource: an idle minute costs as many minutes as there are people in the call. Reading happens in the background, and the room is stopped only where stopping is worth it.

The session writes two documents, both templated in [DOCUMENTS.md](DOCUMENTS.md): a **session document** held for resume, and a **complete document** the room signs off. Only the complete document, its HTML, the mid-session HTML, the live rounds, and any Jira write-back are **user-facing**. `session.md` is resume infrastructure — full fidelity so a later session can reopen the change without re-deriving today.

Run the `/plain-language` skill, then hold a stricter bar than it asks for on every user-facing sentence: readable aloud once, in a room, to someone who does not write code. That binds the rounds, both HTML renders, `complete.md`, and the Jira write-back. A room cannot go back and re-read a hard sentence. The resume density of `session.md` is not held to that bar.

## 1. Take the input

A Jira ticket key or URL, an Idea at `.agents/ideas/<slug>.md`, or a sentence typed into the invocation. Retrieve a ticket through whatever MCP tools this session has; an Idea is read and left in place.

Derive a kebab-case slug from the change itself rather than the ticket key. Everything the session writes lands in `.agents/refinements/<slug>/`.

A `complete.md` already there means the change is settled, and reopening it is an explicit ask rather than an assumption. Otherwise a `session.md` makes this a **resume**: read it, replay what it has settled as declarations, and grill only what is open — everything absent from the document is open.

Done when you can state the change in a sentence and know whether this is a resume.

## 2. Dispatch the exploration

**Today** is yours to establish from the code, never the room's to supply, and never with the room stopped. Three `skills:explorer` background agents, differing only in what you ask them:

- **Docs pass** — `CONTEXT.md`, the ADRs, recent git history. Aimed by the input, out as the session opens.
- **Already-built probe** — does this change already ship? Aimed by the ticket, out as the session opens.
- **Code walk** — how the affected area actually works. Aimed by **intent**, so it waits for round 1.

The docs pass lands mid-round and writes a **provisional today**: a `How it works today` taken from the documents and labelled as such, because documents lag code. The code walk replaces it with the confirmed section — full fidelity for resume, including code anchors — and the label goes.

Dispatch the code walk once round 1 closes, whether or not intent settled — aimed from the ticket if it has to be, re-dispatched when intent turns out to be somewhere else.

Two findings interrupt the room the moment they arrive, mid-round if need be:

- **Already built** — the change exists. Tell the room what users already get and where they get it, in room language. Raised by the probe and the code walk alone: a false positive here ends a session that should have run.
- **Contradiction** — two accounts of today disagree. Name which two — the room's, the documents', the code's — restate the code's account as behaviour, and treat that as the one that is right.

Everything else waits for the round to close.

Done when the dispatches are out, not when they return. A resume dispatches the same way, and re-verifies an inherited `How it works today` only when a question touches it.

## 3. Grill at functional altitude

**Round 1 is yours, and it is intent only.** It goes out the moment the input is read and the first two agents are dispatched — bare, because intent questions need nothing from the code. No use-case or delta question until the room has agreed *why* the change is wanted; a room that hasn't agreed why produces use cases encoding three different goals.

From round 2 the **frontier** — the questions whose prerequisites the room has already settled — decides the rounds. Run the `/grilling` skill with the subject pinned to **functional**, and hold it there for the whole session however far the room wants to drop. Keep the grilling form (Subject line, Q/D numbers, lettered options).

Run the `/domain-modeling` skill alongside it with one override: terms the room settles land in `CONTEXT.md` as they settle; do not offer or write ADRs. Existing ADRs stay part of the docs pass that establishes today.

Every option leads with a **room cost** — user harm, support load, who gets stuck, compliance, what people do instead today. At most one short mechanism clause may trail, and only when that clause would change the pick.

When a live question needs a fact from today, restate that fact as behaviour in the question — even when `session.md` already holds the code-level note.

`/grilling` treats a running exploration as an unsettled prerequisite; here it deliberately is not, and the frontier is grilled around it. A question that genuinely needs code does wait, but **batch them**: dispatch every code-dependent question a round surfaced as one probe, so the room's clock stops once per round rather than once per question. When the probe returns, restate findings as *today does X*, then ask only what should happen instead — never a proposed mechanism as the choice.

Hunt edge cases: every use case leaves the session carrying at least one scenario that is not the happy path.

Any question can be **parked** — the room says "later, not this session", it lands under `Open Questions` naming who owes the answer, and that branch of the frontier closes.

Done when every branch of the frontier is settled or parked, and every use case carries its non-happy-path scenario.

## 4. Write the session document live

Append to `.agents/refinements/<slug>/session.md` as the session runs, so an interrupted one leaves something for a resume to pick up. Each round's answers are in the document before the next round's questions go out — that is the completion criterion for every round, not just the last. Write for resume: `How it works today` keeps the explorers' full account.

When the room asks for the picture mid-session, render `session.html` — a user-facing surface. Restate `How it works today` as behaviour and observable limits only (no modules, paths, or types); map `Intent` to introduction and `What changes` to scope. Only the closing render produces a `complete.html`, so the filename never claims more than the session has settled. See [HTML-REPORT.md](HTML-REPORT.md).

## 5. Offer the split

The moment the change looks like several changes — mid-round, any round, as soon as you see it — name the split out loud and let the room decide. Holding it until the end spends a whole session grilling a scope the room would have cut.

If they split it, finish the current document on the change the room came for, and create `.agents/refinements/<other-slug>/session.md` for each split-off change carrying its intent and nothing else: a resumable Refinement, not a note. Link to them from the closing document's `Out-of-scope`. A stub gets no `complete.md` and no HTML report — both are session outputs.

## 6. Synthesise the complete document

Read the settled **Complete** picture back to the room — Introduction, use cases, scope, out-of-scope, open questions, and Notes — in room language, and wait for their confirmation. Never read the resume walkthrough aloud. If the code walk has not returned, wait for it first: the read-back is what the room signs off, so it is the one stop on the room's clock worth paying for, and it carries a confirmed today.

Then write `.agents/refinements/<slug>/complete.md` from the template and mapping in [DOCUMENTS.md](DOCUMENTS.md). This is a synthesis rather than a rename: today's pain goes to `Introduction`, constraints and implications of today go to `Notes`, and the full walkthrough stays only in `session.md`.

Done when all six sections are present and each one either carries content or carries `None`.

## 7. Close

1. Render the HTML report at `.agents/refinements/<slug>/complete.html` and open it — `start <path>` on Windows, `open` on macOS, `xdg-open` on Linux — reporting the absolute path. See [HTML-REPORT.md](HTML-REPORT.md).
2. If the session started from a Jira ticket, offer write-back. Replacing the description is the default, because a fixed structure in the ticket is the point and a comment leaves the description as it was; offer a comment instead when the room asks. Show what it would replace and wait for a yes. Send `complete.md` converted to Jira markup, with a line pointing at the repo path of `complete.html`.
3. Commit the folder.

`complete.md` is the source of truth for what was signed off: `complete.html` is rendered from it and never parsed, so no signed-off fact lives only in the picture. `session.md` remains the resume source for today-claims that trace to the code.

Then stop — a Refinement is terminal. A Spec may be grilled out of it later with `/grill-with-docs` or `/to-spec`, the user's call in a session with a different room.
