# mvdmio Skills

A collection of software-engineering skills for Claude Code, distributed as a plugin. This context covers the vocabulary the skills use to talk about the documents they read and write, and about each other.

## Language

### Work documents

**Idea**:
A loose, untriaged thought captured at `.agents/ideas/<slug>.md`. Not yet shaped into anything actionable.

**Refinement**:
The description of a change's **Scope** agreed by Product, QA, and Development in a `/refine` session — what is part of this project and what is not — written so a developer can start a `/grill-with-docs` session from it. Deliberately silent on implementation. Lives in a folder of its own at `.agents/refinements/<slug>/`, holding a Session document, a Complete document, and a Prototype when the room used one. Terminal: nothing consumes it automatically.
_Avoid_: functional spec, requirements doc, BRD

**Scope**:
What a `/refine` session determines: what is part of this project and what is not.
_Avoid_: work items, backlog, requirements

**Session document**:
The Refinement a `/refine` session writes as it runs, at `.agents/refinements/<slug>/session.md`. Resume infrastructure, not user-facing: intent, the full read-from-code account of today (including code anchors), in scope, out of scope, the Prototype path, parked questions. It survives the close, so a settled change can be reopened without re-deriving today.

**Complete document**:
The Refinement a `/refine` session signs off, at `.agents/refinements/<slug>/complete.md`. Six fixed sections — Intent, How it works today, In scope, Out of scope, Prototype, Open Questions — every one always present, carrying `None` where the session settled nothing. Synthesised from the Session document rather than renamed out of it, user-facing, and the thing written back to the Jira ticket or markdown file the session started from. How it works today is behaviour; the code walkthrough stays only in the Session document.

**Buildable**:
A proposed change whose Solution is clear enough that `/implement` can start without a further grilling session. `/triage` and `/improve-codebase-architecture` write a Spec only when the change is Buildable.
_Avoid_: ready, agent-ready, clear solution

**Architecture review**:
The output of an `/improve-codebase-architecture` run at `.agents/architecture-reviews/<timestamp>/`, holding `report.md` and the `report.html` rendered from it — deepening candidates, each carrying what the functionality it touches does. Read with a team who work on different parts of the system; after the report, the session says which candidates are Buildable, then picked candidates become Ideas, or Specs when Buildable.
_Avoid_: codebase audit, audit, tech-debt report, architecture report

**Codebase audit**:
The output of a `/codebase-audit` run at `.agents/codebase-audits/<timestamp>/`, holding `report.md` — a coverage-complete, read-only inventory of every identifiable subsystem, each with organizing-model recommendations or an explicit skip.
_Avoid_: architecture review, tech-debt report, DSA audit

**Prototype**:
Throwaway code built to answer one design question — whether a state model holds up once pushed through real cases, or what a screen should look like. A **Spec** points at `.agents/prototypes/<slug>/`. A **Refinement** keeps its Prototype at `.agents/refinements/<slug>/prototype/`.
_Avoid_: spike, POC, demo, mockup

**Spec**:
The approved description of a feature at `.agents/specs/<slug>.md` — problem, solution, user stories, implementation and testing decisions. The input to `/implement` and `/implement-oneshot`.
_Avoid_: PRD, plan, design doc

**Unstated claim**:
A claim a Spec treats as settled that it never states as a decision and that the code does not establish as fact.
_Avoid_: assumption

**Step**:
One implementation slice of a Spec, at `.agents/steps/<spec-slug>/<NN>-<slug>.md`. A tracer bullet: a narrow but complete path through every layer, sized to one fresh agent context, verifiable on its own. Steps exist only for the duration of an `/implement` run and are deleted with the Spec they came from.
_Avoid_: ticket, task, chunk, phase

**Decision ticket** (everyday: **ticket**):
A file on a `/wayfinder` map at `.agents/issues/<effort>/<NN>-<slug>.md` whose resolution is a decision — not a slice of a build to execute. The unit of claim and resolution. Distinct from a Step, which delivers code and decides nothing.
_Avoid_: investigation ticket, implementation ticket

**Fork**:
A place a `/wayfinder` effort could go two ways, and the one it takes changes what gets built. What the map charts.

**Focused**:
A grilling **Decision ticket** whose **Fork** is a tree: more than one question already nameable, or one-question forks that block each other.

**Small questions**:
A grilling **Decision ticket** that holds leftover unblocked one-question **Forks**, even when the subjects differ. The heading is Small questions.
_Avoid_: leftovers ticket, bundle, grab-bag

**Issue**:
An incoming request moving through the `/triage` state machine, at `.agents/issues/<slug>/<NN>-<slug>.md`, one file per distinct problem, carrying `Category:` and `Status:` lines. A Buildable issue ends as a **Spec** and that issue file is deleted; surviving states are `needs-info`, `needs-human`, and `needs-grilling`; rejected or already-implemented work is not kept as a document.

**Map**:
The index of a `/wayfinder` effort at `.agents/issues/<effort>/map.md` — Destination, Notes, Decisions so far, fog. Every Map ends in a Spec, so its Destination names the change that Spec will cover rather than which artifact the effort produces.

**Changelog**:
The product-facing history of a context, at `CHANGELOG.md` beside that context's `CONTEXT.md` (one file per context in a multi-context repo). Newest **Changelog entry** at the top. Written for people who use the product, not for people who build it.
_Avoid_: release notes, Keep a Changelog, commit log, NEWS

**Changelog entry**:
One shipped, product-visible change recorded in a Changelog: a dated title of at most six words and a body of at most three sentences, in **Plain language** with no development jargon. One entry per `/implement` or `/implement-oneshot` run per context that changed; backfill groups git history into the same shape by logical product feature, not by merge commit.
_Avoid_: release bullet, commit message, patch note

### Communication

**Plain language**:
Writing pitched at a reader who does not know this repo, in the sense of ISO 24495-1:2023. The standard every piece of text a skill puts in front of a person is held to.
_Avoid_: simple English, simplified language, readability

**Definition site**:
Text whose job is to fix the meaning of a term — a `CONTEXT.md` entry, a glossary heading, an ADR passage that coins a name. The one place precision outranks **Plain language**, because careful words paid once are what make the shorthand safe to use everywhere else.
_Avoid_: definition block, glossary entry

**Gloss**:
The plain-words introduction a skill gives its own vocabulary the first time that vocabulary appears — "the frontier (the questions I can ask now)". What buys a skill the right to use a term it defined rather than spelling the idea out every time.
_Avoid_: definition, footnote, explainer, aside

### Sessions

**Driving session**:
The main agent session a user invokes a skill in. It orchestrates and holds the low-resolution view; it delegates detail work to sub-agents so its context stays small.

**Design tree**:
The shape a `/grilling` session maps: every decision branching into the decisions that hang off it.

**Round**:
One batch of questions a Driving session puts to the user at once, covering the whole frontier, followed by a wait for answers.

**Frontier**:
Every decision on the Design tree whose prerequisites are already settled — what a Round can ask without guessing at answers it hasn't heard. An empty frontier ends the session.

**Question**:
A frontier item with more than one defensible answer, where a different answer visibly changes what gets built. Numbered `Q1`, `Q2` continuously across a session; options within one lettered `a`, `b`, `c`.
_Avoid_: open question — that is a parked item on a Refinement, not a live Question

**Explainer**:
The one to three sentences opening every Question, saying what the question is about and what rides on the answer. Written for someone who has never seen the thing being asked about. Distinct from a **Gloss**, which introduces a skill's own vocabulary rather than the subject matter.
_Avoid_: framing sentence, preamble, context

**Declaration**:
A frontier item with one defensible answer, reasoned out and stated flat rather than asked. Numbered `D1`, `D2` continuously across a session, one per line; silence accepts it.
_Avoid_: assumption

**Orientation**:
The one to three plain sentences that open round 1 of a `/grilling` session, naming what is being grilled so a reader who landed on the tab cold among several can place it. Round 1 only.
_Avoid_: summary, preamble, blurb, lede

**Read-back**:
The closing round of a `/grilling` session once the Frontier is empty: the settled design restated in plain sentences, walking every surface and case the change touches, with no Questions and no new Declarations, ending in the ask for confirmation that we have reached a shared understanding. No Spec, ADR, or code is written before that confirmation.
_Avoid_: recap, summary, closing round, confirmation round

**Explorer**:
The read-only sub-agent (`skills:explorer`) a Driving session dispatches with named fact questions about the code. The session carries its report, never the files it read.
_Avoid_: scout, researcher, background reader

**Subject**:
The altitude a `/grilling` session grills at, named on one line in its first Round and classified `functional` or `technical` by where the user's judgement is needed rather than by which half is bigger.

**Altitude**:
How deep a Round grills, set by the Subject. Raised by turning Questions into Declarations, lowered when the user asks for detail. It bottoms out at the functional decisions, which stay Questions however high it goes.

**Docs pass**:
The background exploration that opens a `/refine` session — `CONTEXT.md`, the ADRs, and recent git history, read before any code. Cheap enough to land while round 1 is still being answered.

**Code walk**:
The background exploration of the affected code in a `/refine` session, aimed by the intent the room settled in round 1. It confirms or corrects what the Docs pass wrote.

**Room's clock**:
The scarce resource in a `/refine` session: an idle minute costs as many minutes as there are people in the call. What justifies reading in the background, and stopping the room only for the Prototype and the closing read-back.

**Retrospective**:
Suggestions for the agent's environment after a session. **High-priority** suggestions are applied without asking; the rest appear only in the summary. A **Named session skill** starts one when it finishes; you can also type `/retro`.
_Avoid_: postmortem, wrap-up, retro as a meeting

**Named session skill**:
A user-typed skill that starts a **Retrospective** when it finishes.
_Avoid_: host skill, wrapping skill, parent skill

**High-priority**:
A **Retrospective** suggestion whose pain will recur every turn or every session. Includes a judgement-call coding standard and a new check when this session demonstrated them.
_Avoid_: mechanical-only, severity

### Execution

**Planner**:
The sub-agent that reads a Spec, walks the code only until every Step's Footprint can be filled, and writes the Step files — each with that Footprint and the Steps it is blocked by. It closes leftover behaviour the Spec did not name, commits the files in one commit, and returns only a compact index to the Driving session — never the Step bodies.

**Ready**:
A pending Step whose `Blocked by` Steps are all done. What `/implement` dispatches now; several Ready Steps run together.
_Avoid_: frontier — that is grilling's word for questions whose prerequisites are settled

**Step agent**:
The sub-agent that implements exactly one Step, in its own worktree. Reads the Outcomes of Steps already done, closes any gap in the Spec or Step from the code and existing patterns, leaves its Footprint's projects green, commits, and returns a fixed three-line report.

**Oneshot agent**:
The Spec-bound sub-agent that implements a whole Spec in one session — no Planner, no Step files. Dispatched by `/implement-oneshot`.
_Avoid_: direct implementer, oneshot implementer, single-session agent, implement-direct

**Footprint**:
The section of a Step file naming where that Step's work lands — the files it is expected to touch, the symbols inside them that matter, and the projects that must be green when it finishes. Written by the Planner from the codebase walk it does anyway, and read by the Step agent as a starting point rather than a contract: where the code and the Footprint disagree the code wins, and the Step agent records the drift in its Outcome. Its list of projects also fixes how much test suite that Step runs.
_Avoid_: entry map, landing, touch list, blast radius — the last is a property of a Wide refactor, not of a Step

**Green**:
Zero failures in the projects a Step's Footprint names, or in the projects an Oneshot agent found in the codebase, plus any verification the repo's conventions demand for the surface touched, measured against `master`: a failure that also fails on `master` at the merge-base is a Deviation to report, not the run's to fix, and does not block landing.
_Avoid_: passing, all tests pass, mostly green

**Outcome**:
The section a Step agent appends to its own Step file, recording what it built and where its Footprint proved wrong. The channel by which a Step agent informs its successors, bypassing the Driving session's context entirely.

**Deviation**:
Anything a Step agent or Oneshot agent did that contradicts the Spec or changes what a later Step must do, and any failure it left red because `master` already fails it. The one piece of a run's detail the Driving session does carry forward.

**Spec-bound dispatch**:
A sub-agent whose assignment is a document decided before it was dispatched — a Spec, a Step, a research question. It runs at reduced effort because the scope of the work was already settled. Its opposite carries design or review judgement and is dispatched at the Driving session's own settings.
_Avoid_: cheap agent, worker, low-tier agent

**Provisional today**:
A `How it works today` written from the Docs pass and not yet confirmed by the Code walk, labelled as such in the Session document — documents lag code. The Complete document is written after the Code walk lands, so it can never carry one.

**Tracer bullet**:
A vertical slice that cuts a narrow but complete path through every layer (schema, API, UI, tests), rather than a horizontal slice of one layer. The shape every Step takes.

**Wide refactor**:
One mechanical change whose blast radius fans across the codebase, so a single edit breaks call sites everywhere and no tracer bullet can land green. Sequenced as expand–contract instead of sliced vertically.
