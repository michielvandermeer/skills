# mvdmio Skills

A collection of software-engineering skills for Claude Code, distributed as a plugin. This context covers the vocabulary the skills use to talk about the documents they read and write, and about each other.

## Language

### Work documents

**Idea**:
A loose, untriaged thought captured at `.agents/ideas/<slug>.md`. Not yet shaped into anything actionable.

**Refinement**:
The functional description of a change agreed by Product, QA, and Development in a `/refine` session — intent, use cases, and the delta against today, deliberately silent on implementation. Lives in a folder of its own at `.agents/refinements/<slug>/`, holding a Session document and a Complete document. Terminal: a Spec may be grilled out of it later, but nothing consumes it automatically.
_Avoid_: functional spec, requirements doc, BRD

**Session document**:
The Refinement a `/refine` session writes as it runs, at `.agents/refinements/<slug>/session.md`. Resume infrastructure, not user-facing: intent, the full read-from-code account of today (including code anchors), the delta, use cases, parked questions. It survives the close, so a settled change can be reopened without re-deriving today.

**Complete document**:
The Refinement a `/refine` session signs off, at `.agents/refinements/<slug>/complete.md`. Six fixed sections — Introduction, Open Questions, Use cases, Scope, Out-of-scope, Notes — every one always present, carrying `None` where the session settled nothing. Synthesised from the Session document rather than renamed out of it, user-facing, and the thing written back to a Jira ticket. Constraints of today land in Notes; the code walkthrough stays only in the Session document.

**Architecture review**:
The output of an `/improve-codebase-architecture` run at `.agents/architecture-reviews/<timestamp>/`, holding `report.md` and the `report.html` rendered from it — deepening candidates, each carrying what the functionality it touches does. Read with a team who work on different parts of the system, then grilled into a Spec with `/grill-with-docs`.
_Avoid_: audit, tech-debt report, architecture report

**Spec**:
The approved description of a feature at `.agents/specs/<slug>.md` — problem, solution, user stories, implementation and testing decisions. The input to `/implement`.
_Avoid_: PRD, plan, design doc

**Step**:
One implementation slice of a Spec, at `.agents/steps/<spec-slug>/<NN>-<slug>.md`. A tracer bullet: a narrow but complete path through every layer, sized to one fresh agent context, verifiable on its own. Steps exist only for the duration of an `/implement` run and are deleted with the Spec they came from.
_Avoid_: ticket, task, chunk, phase

**Ticket**:
An open question on a `/wayfinder` map, at `.agents/issues/<effort>/<NN>-<slug>.md`. A Ticket resolves a *decision*; it does not deliver code. Distinct from a Step, which delivers code and decides nothing.

**Issue**:
An incoming request moving through the `/triage` state machine, at `.agents/issues/<slug>/<NN>-<slug>.md`. Carries `Category:` and `Status:` lines.

**Map**:
The index of a `/wayfinder` effort at `.agents/issues/<effort>/map.md` — Destination, Notes, Decisions so far, fog.

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

**Declaration**:
A frontier item with one defensible answer, reasoned out and stated flat rather than asked. Numbered `D1`, `D2` continuously across a session, and silence accepts it.
_Avoid_: assumption

**Subject**:
What a session is about, named on one line in its first Round and classified `functional` or `technical` by where the user's judgement is needed rather than by which half is bigger.

**Altitude**:
How deep a Round grills, set by the Subject. Raised by turning Questions into Declarations, lowered when the user asks for detail. It bottoms out at the functional decisions, which stay Questions however high it goes.

**Docs pass**:
The background exploration that opens a `/refine` session — `CONTEXT.md`, the ADRs, and recent git history, read before any code. Cheap enough to land while round 1 is still being answered.

**Code walk**:
The background exploration of the affected code in a `/refine` session, aimed by the intent the room settled in round 1. It confirms or corrects what the Docs pass wrote.

**Room's clock**:
The scarce resource in a `/refine` session: an idle minute costs as many minutes as there are people in the call. What justifies reading in the background, batching code-dependent questions into one probe per round, and stopping the room only for the closing read-back.

### Execution

**Planner**:
The sub-agent that reads a Spec, explores the codebase, and writes the Step files. Returns only a compact index to the Driving session — never the Step bodies.

**Step agent**:
The sub-agent that implements exactly one Step. Reads the prior Steps' Outcomes itself, leaves the test suite green, commits, and returns a fixed three-line report.

**Outcome**:
The section a Step agent appends to its own Step file recording what it built. The channel by which a Step agent informs its successors, bypassing the Driving session's context entirely.

**Deviation**:
Anything a Step agent did that contradicts the Spec or changes what a later Step must do. The one piece of a Step's detail the Driving session does carry forward.

**Spec-bound dispatch**:
A sub-agent whose work is fully determined by a document decided before it was dispatched — a Spec, a Step, a research question. It exercises no judgement the document has not already settled, and so runs at reduced effort. Its opposite carries design or review judgement and is dispatched at the Driving session's own settings.
_Avoid_: cheap agent, worker, low-tier agent

**Provisional today**:
A `How it works today` written from the Docs pass and not yet confirmed by the Code walk, labelled as such in the Session document — documents lag code. The Complete document is written after the Code walk lands, so it can never carry one.

**Tracer bullet**:
A vertical slice that cuts a narrow but complete path through every layer (schema, API, UI, tests), rather than a horizontal slice of one layer. The shape every Step takes.

**Wide refactor**:
One mechanical change whose blast radius fans across the codebase, so a single edit breaks call sites everywhere and no tracer bullet can land green. Sequenced as expand–contract instead of sliced vertically.
