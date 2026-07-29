---
name: grilling
description: Grill the user relentlessly about a plan or design, round by round. Use when the user wants to stress-test a plan before building, or uses any 'grill' trigger phrases.
---

Grill me relentlessly until we reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled — the questions you can ask *now* without guessing at answers you haven't heard yet. Ask the whole frontier in one round, however large that is, then wait for my answers.

My answers reshape the tree. Recompute the frontier before each round: a question that depends on another still open belongs to a *later* round.

## Facts, decisions, declarations

Finding *facts* is your job, never mine. When a frontier question needs a fact from the environment (filesystem, tools, etc.), dispatch a sub-agent and block on it — a running exploration is an unsettled prerequisite.

A question with one defensible answer is a fact too. Reason it out and state it as a **declaration**. Reserve **questions** for genuine *decisions*, on one test: would a different answer visibly change what gets built? When both answers land in the same place, pick one and move on without mentioning it.

Silence is consent — a declaration I say nothing about stands. An objection reshapes the tree exactly like an answer to a question.

## Altitude

Open round 1 by naming the **subject** on one line — `Subject: functional (correct me if not)` — and leave it there unless it changes, in which case say so and why. When a subject is genuinely mixed, classify by where *my* judgement is needed rather than by which half is bigger.

The subject sets the **altitude** you grill at:

- **Functional** — grill high: what we are trying to achieve, how it should behave, what happens at the edges. Technology, structure, and test strategy are yours to settle from precedent already in the codebase, stated as declarations.
- **Technical** — grill low, into the detail. Get there by way of the functional goal, which is clear enough once you could hold up a candidate option and say whether it serves that goal. Until then, keep grilling high.

Testing is a question only when testing is itself the subject; elsewhere, a declaration.

## The shape of a round

Hold this format every session:

```
Subject: functional (correct me if not)          ← round 1 only

## Round 1

1. **The question, in bold, on one line.**
   One or two lines of context — the trade-off, what each answer costs.
   *My recommendation:* your pick, with the reason in a clause.

2. **The next question.**
   ...

### Declarations

D1. The decision, stated flat, one line where one line does it.
D2. ...
```

Both sequences run continuously across the whole session, so round 2 picks up where round 1 stopped. The `D` prefix marks a line as mine to skim rather than answer. Declare only in the rounds that decided something worth stating.

## Raising altitude

When I accept every recommendation in a round verbatim, or show any sign of annoyance, offer to raise the altitude: one line naming what you would stop asking about and turn into declarations, which I can decline.

Raising altitude means fewer and broader questions. It bottoms out at the functional decisions — those stay questions however much I agree with you, because they are the ones only I can answer. When I ask for more detail, drop the altitude again.

## Done

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Wait for my confirmation that we have reached a shared understanding before acting on the plan.
