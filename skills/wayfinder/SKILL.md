---
name: wayfinder
description: Plan a change too big for one agent session as a shared map of investigation tickets under .agents/issues/, resolved one at a time until the way is clear and the Spec can be written.
disable-model-invocation: true
---

A loose idea has arrived — too big for one agent session, and wrapped in fog: the way from here to the **destination** isn't visible yet. Wayfinding is about finding that way, not charging at the destination. This skill charts the way as a **shared map** of markdown files under `.agents/issues/`, then works its tickets one at a time until the route is clear.

The destination is always the same: a Spec at `.agents/specs/<slug>.md`, ready to hand to `/implement`. What varies is the change that Spec covers, and fixing that scope is the first act of charting — it shapes every ticket.

## Plan, don't do

Wayfinder is **planning**: it produces decisions, not deliverables. The pull to just do the work is the signal you've reached the edge of the map, and the Spec is where you put it.

## Forks in the road

A ticket is a **fork in the road**: two ways on, and the one you take changes what gets built. Everything between forks is just road — walk it, don't chart it.

Scope is the fork worth pressing hardest. *Do we cover this too? Does that case count?* Those are the user's to answer, and the answer moves the destination.

Once scope is settled, ride what already exists and aim for the smallest change that does the work. An edge case the code handles today needs no decision. An obvious refactor on the way is part of the way; reshaping the system to fit a small change is not.

The territory earns a place on the map only where it gives the way context. An inventory of everything the change touches is territory.

## Refer by name

Every map and ticket has a **name** — the `#` heading at the top of its file. In everything the human reads — narration, the map's Decisions-so-far — refer to it by that name, never by a bare filename or `NN`. A wall of `01, 02, 03` is illegible; names read at a glance. The filename and link don't vanish — a name wraps its link — but they ride *inside* the name, never stand in for it.

Everything the human reads also runs at the bar the `/plain-language` skill sets. A map outlives the session that drew it, and its later readers cannot look up a word only this skill defines. The **Not yet specified** heading is that rule already applied.

## The Map

The map is `.agents/issues/<effort>/map.md` — the canonical artifact. Its tickets are sibling files alongside it in `.agents/issues/<effort>/`.

The map is an **index**, not a store. It lists the decisions made and points at the tickets that hold their detail; a decision lives in exactly one place — its ticket — so the map never restates it, only gists it and links.

### The map body

The whole map at low resolution, loaded once per session. Open tickets are **not** listed — they are files in `.agents/issues/<effort>/` (other than `map.md`) with no `Status:` line, found by scanning.

```markdown
## Destination

<the change the Spec will cover, and what it leaves alone. One or two lines; every session orients to it before choosing a ticket.>

## Notes

<domain; skills every session should consult; standing preferences for this effort>

## Decisions so far

<!-- the index — one line per resolved ticket: enough to judge relevance, then zoom the link for the detail the ticket holds -->

- [<resolved ticket title>](link) — <one-line gist of the answer>

## Not yet specified

<!-- see "Fog of war": in-scope fog you can't ticket yet; graduates as the frontier advances -->

## Out of scope

<!-- see "Out of scope": work ruled beyond the destination; never graduates -->
```

### Tickets

Each ticket is a file at `.agents/issues/<effort>/<NN>-<slug>.md`, numbered from `01`; its filename is its identity. Its body is the question:

```markdown
## Question

<the decision or investigation this ticket resolves>
```

Aim for the fewest tickets that still put every fork on the map. One 250K token agent session is the ceiling on any one of them, not the target.

Each ticket carries a `Type:` line near the top — one of `research`, `prototype`, `grilling`, `task` (see [Ticket Types](#ticket-types)).

A session **claims** a ticket by setting its `Status:` line to `claimed`, **first**, before any work, so concurrent sessions skip it. That `Status:` value _is_ the claim: a ticket with no `Status:` line is unclaimed.

Blocking is recorded as a `Blocked by: NN, NN` line near the top of the ticket file. A ticket is **unblocked** when every ticket it lists is `resolved`; the **frontier** is the open (no `Status:` line), unblocked, unclaimed tickets — the edge of the known.

The answer isn't part of the body — it's recorded on resolution (see [Work through the map](#work-through-the-map)). Assets created while resolving a ticket are linked from the ticket file, not pasted in.

A ticket that sits past the destination gets `Status: out-of-scope` rather than an answer — see [Out of scope](#out-of-scope).

## Ticket Types

Every ticket is either **HITL** — human in the loop, worked *with* a human who speaks for themselves — or **AFK**, driven by the agent alone. A HITL ticket only resolves through that live exchange; the agent never stands in for the human's side of it (a grilling agent that answers its own questions has broken this).

- **Research** (AFK): Reading documentation, third-party APIs, or local resources like knowledge bases. Creates a markdown summary as a linked asset. Use when knowledge outside the current working directory is required.
- **Prototype** (HITL): Raise the fidelity of the discussion by making a cheap, rough, concrete artifact to react to — an outline, a rough take, a stub, or UI/logic code via the /prototype skill. Links the prototype as an asset. Use when "how should it look" or "how should it behave" is the key question.
- **Grilling** (HITL): Conversation via the /grilling and /domain-modeling skills, round by round. The default case.
- **Task** (HITL or AFK): Manual work that must happen before a *decision* can be made — nothing to decide, prototype, or research, but the discussion is blocked until it's done. Signing up for a service so its API can be judged, provisioning access, moving data so its shape can be seen. This is the one type that *does* rather than decides — and it earns its place by unblocking a decision, not by delivering the destination. The agent drives it alone where it can (AFK); otherwise it hands the human a precise checklist (HITL). Resolved when the work is done; the answer records what was done and any resulting facts (credentials location, new URLs, row counts) later tickets depend on.

## Fog of war

The map is _deliberately_ incomplete: don't chart what you can't yet see. Beyond the live tickets lies the **fog of war** — the dim view of decisions and investigations you can tell are coming but can't yet pin down, because they hang on questions still open. Resolving a ticket clears the fog ahead of it, graduating whatever's now specifiable into fresh tickets — one at a time.

The map's **Not yet specified** section is where that dim view is written down: the suspected question, the area to revisit later. It's the undiscovered frontier _toward_ the destination — everything here is in scope, just not sharp enough to ticket. Write as loosely or as fully as the view allows; it doubles as a signpost for collaborators reading where the effort is headed.

**Fog or ticket?** The test is whether you can state the question precisely now — _not_ whether you can answer it now.

- **Ticket when** the question is already sharp — even if it's blocked and you can't act on it yet.
- **Not yet specified when** you can't yet phrase it that sharply. Don't pre-slice the fog into ticket-sized pieces: it's coarser than a ticket, and one patch may graduate into several tickets, or none, once the frontier reaches it.

**Not yet specified** excludes what's already decided (Decisions so far), what's already a live ticket, and what's out of scope (the next section).

## Out of scope

Fog only ever gathers _toward_ the destination. The destination fixes the scope, so work beyond it is **out of scope** — it isn't fog, and it doesn't belong in **Not yet specified**. It gets its own **Out of scope** section on the map: work you've consciously ruled out of _this_ effort. Scope, not sharpness, lands it here.

Out-of-scope work never graduates — the frontier stops at the destination — so it returns only if the destination is redrawn, and then as a fresh effort, not a resumption.

Ruling something out of scope is a scoping act, not a step on the route. When a ticket that already exists turns out to sit past the destination — mis-scoped in while charting, or exposed by a resolution — set its `Status:` to `out-of-scope` (unambiguously off the frontier) and leave one line in the **Out of scope** section: the gist plus why it's out of scope, linking the ticket. It stays out of **Decisions so far**, which records the route actually walked — a scope boundary isn't a step on it.

## Invocation

Two modes. Either way, **never resolve more than one ticket per session.**

### Chart the map

User invokes with a loose idea.

1. **Fix the scope.** Run one `/grilling` and `/domain-modeling` session on the change itself: what it covers, what it leaves alone, and which forks stand in the way. **If it surfaces no fog** — the way is already clear, the whole journey small enough for one session — you don't need a map. Stop and ask the user how they'd like to proceed.
2. **Create the map** (`.agents/issues/<effort>/map.md`): Destination and Notes filled in, Decisions-so-far empty, the fog sketched into **Not yet specified**.
3. **Create the tickets you can specify now** as files in `.agents/issues/<effort>/` — assign each its `NN` first, then wire `Blocked by:` lines in a **second pass** (a ticket needs its number before others can reference it). Wiring sorts them into the frontier and the blocked; everything you can't yet specify stays in the fog — the **Not yet specified** section.
4. Stop — charting the map is one session's work; do not also resolve tickets.

### Work through the map

User invokes with a map (path or effort name). A ticket is **optional** — without one, you pick the next fork, not the user.

1. Load the **map** — the low-res view, not every ticket body.
2. Choose the ticket. If the user named one, use it. Otherwise take the first frontier ticket in order. **Claim it**: set `Status: claimed` before any work.
3. Resolve it — **zoom as needed**: read the full body of any related or resolved ticket on demand; invoke the skills the `## Notes` block names. If in doubt, use `/grilling` and `/domain-modeling`.
4. Record the resolution: append the answer under an `## Answer` heading in the ticket file, set `Status: resolved`, and **append a context pointer** to the map's Decisions-so-far in `map.md`.
5. Add newly-surfaced tickets (create-then-wire); graduate any fog the answer has made specifiable, clearing each graduated patch from **Not yet specified** so it lives only as its new ticket. If the answer reveals a ticket — this one or another — sits beyond the destination, **rule it out of scope** rather than resolving it on the route. If the decision invalidates other parts of the map, update or delete those tickets.

When no tickets remain, the way is clear and that session writes the destination: zoom every resolved ticket, then run `/to-spec`. It synthesises from the conversation, so the decisions have to be in it.

The user may run unblocked tickets in parallel, so expect other sessions to be editing the `.agents/issues/` files concurrently.
