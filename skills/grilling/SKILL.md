---
name: grilling
description: Grill the user relentlessly about a plan or design, round by round. Use when the user wants to stress-test a plan before building, or when another skill needs the round format.
---

Grill me relentlessly until we reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled — the questions you can ask *now* without guessing at answers you haven't heard yet. Ask the whole frontier in one round, however large that is, then wait for my answers.

My answers reshape the tree. Recompute the frontier before each round.

## Facts, decisions, declarations

Finding *facts* is your job, never mine — and it is a sub-agent's job, never your own context's ([ADR-0025](../../docs/adr/0025-grilling-facts-come-from-explorers.md)):

- Read `CONTEXT.md`, the ADRs, and the brief we start from yourself; every fact from the code arrives as an **explorer**'s report (a read-only sub-agent sent with named questions).
- Dispatch the explorer with the questions it must answer, wait for it however long that takes, and carry its report rather than the files. A running exploration is an unsettled prerequisite, and a round posted before it lands is built on guesses.
- Scope needs no facts from the code, so round 1 may go out while explorers run when it asks only scope.
- A report that lands after a round is posted waits silently for the next round.
- A fact only I hold — who the contracting party is, what a price should be — is a question, with a line saying why you could not find it.

A question with one defensible answer is a fact too. Reason it out and state it as a **declaration**. Reserve **questions** for genuine *decisions*, on two tests: would a different answer visibly change what gets built, and would a reasonable owner of this codebase pick the other option? An option you cannot write a cost for, or one the codebase already settles by precedent, is not an option, and the question is a declaration. When both answers land in the same place, pick one and move on without mentioning it.

When every option you can offer fails the goal we opened with, the question is not a decision. Name the prerequisite that blocks it as a declaration and ask one thing: widen scope to cover it, file it as an Idea and stop, or accept the shortfall.

Silence is consent — a declaration I say nothing about stands. An objection reshapes the tree exactly like an answer to a question.

## Altitude

Open round 1 with an **orientation** — one to three plain sentences that name what we are grilling, written for someone who opened this tab cold among several sessions. Then name the **subject** on one line — `Subject: functional (correct me if not)` — in round 1 only, like the orientation; print it again only in the round where it changes, with one line saying why. When a subject is genuinely mixed, classify by where *my* judgement is needed rather than by which half is bigger. An Idea with no user-visible change — a refactor, a flag removal — is `technical` from round 1.

The subject sets the **altitude** you grill at:

- **Functional** — grill high: what we are trying to achieve, how it should behave, what happens at the edges. Technology and structure are yours to settle from precedent already in the codebase, stated as declarations.
- **Technical** — grill low, into the detail. Get there by way of the functional goal, which is clear enough once you could hold up a candidate option and say whether it serves that goal. Until then, keep grilling high.

The size of the change sets where you start, and most sessions are one change to a system that already works — so start high. Grill **scope** before anything else: what this change covers, and what it leaves alone.

- When my request already draws the scope, restate it as a declaration and offer nothing smaller.
- When the request is open-ended, the scope question is round 1 on its own, because every other question hangs off its answer.
- When the session starts from a written brief — an Idea, a Refinement, an Architecture review — D1 is your reading of it in your own words, including what you took from it as settled. Where the brief reads two ways that change what gets built, that is Q1, and the rest of the round waits.

Once scope is settled, ride what already exists and aim for the smallest change that does the work — an edge case the existing code already handles is a declaration, and so is an obvious refactor on the way. The smallest change is the default recommendation, not a position: when I choose a wider option than you recommended, or say the architecture is the point, recommend at that width for the rest of the session. A branch we cut as out of scope but still want is filed as an Idea where the repo keeps them and named in a declaration, without waiting to be asked.

A question about what a screen should look like is a `/prototype` question. Settle scope and behaviour, then run `/prototype` on it and carry its verdict back as declarations; copy, placement, and format wait for the prototype when one is coming.

Testing is a question only when testing is itself the subject; elsewhere, a declaration.

When I accept every recommendation in a round verbatim, or show any sign of annoyance, raise the altitude — one line naming what you are turning into declarations, which I can decline.

Raising altitude means fewer and broader questions. It bottoms out at the functional decisions — those stay questions however much I agree with you, because they are the ones only I can answer. When I ask for more detail, drop the altitude again.

## The shape of a round

Hold this format every session:

```
We're deciding what happens when someone opens an export link after it has expired, and what to call the window that file stays valid for.

Subject: functional (correct me if not)

## Round 1

Q1. **Does an expired export stay downloadable?**

An export is a file we generate on request and keep for a while. This decides what someone sees when they open the link after that window closes.

- a. Deleted on expiry — storage stays flat, and someone who bookmarked the link gets a bare 404. ← recommended
- b. Kept and marked expired — the link still resolves and can say why, at the cost of unbounded growth.

*My recommendation: a* — the bookmarked-link case is rare enough to answer with a generic message.

Q2. **What should we call the window an export stays valid for?**

This name goes into the schema, the API, and the screen, so it is expensive to change later.

*My recommendation:* `retention`, since that is the word the storage layer already uses.

### Declarations

D1. Exports go to the object store already behind the reports feature.
D2. Retention is one fixed window for every user.
```

Round 2 continues the numbering:

```
## Round 2

Q3. **Does a deleted export leave a record?**

The download page lists past exports. This decides whether an expired one still appears there.

- a. No — the list shows only what can be downloaded, so an expired export vanishes without trace. ← recommended
- b. Yes, marked expired — the history stays complete, at the cost of a list that grows without bound.

*My recommendation: a* — nobody has asked for export history.

### Declarations

D3. The 404 page carries the generic "this link has expired" copy the site already uses.
```

A blank line separates questions; one declaration per line, packed tight.

Every question, a yes/no one included, opens with an **explainer** — one to three sentences saying what the question is about and what rides on the answer, written for someone who has never seen the thing you are asking about. It sets the question up and stops there.

Letter the options where the choice is closed, one per line, each ending with what it costs, and mark your pick twice: `← recommended` on the option, and a `*My recommendation:*` line carrying the reason. An open question has nothing to letter, so it gets the recommendation line alone, as Q2 does. I answer by letter: `Q1: b`.

`Q` and `D` run continuously across the whole session, so round 2 picks up where round 1 stopped; option letters restart at `a` on every question. The `D` prefix marks a line as mine to skim rather than answer. Declare only in the rounds that decided something worth stating, one line where one line does it.

A round is read at speed, often late in a long day of them. Run the `/plain-language` skill before round 1 and hold its bar for every round after — it binds how each question is worded, never how hard it presses.

## Done

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Prove it with a **read-back** (the settled design, restated): plain sentences walking every surface and case the change touches, so that each meets a decision that applies to it. A surface no decision fits is a frontier item — ask it as a round, not in the read-back. The read-back carries no questions and no new declarations, names the Ideas filed along the way, and ends by asking whether we have reached a shared understanding. Act on the plan — spec, ADR, code — only after that answer; a forecast in an earlier round is not it.

A session I stop before the frontier is empty still leaves a record: write every settled decision and unanswered Question back to the document we started from, or to a new Idea when there was none, and commit it.
