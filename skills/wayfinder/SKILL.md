---
name: wayfinder
description: Plan a change too big for one agent session as a shared map of decision tickets under .agents/issues/, resolved one at a time until the way is clear and its Specs can be written.
disable-model-invocation: true
---

A loose idea has arrived — too big for one agent session, and wrapped in fog: the way from here to the **destination** isn't visible yet. Wayfinding is about finding that way, not charging at the destination. This skill charts the way as a **shared map** of markdown files under `.agents/issues/`, then works its **decision tickets** — questions whose resolution is a decision, not slices of a build to execute — one at a time until the route is clear.

The destination is always the same: one or more Specs at `.agents/specs/<slug>.md`, each ready to hand to `/implement`. What varies is the change those Specs cover, and fixing that scope is the first act of charting — it shapes every ticket. How many Specs, and where one ends, waits until no tickets remain ([ADR-0047](../../docs/adr/0047-a-wayfinder-map-ends-in-one-or-more-specs.md)).

## Plan, don't do

Wayfinder is **planning**: it produces decisions, not deliverables. The pull to just do the work is the signal you've reached the edge of the map, and the Specs are where you put it.

## Forks in the road

A **fork** is two ways on, and the one you take changes what gets built. Everything between forks is just road — walk it, don't chart it.

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

<the whole change this effort's Specs will cover, and what it leaves alone. One or two lines; every session orients to it before choosing a ticket.>

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

A session **claims** a ticket by setting its `Status:` line to `claimed`, **first**, before any work, so concurrent sessions skip it. That `Status:` value _is_ the claim: a ticket with no `Status:` line is unclaimed. Firing a `/research` subagent is work, so a session fires one by **claim-then-fire**: write `Status: claimed` in the ticket file, in the working copy the user invoked (the copy other sessions scan), wait until that write is on disk, then fire. A research ticket this session creates and will fire may carry the claim from creation. The subagent's only status write is `resolved`.

Blocking is recorded as a `Blocked by: NN, NN` line near the top of the ticket file. A ticket is **unblocked** when every ticket it lists is `resolved`; the **frontier** is the open (no `Status:` line), unblocked, unclaimed tickets — the edge of the known. A ticket **remains** until it is `resolved` or `out-of-scope`; claimed and blocked tickets remain.

The answer isn't part of the body — it's recorded on resolution (see [Work through the map](#work-through-the-map)). Assets created while resolving a ticket are linked from the ticket file, not pasted in.

A ticket that sits past the destination gets `Status: out-of-scope` rather than an answer — see [Out of scope](#out-of-scope).

## Ticket Types

Every ticket is either **HITL** — human in the loop, worked *with* a human who speaks for themselves — or **AFK**, driven by the agent alone. A HITL ticket only resolves through that live exchange; the agent never stands in for the human's side of it (a grilling agent that answers its own questions has broken this).

- **Research** (AFK): Reading documentation, third-party APIs, or local resources like knowledge bases to surface a fact a decision waits on. Resolved by a `/research` **subagent**, fired by [claim-then-fire](#tickets). Use when knowledge outside the current working directory is required.
- **Prototype** (HITL): Raise the fidelity of the discussion by making a cheap, rough, concrete artifact to react to — an outline, a rough take, a stub, or UI/logic code via the /prototype skill. A `/prototype` invoked here serves this effort: it hands its verdict back for the answer to record, saves the prototype so the Spec covering its part can point at it, and leaves the worktree to the effort. Use when "how should it look" or "how should it behave" is the key question.
- **Grilling** (HITL): Conversation via the /grilling and /domain-modeling skills, round by round. The default case. Two shapes — see [Grilling tickets](#grilling-tickets).
- **Task** (HITL or AFK): Manual work that must happen before a *decision* can be made — nothing to decide, prototype, or research, but the discussion is blocked until it's done. Signing up for a service so its API can be judged, provisioning access, moving data so its shape can be seen. This is the one type that *does* rather than decides — and it earns its place by unblocking a decision, not by delivering the destination. The agent drives it alone where it can (AFK); otherwise it hands the human a precise checklist (HITL). Resolved when the work is done; the answer records what was done and any resulting facts (credentials location, new URLs, row counts) later tickets depend on.

## Grilling tickets

Both shapes are `Type: grilling`.

**Focused** — the fork is a tree: more than one question already nameable, or one-question forks that would block each other. Body and heading as any other ticket.

**Small questions** — leftover unblocked one-question forks, subjects need not match. Body is one `## Question` listing each leftover as a short decision. Heading `Small questions`, then `Small questions 2`. At most one open.

One-question means one closed choice and no follow-up already nameable.

**Group** when creating grilling tickets — every grilling fork ends as a Focused ticket, a leftover in Small questions, or a blocked one-question standalone:

1. Mint Focused tickets for trees.
2. Leftover unblocked one-question forks join the unclaimed open Small questions (a singleton joins too) unless the 250K ceiling would be exceeded. With nothing to join: two or more mint Small questions; a singleton keeps a heading that names its fork.
3. A blocked one-question grilling ticket stays until it unblocks, then it is a leftover — join or mint, and delete the standalone file.

Resolving Small questions: `/grilling`, round 1 every leftover in the body, until that ticket's frontier is empty. Decisions-so-far: one line; the gist lists each decision.

## Fog of war

The map is _deliberately_ incomplete: don't chart what you can't yet see. Beyond the live tickets lies the **fog of war** — the dim view of decisions and investigations you can tell are coming but can't yet pin down, because they hang on questions still open. Resolving a ticket clears the fog ahead of it, graduating whatever's now specifiable into fresh tickets.

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

Two modes. Either way, **never resolve more than one ticket per session** — with the exception of research tickets.

### Chart the map

User invokes with a loose idea.

1. **Fix the scope.** Run one `/grilling` and `/domain-modeling` session on the change itself: what it covers, what it leaves alone, and which forks stand in the way. **If the way is already clear** — after grouping grilling forks, one session and no fog — you don't need a map. Stop and ask the user how they'd like to proceed.
2. **Create the map** (`.agents/issues/<effort>/map.md`): Destination and Notes filled in, Decisions-so-far empty, the fog sketched into **Not yet specified**.
3. **Create the tickets you can specify now** as files in `.agents/issues/<effort>/`. **Group** grilling tickets per [Grilling tickets](#grilling-tickets), then assign each its `NN` first, then wire `Blocked by:` lines in a **second pass** (a ticket needs its number before others can reference it). Create each `research` ticket with `Status: claimed` already set, since step 4 fires it. Wiring sorts them into the frontier and the blocked; everything you can't yet specify stays in the fog — the **Not yet specified** section.
4. **Fire the research subagents.** For each `research` ticket, [claim-then-fire](#tickets) its `/research` subagent. Fire each in turn; they run together, and charting does not wait on them. Each subagent captures findings on a throwaway `research/<name>` branch, leaves a context pointer on the ticket, writes `## Answer`, and sets `Status: resolved`. Then run `/retro`. Charting is one session's work; it ends with its research tickets still claimed and hand-resolves nothing.

### Work through the map

User invokes with a map (path or effort name). A ticket is **optional** — without one, you pick the next fork, not the user.

1. Load the **map** — the low-res view, not every ticket body. When no tickets remain, [write the Specs](#write-the-specs) instead. When tickets remain but the frontier is empty, name each remaining ticket and what it waits on — for a claimed research ticket, that's "research still running" — tell the user to run `/wayfinder <effort>` again once they resolve, and end. A claim stands until the user clears its `Status:` line.
2. Choose the ticket. If the user named a claimed ticket, tell them another session holds it — for a research ticket, "research still running" — and end. Otherwise use the ticket the user named, or else the first frontier ticket in order. **Claim it**: set `Status: claimed` before any work.
3. Resolve it — **zoom as needed**: read the full body of any related or resolved ticket on demand; invoke the skills the `## Notes` block names. If in doubt, use `/grilling` and `/domain-modeling`. A grilling ticket resolves per [Grilling tickets](#grilling-tickets). For a research ticket that graduated later, finish its [claim-then-fire](#tickets): once step 2's claim is on disk, fire its `/research` subagent rather than reading it in the Driving session.
4. Record the resolution: append the answer under an `## Answer` heading in the ticket file, set `Status: resolved`, and **append a context pointer** to the map's Decisions-so-far in `map.md`.
5. Add newly-surfaced tickets and graduate any fog the answer has made specifiable (**group** grilling per [Grilling tickets](#grilling-tickets), then create-then-wire), clearing each graduated patch from **Not yet specified** so it lives only as its new ticket. For each new `research` ticket, [claim-then-fire](#tickets) its `/research` subagent now. If the answer reveals a ticket — this one or another — sits beyond the destination, **rule it out of scope** rather than resolving it on the route. If the decision invalidates other parts of the map, update or delete those tickets.

Then run `/retro`. When no tickets remain, the way is clear: end on one last line, after the retro summary, telling the user to run `/wayfinder <effort>` in a fresh session to write the Specs. The Specs need every resolved ticket loaded, and this session holds one ([ADR-0048](../../docs/adr/0048-a-fresh-session-writes-a-wayfinder-maps-specs.md)).

The user may run unblocked tickets in parallel, so expect other sessions to be editing the `.agents/issues/` files concurrently.

### Write the Specs

A session reaches this only when it starts on a map with no tickets remaining.

1. **Zoom every resolved ticket.** Read `map.md` and every resolved ticket's full body, with the prototypes and research findings they link. `/to-spec` synthesises from the conversation, so the decisions have to be in it.
2. **Cut.** Each Spec is a change that lands green and is worth shipping on its own. Size is the reason to look for a cut; landing alone is where it goes. A change with no such cut stays one Spec. A Spec may wait on another landing first.
3. **Propose the cut** to the user: one line per Spec — what it covers, and which Spec it waits on. Write nothing until they confirm; an objection redraws the cut.
4. **One `/to-spec` per Spec**, scoped to that Spec's part alone, prerequisites first, naming each prerequisite's slug so `/to-spec` writes its `Blocked by:` line.
5. **Commit** every Spec, and whatever those runs changed, together with the deletion of `.agents/issues/<effort>/`, staged by name, in one commit. The Specs are the record; a Map with every ticket resolved would read as a destination still to write.
