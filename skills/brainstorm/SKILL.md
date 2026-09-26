---
name: brainstorm
description: Explore a vague problem as very different Directions, side by side, and write the ones you keep as Ideas.
disable-model-invocation: true
argument-hint: "<problem or idea path>"
---

# Brainstorm

Turn a vague problem into Ideas by **diverging** first: lay out very different **Directions** side by side, each from its own angle, so the set spreads rather than clusters around the first thought.

The input is the problem in plain words, or the path to an Idea still too loose to grill. Read `CONTEXT.md` and the ADRs covering the area yourself.

The run's only documents are Ideas ([ADR-0035](../../docs/adr/0035-architecture-reviews-end-in-ideas-and-specs.md)). Specs, ADRs, and the next session belong to the user: point them at `/grill-with-docs` or `/refine` on a kept Direction, and leave the typing to them.

Run the `/plain-language` skill before the first message and hold its bar for the opening, every card, and the closing pick. Every Idea holds its durable-document bar. The briefs you send helper agents are for agents and sit outside that bar.

## Process

### 1. Map the code

Dispatch one `skills:explorer` with named questions: which parts of the code the problem touches, what they do today, and what limits them. Carry its report, never the files ([ADR-0027](../../docs/adr/0027-grilling-facts-come-from-explorers.md)); every fact from the code arrives through it, for the whole run. When the problem touches no code in this repository, the report says so and the run goes on.

Done when the report has landed.

### 2. Frame

Write your **reading** of the problem in your own words, the **constraints** you take as fixed, and the four **angles** you will explore from:

- **How are other people solving this?** — in every set, every pass. Its agent must search the web and name real tools and techniques that exist today.
- Three more, picked for this problem from the starter list — smallest change to what exists, build it the ideal way from scratch, reframe or avoid the problem, borrow from another field — or a problem-specific angle of your own where it gives a wider spread.

When the problem reads two ways that would lead to different Directions, ask that one question and wait. Otherwise go straight on: the user corrects the reading by replying to the set.

Done when every angle is named and no reading that would change the Directions is left open.

### 3. Fan out

Dispatch one general-purpose sub-agent per angle, all in parallel, on your own model and effort. Each brief carries the problem, the constraints, the explorer report, its angle, and this instruction: produce one Direction that differs as much as possible from the obvious answer, unbound by what the code does today. Any agent may search the web when its Direction depends on an outside tool or technique, and names what it found as sources.

Each agent returns one **card**:

- **Pitch** — the Direction in one or two sentences.
- **How it works**
- **What it costs**
- **Best at**
- **Biggest risk**
- **Sources** — links, when the agent used any.

Done when every agent has returned its card.

### 4. Present the set

In one message: your reading, the constraints, the angles (on the first set only, or when they change), then the cards side by side, numbered continuously across the run so "go deeper on 2" names one card. Say in plain words, the first time, what a Direction and an angle are. Close with **your pick** and the reason. Be opinionated — the user wants a strong read, not a menu.

End by naming the moves: keep one or more Directions, go deeper on one, combine two, widen with more angles, or stop.

Done when every card is shown and the pick carries its reason.

### 5. Loop

The user's reply picks the move:

- **Deeper, combined, or wider** — write the tighter brief and go back to step 3 with fresh agents.
- **A correction** to the reading or constraints — reframe, then go back to step 3 with fresh agents.
- **Keep** — go to step 6 with the kept Directions.
- **Stop** without a pick — go to step 6 with none kept.

Every pass reuses the first explorer report.

Done when the user has kept Directions or stopped.

### 6. Write the Ideas

Each kept Direction becomes its own Idea at `.agents/ideas/<slug>.md`, the slug kebab-case from its title. Starting from an Idea, the kept Direction with the lowest card number overwrites that Idea's content under the same slug; every other kept Direction is a new Idea.

Fill the Idea sections `/validate-spec` checks, in prose about behaviour and reasons, under an H1 title:

- **Motivation** — the problem, why this Direction, and links to the outside sources it relies on.
- **Goal**
- **Decisions (locked)** — what the run settled about this Direction.
- **Out of scope** — every other Direction shown, each with the reason it was dropped.
- **Open questions** — the Direction's open points, where the next grilling session starts.

**Stopping without a pick** writes one Idea holding the problem: Motivation and Goal state the problem, Decisions (locked) holds the constraints you took as fixed, Out of scope says nothing is ruled out yet, and every Direction shown goes under Open questions. Starting from an Idea, add those Directions to its Open questions and keep the rest of its content.

Done when every kept Direction, or the stopped run, has its Idea on disk.

### 7. Close

Commit every Idea from the run in one commit, staged by name, on the branch you are on. Leave every other working-tree change alone.

List each Idea with the command that continues it: `/grill-with-docs` or `/refine`. Then run `/retro`.

Done when the commit exists, each Idea is listed with its next command, and `/retro` has finished.
