---
name: refine
description: A room session that determines a change's scope — what is in this project and what is not — so a developer can start /grill-with-docs.
disable-model-invocation: true
---

# Refine

Run a refinement session: several people in one **room**, one keyboard, determining **Scope** — what is part of this project and what is not. The outcome is a **Refinement**: a briefing a developer uses to start `/grill-with-docs`. Silent on implementation ([ADR-0018](../../docs/adr/0018-refine-determines-scope-via-prototype.md)).

**The room's clock** is the scarce resource: an idle minute costs as many minutes as there are people in the call. Reading happens in the background. The room stops for the **Prototype** and the closing read-back.

The session does minimal grilling, then a first Prototype, then the room **steers** from the demo.

Two documents, templated in [DOCUMENTS.md](DOCUMENTS.md):

- **`session.md`** — **resume** infrastructure. Full-fidelity today (code anchors included) so a later session reopens without re-deriving.
- **`complete.md`** — what the room signs off.

**User-facing** surfaces — live rounds, `complete.md`, write-back — run at **room language**: every sentence readable aloud once to someone who does not write code. Run `/plain-language`, then hold that stricter bar. Resume density in `session.md` is exempt ([ADR-0010](../../docs/adr/0010-refine-user-facing-surfaces.md)).

## 1. Take the input

A Jira ticket key or URL, a markdown file, or a sentence typed into the invocation. Retrieve a ticket through whatever MCP tools this session has. An Idea at `.agents/ideas/<slug>.md` is the usual markdown file; any `.md` path is allowed. Read it; close may replace it.

Derive a kebab-case slug from the change itself rather than the ticket key. Everything the session writes lands in `.agents/refinements/<slug>/`.

A `complete.md` already there means the change is settled; reopening it is an explicit ask. Otherwise a `session.md` makes this a **resume**: read it, replay settled items as declarations, grill only what is open — everything absent from the document is open. A Prototype path already in the document resumes at step 5; a Prototype still in flight is resumed by `/prototype`.

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

## 3. Grill just enough

**Round 1 is yours, and it is intent only.** It goes out the moment the input is read and the first two agents are dispatched — bare, because intent questions need nothing from the code.

**Round 2 names the question the Prototype will answer** — which flow or screen the room will look at. Agreeing that question is the go-ahead to build.

Run `/grilling` with the subject pinned to **functional** for the whole session.

Run `/domain-modeling` **glossary-only**: settled terms land in `CONTEXT.md` as they settle, and stop there.

Price every option with a **room cost** first — user harm, support load, who gets stuck, compliance, what people do instead today. A one-clause mechanism trailer earns its place only when it would change the pick.

Speak today as behaviour in every live question. `/grilling` treats a running exploration as an unsettled prerequisite; here it deliberately is not, and the frontier is grilled around it. Code-dependent questions wait and **batch**: one probe per round for every code-dependent question that round surfaced, so the room's clock stops once rather than once per question. When the probe returns, frame each follow-up as *today does X — what should happen?* Options name outcomes.

Any question can be **parked** — the room says "later, not this session"; it lands under `Open Questions` naming who owes the answer; that branch of the frontier closes.

Append to `.agents/refinements/<slug>/session.md` as the session runs. Write for resume: `How it works today` keeps the explorers' full account. Each round's answers are in the document before the next round's questions go out.

Done when intent is settled, the room has agreed or declined the Prototype question, and those answers are on disk in `session.md`.

## 4. Build the first Prototype

If the room declined a Prototype, skip to step 5.

Tell the room this wait is coming. Follow `/prototype` through handover for the question round 2 settled. It serves this effort. Name `.agents/refinements/<slug>/prototype/` as the folder it writes. The Prototype does not wait for the Code walk.

Done when the file or URL is in the room's hands.

## 5. Steer

The Prototype is the conversation. The room reacts; revise the same Prototype until the room can name what is in and what is out. A new Prototype only if the question itself was wrong.

Questions in text only for things a demo cannot show — who is allowed, compliance, what this project will not do. Same grilling rules as step 3, including batching.

The moment the change looks like several changes, name the split out loud and let the room decide. If they split it, the other work goes on the out list, and each split-off gets `.agents/refinements/<other-slug>/session.md` carrying its intent and nothing else: a resumable Refinement, not a note. A stub gets no `complete.md`.

Keep `session.md` current: in, out, the Prototype path, parked questions. When the room has named in and out, write the folder named in step 4 as `/prototype` serving a larger effort describes, or `None`.

Done when `In scope` and `Out of scope` are written in `session.md` and the room has confirmed them, every text-only question is settled or parked, every accepted split-off has a stub (or the room declined), and the Prototype folder is on disk (or Prototype is `None`).

## 6. Synthesise the complete document

If the code walk has not returned, wait for it: the read-back needs a confirmed today.

Read the settled Complete picture back to the room in room language — Intent, How it works today, In scope, Out of scope, Prototype, Open Questions — and wait for confirmation.

Then write `.agents/refinements/<slug>/complete.md` from the template and mapping in [DOCUMENTS.md](DOCUMENTS.md).

Done when all six sections are present and each carries content or `None`.

## 7. Close

1. Report the absolute path of `.agents/refinements/<slug>/`. The Prototype is already in the room's hands.
2. **Write-back.** If the session started from a Jira ticket or a markdown file, show the payload and wait for a yes. Jira payload is `complete.md` as Jira markup; a file payload is `complete.md` as markdown. A yes replaces the ticket description or overwrites the source file. A no leaves the source and continues. A typed sentence has no write-back.
3. Commit the Refinement folder. Include the source markdown file when write-back overwrote a file in the repo.

`complete.md` is what was signed off. `session.md` remains the resume source for today-claims that trace to the code.

Then stop — a Refinement is terminal. A developer starts `/grill-with-docs` from this document, in a session with a different room.

Done when the folder path is reported, write-back has a yes, a no, or no source, the Refinement folder is committed (Prototype `None` skips that subdirectory), and the session has stopped.
