---
name: refine
description: A round-by-round session with Product, QA, and Development that settles a change functionally — intent, use cases, and the delta against today.
disable-model-invocation: true
---

# Refine

Run a refinement session: several people in one **room**, one keyboard, working out *what* we want to change in the application. The outcome is a **Refinement** — intent, use cases, and the **delta** against **today** — functional only ([ADR-0005](../../docs/adr/0005-refinement-is-terminal-and-functional-only.md)).

**The room's clock** is the scarce resource: an idle minute costs as many minutes as there are people in the call. Reading happens in the background; stop the room only where stopping is worth it.

Two documents, templated in [DOCUMENTS.md](DOCUMENTS.md):

- **`session.md`** — **resume** infrastructure. Full-fidelity today (code anchors included) so a later session reopens without re-deriving.
- **`complete.md`** — what the room signs off.

**User-facing** surfaces — live rounds, `session.html`, `complete.md`, `complete.html`, Jira — run at **room language**: every sentence readable aloud once to someone who does not write code. Run `/plain-language`, then hold that stricter bar. Resume density in `session.md` is exempt ([ADR-0010](../../docs/adr/0010-refine-user-facing-surfaces.md)).

## 1. Take the input

A Jira ticket key or URL, an Idea at `.agents/ideas/<slug>.md`, or a sentence typed into the invocation. Retrieve a ticket through whatever MCP tools this session has; an Idea is read and left in place.

Derive a kebab-case slug from the change itself rather than the ticket key. Everything the session writes lands in `.agents/refinements/<slug>/`.

A `complete.md` already there means the change is settled; reopening it is an explicit ask. Otherwise a `session.md` makes this a **resume**: read it, replay settled items as declarations, grill only what is open — everything absent from the document is open.

Done when you can state the change in a sentence and know whether this is a resume.

## 2. Dispatch the exploration

**Today** is yours to establish from the code, never the room's to supply, and never with the room stopped. Three `skills:explorer` background agents, differing only in what you ask them:

- **Docs pass** — `CONTEXT.md`, the ADRs, recent git history. Aimed by the input, out as the session opens.
- **Already-built probe** — does this change already ship? Aimed by the ticket, out as the session opens.
- **Code walk** — how the affected area actually works. Aimed by **intent**, so it waits for round 1.

The docs pass lands mid-round and writes a **provisional today**: a `How it works today` taken from the documents and labelled as such, because documents lag code. The code walk replaces it with the confirmed full-fidelity section and the label goes.

Dispatch the code walk once round 1 closes, whether or not intent settled — aimed from the ticket if it has to be, re-dispatched when intent turns out to be somewhere else.

Two findings interrupt the room the moment they arrive, mid-round if need be:

- **Already built** — the change exists. Tell the room, in room language, what users already get. Raised by the probe and the code walk alone: a false positive here ends a session that should have run.
- **Contradiction** — two accounts of today disagree. Name which two — the room's, the documents', the code's — restate the code's account as behaviour, and treat that as right.

Everything else waits for the round to close.

Done when the dispatches are out, not when they return. A resume dispatches the same way, and re-verifies an inherited `How it works today` only when a question touches it.

## 3. Grill at functional altitude

**Round 1 is yours, and it is intent only.** It goes out the moment the input is read and the first two agents are dispatched — bare, because intent questions need nothing from the code. Use cases and delta wait until the room has agreed *why*; a room that hasn't agreed why produces use cases encoding three different goals.

From round 2 the **frontier** (the questions whose prerequisites the room has already settled) decides the rounds. Run `/grilling` with the subject pinned to **functional** for the whole session, however far the room wants to drop.

Run `/domain-modeling` **glossary-only**: settled terms land in `CONTEXT.md` as they settle, and stop there.

Price every option with a **room cost** first — user harm, support load, who gets stuck, compliance, what people do instead today. A one-clause mechanism trailer earns its place only when it would change the pick.

Speak today as behaviour in every live question. `/grilling` treats a running exploration as an unsettled prerequisite; here it deliberately is not, and the frontier is grilled around it. Code-dependent questions wait and **batch**: one probe per round for every code-dependent question that round surfaced, so the room's clock stops once rather than once per question. When the probe returns, frame each follow-up as *today does X — what should happen?* Options name outcomes.

Every use case leaves carrying at least one scenario that is not the happy path.

Any question can be **parked** — the room says "later, not this session"; it lands under `Open Questions` naming who owes the answer; that branch of the frontier closes.

Done when every branch of the frontier is settled or parked, and every use case carries its non-happy-path scenario.

## 4. Write the session document live

Append to `.agents/refinements/<slug>/session.md` as the session runs. Write for resume: `How it works today` keeps the explorers' full account. Each round's answers are in the document before the next round's questions go out.

When the room wants the picture mid-session, render `session.html` per [HTML-REPORT.md](HTML-REPORT.md). Only the closing render produces `complete.html`, so the filename never claims more than the session has settled.

Done when the latest round's answers are on disk in `session.md`.

## 5. Offer the split

The moment the change looks like several changes — mid-round, any round — name the split out loud and let the room decide. Holding it until the end spends a whole session grilling a scope the room would have cut.

If they split it, finish the current document on the change the room came for, and create `.agents/refinements/<other-slug>/session.md` for each split-off carrying its intent and nothing else: a resumable Refinement, not a note. Link them from the closing document's `Out-of-scope`. A stub gets no `complete.md` and no HTML report — both are session outputs.

Done when the room has decided, and every accepted split-off has a stub (or the room declined).

## 6. Synthesise the complete document

If the code walk has not returned, wait for it: the read-back is the one stop on the room's clock worth paying for, and it needs a confirmed today.

Read the settled Complete picture back to the room in room language — Introduction, use cases, scope, out-of-scope, open questions, Notes — and wait for confirmation.

Then write `.agents/refinements/<slug>/complete.md` from the template and mapping in [DOCUMENTS.md](DOCUMENTS.md).

Done when all six sections are present and each carries content or `None`.

## 7. Close

1. Render `.agents/refinements/<slug>/complete.html` and open it — `start <path>` on Windows, `open` on macOS, `xdg-open` on Linux — reporting the absolute path. See [HTML-REPORT.md](HTML-REPORT.md).
2. If the session started from a Jira ticket, offer write-back. Replacing the description is the default (fixed structure in the ticket is the point); offer a comment instead when the room asks. Show what it would replace and wait for a yes. Send `complete.md` as Jira markup, with a line pointing at the repo path of `complete.html`.
3. Commit the folder.

`complete.md` is what was signed off; `complete.html` is rendered from it and never parsed. `session.md` remains the resume source for today-claims that trace to the code.

Then stop — a Refinement is terminal. A Spec may be grilled out of it later with `/grill-with-docs` or `/to-spec`, the user's call in a session with a different room.

Done when the HTML is open, any Jira write-back offer is resolved, the folder is committed, and the session has stopped.
