---
name: grilling
description: Grill the user relentlessly about a plan or design, round by round. A Library skill other skills read by path.
disable-model-invocation: true
user-invocable: false
---

Grill me relentlessly until we reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled — the questions you can ask *now* without guessing at answers you haven't heard yet. Ask the whole frontier in one round, however large that is, then wait for my answers.

My answers reshape the tree. Recompute the frontier before each round.

## Facts, decisions, declarations

Finding *facts* is your job, never mine — and it is a sub-agent's job, never your own context's ([ADR-0027](../../docs/adr/0027-grilling-facts-come-from-explorers.md)):

- Read `CONTEXT.md`, the ADRs, and the brief we start from yourself, an Issue's comments included; every fact from the code arrives as an **explorer**'s report (a `skills:explorer`, a read-only sub-agent, sent with named questions).
- Dispatch the explorer with the questions it must answer, wait for it however long that takes, and carry its report rather than the files. A running exploration is an unsettled prerequisite, and a round posted before it lands is built on guesses.
- Scope needs no facts from the code, so round 1 may go out while explorers run when it asks only scope.
- Before a declaration or question that changes what a page lets a person do — drops, adds, or restricts a field, control, or action — the explorer's questions include that page's markup: the controls it renders, not only what the code behind it stores or accepts. A report that covers only the code behind the page leaves that declaration unsettled.
- A report that lands after a round is posted waits silently for the next round.
- Before a declaration or question that changes code that looks deliberate, such as a guard, a limit, a workaround, or an odd special case, with nothing read so far saying why it is there, run the `/why` skill on that code. Its Preserve, Change, Avoid, and Risk lists settle facts, and a reason it could not find is a question for me.
- A fact only I hold — who the contracting party is, what a price should be — is a question, with a line saying why you could not find it.

A question with one defensible answer is a fact too. Reason it out and state it as a **declaration**. Reserve **questions** for genuine *decisions*, on two tests: would a different answer visibly change what gets built, and would a reasonable owner of this codebase pick the other option? An option you cannot write a cost for, or one the codebase already settles by precedent, is not an option, and the question is a declaration. When both answers land in the same place, pick one and move on without mentioning it.

When every option you can offer fails the goal we opened with, the question is not a decision. Name the prerequisite that blocks it as a declaration and ask one thing: widen scope to cover it, file it as an Issue in `needs-grilling` and stop, or accept the shortfall.

Silence is consent — a declaration I say nothing about stands. An objection reshapes the tree exactly like an answer to a question.

Issues live in the repo's **Tracker**: carry out each operation on one — file, read, list, rewrite, set status, comment, link, close — as `.agents/refs/tracker.md` says, or as [setup/LOCAL.md](../setup/LOCAL.md) says when the repo has no ref.

## Altitude

Open round 1 by naming the **subject** on one line — `Subject: functional (correct me if not)`. Print it again only in the round where it changes, with one line saying why. When a subject is genuinely mixed, classify by where *my* judgement is needed rather than by which half is bigger. An Issue with no user-visible change — a refactor, a flag removal — is `technical` from round 1.

The subject sets the **altitude** you grill at:

- **Functional** — grill high: what we are trying to achieve, how it should behave, what happens at the edges. Technology and structure are yours to settle from precedent already in the codebase, stated as declarations.
- **Technical** — grill low, into the detail. Get there by way of the functional goal, which is clear enough once you could hold up a candidate option and say whether it serves that goal. Until then, keep grilling high.

The size of the change sets where you start, and most sessions are one change to a system that already works — so start high. Grill **scope** before anything else: what this change covers, and what it leaves alone.

- When my request already draws the scope, restate it as a declaration and offer nothing smaller.
- When the request is open-ended, the scope question is round 1 on its own, because every other question hangs off its answer.
- When the session starts from a written brief, such as an Issue, D1 is your reading of it in your own words, including what you took from it as settled. Where the brief reads two ways that change what gets built, that is Q1, and the rest of the round waits.

Once scope is settled, ride what already exists and aim for the smallest change that does the work — an edge case the existing code already handles is a declaration, and so is an obvious refactor on the way. When the design names a change, recommend by the **Planning principles** in [to-spec/PRINCIPLES.md](../to-spec/PRINCIPLES.md), which the Spec will be held to. Where the smallest build would leave the person a worse experience than a wider one, that is a question. The smallest change is the default recommendation, not a position: when I choose a wider option than you recommended, or say the architecture is the point, recommend at that width for the rest of the session. A branch we cut as out of scope but still want is filed as an Issue in `needs-grilling`, with the sections `/validate-spec` checks on a `needs-grilling` Issue, and named in a declaration.

A question about what a screen should look like is a `/prototype` question, and so is a design with no precedent in the codebase. Settle scope and behaviour, then run `/prototype` on it and carry its verdict back as declarations; copy, placement, and format wait for the prototype when one is coming.

Testing is a question only when testing is itself the subject; elsewhere, a declaration.

When I accept every recommendation in a round verbatim, or show any sign of annoyance, raise the altitude — one line naming what you are turning into declarations, which I can decline.

Raising altitude means fewer and broader questions. It bottoms out at the functional decisions — those stay questions however much I agree with you, because they are the ones only I can answer. When I ask for more detail, drop the altitude again.

## The shape of a round

Hold this format every session:

```
Subject: functional (correct me if not)

## Round 1

Q1. **Should an expired export be deleted?**

An export is a file we generate on request and keep for a while. This decides what someone sees when they open the link after that window closes.

*My recommendation:* yes, delete it on expiry. Storage stays flat, and the bookmarked-link case is rare enough to answer with a generic 404.

---

Q2. **Should we call the window an export stays valid for `retention`?**

This name goes into the schema, the API, and the screen, so it is expensive to change later. Proposed meaning: the time from generation until the file is deleted.

| Scenario | Is it the retention? |
|---|---|
| Link opened on day 3 of a 7-day window | Inside it |
| Link opened on day 8 | Outside it; the export is gone |
| Owner deletes the export on day 2 | Ends it early; the window itself is unchanged |

*My recommendation:* yes, `retention`, since that is the word the storage layer already uses.

### Declarations

D1. Exports go to the object store already behind the reports feature.
D2. Retention is one fixed window for every user.
```

Round 2 continues the numbering. Q3 has a small closed set of answers, so it is lettered:

```
## Round 2

Q3. **What does the download page show for an expired export?**

The download page lists past exports. This decides whether an expired one still appears there.

- a. Nothing. The list shows only what can be downloaded, so an expired export vanishes without trace. ← recommended
- b. A row marked expired, with the link disabled. The history stays complete, at the cost of a list that grows without bound.
- c. A row marked expired, with a "generate again" button. It helps most, at the cost of a new action and endpoint.

*My recommendation: a*, because nobody has asked for export history.

### Declarations

D3. The 404 page carries the generic "this link has expired" copy the site already uses.
```

A line holding `---`, with a blank line above and below, separates one question from the next, and `### Declarations` follows the last question directly. One declaration per line, packed tight.

Every question, a yes/no one included, opens with an **explainer** — one to three sentences saying what the question is about and what rides on the answer, written for someone who has never seen the thing you are asking about. It sets the question up and stops there.

**Scenario-test** every term: a question that defines or names one follows its explainer with a **scenario table** — one row per situation the term would be used in, at least one on the boundary, each row showing how the term reads there. A closed question's table gains a column per option.

Ask a question open by default: in prose, with the `*My recommendation:*` line alone, as Q1 and Q2 do. Word it so "yes" accepts your recommendation. Letter the options only where the answers are a small closed set you could name before I answered, as Q3 does: one option per line, each ending with what it costs, and your pick marked twice, with `← recommended` on the option and a `*My recommendation:*` line carrying the reason. I answer a lettered question by letter: `Q3: b`.

Before round 1, read every **Grilling profile** in `.agents/refs/profiles/`: mine is the one whose `Email:` line lists `git config user.email`, else the one named after `git config user.name` in kebab case; the rest are my team. Only their `## Habits` count. Where one of my **Habits** applies to a closed question, recommend the option it points to, with a `*Your habit:*` line above the recommendation line naming that Habit; when you hold a different pick against it, keep yours and say why on that line. Name each person whose Habit applies, by first name, on the option it points to — `← recommended, Ana, Ben`, `← Chen` — me included; a teammate gets the name and no line. An open question carries no names. A Habit moves a recommendation and never turns a question into a declaration, and my picks in this session outrank my profile. With no profiles, or no email, rounds run as above with no names.

`Q` and `D` run continuously across the whole session, so round 2 picks up where round 1 stopped; option letters restart at `a` on every question. The `D` prefix marks a line as mine to skim rather than answer. Declare only in the rounds that decided something worth stating, one line where one line does it.

A round is read at speed, often late in a long day of them. Before round 1, read [`technical-writing/SKILL.md`](../technical-writing/SKILL.md) and follow it — `/technical-writing` does not load as a skill — and hold its bar for every round after. It binds how each question is worded, never how hard it presses.

## Done

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Prove it with a **read-back** (the settled design, restated): plain sentences walking every surface and case the change touches, so that each meets a decision that applies to it. A surface no decision fits is a frontier item — ask it as a round, not in the read-back. The read-back carries no questions and no new declarations, names the Issues filed along the way, and ends by asking whether we have reached a shared understanding. Only after that answer: a change to implement becomes a Spec; a settled design that nothing will be built writes no Spec. A forecast in an earlier round is not confirmation.

A session I stop before the frontier is empty still leaves a record: rewrite the body of the Issue we started from to add every settled decision and unanswered Question, or file them as a new Issue in `needs-grilling` when there was none, and commit.
