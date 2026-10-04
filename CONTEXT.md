# mvdmio Skills

A collection of software-engineering skills for Claude Code, distributed as a plugin. This context covers the vocabulary the skills use to talk about the documents they read and write, and about each other.

## Language

### Work documents

**Tracker**:
Where a repo keeps its Issues: local Markdown files in the repo, GitHub Issues, Jira, or any other system its **Tracker ref** describes. One per repo. A repo with no Tracker ref uses the local Markdown **Tracker template** as shipped.
_Avoid_: issue tracker, ticketing system, backlog

**Tracker ref**:
The repo's own description of its **Tracker**, at `.agents/refs/tracker.md`: which system it is, how each operation the skills name is carried out there, and which label or field holds each status. The repo owns it and may edit it freely; the skills follow it as written.
_Avoid_: issue-tracker.md, tracker config, tracker settings

**Tracker template**:
A starting **Tracker ref** the plugin ships for one system — local Markdown, GitHub Issues, or Jira — that `/setup` copies into a repo. Once copied it is the repo's own; later changes to the template do not reach it.
_Avoid_: baseline, preset, issue-tracker template

**Issue**:
One piece of work in the repo's **Tracker**, from a first rough thought to a finished **Spec**, carrying exactly one status: `needs-triage` (nobody has triaged it), `needs-info` (waiting on the reporter), `needs-grilling` (a person must decide the solution), `needs-human` (waiting on a secret or a manual test), `wayfinding` (it is a **Map**), or `ready-for-agent` / `ready-for-human` (it carries a Spec, for an agent or a person to build). A `needs-` status means it waits on something; a `ready-for-` status means it carries a Spec. Moving from one stage to the next updates the same Issue; finished or rejected work is closed. `/triage` may also give it a `bug` or `enhancement` category.
_Avoid_: Idea, ticket, card, work item, PRD

**Scope**:
What a `/refine` session determines: what is part of this project and what is not.
_Avoid_: work items, backlog, requirements

**Buildable**:
A proposed change whose Solution is clear enough that `/implement` can start without a further grilling session. `/triage` and `/improve-codebase-architecture` write a Spec only when the change is Buildable.
_Avoid_: ready, agent-ready, clear solution

**Architecture review**:
The output of an `/improve-codebase-architecture` run at `.agents/architecture-reviews/<timestamp>/` (`.agents/architecture-reviews/<context>/<timestamp>/` in a multi-context repo), holding `report.md` and the `report.html` rendered from it — deepening candidates, each carrying what the functionality it touches does. Read with a team who work on different parts of the system; after the report, the session says which candidates are Buildable, then picked candidates become Issues in `needs-grilling`, or Specs when Buildable.
_Avoid_: codebase audit, audit, tech-debt report, architecture report

**Codebase audit**:
The output of a `/codebase-audit` run at `.agents/codebase-audits/<timestamp>/` (`.agents/codebase-audits/<context>/<timestamp>/` in a multi-context repo), holding `report.md` — a coverage-complete, read-only inventory of every identifiable subsystem, each with organizing-model recommendations or an explicit skip.
_Avoid_: architecture review, tech-debt report, DSA audit

**Prototype**:
Throwaway code built to answer one design question — whether a state model holds up once pushed through real cases, or what a screen should look like. A **Spec** points at `.agents/prototypes/<slug>/`, or `.agents/prototypes/<context>/<slug>/` in a multi-context repo.
_Avoid_: spike, POC, demo, mockup

**Wizard**:
A bash script that walks a person, stage by stage, through a manual procedure only they can perform. The `/wizard` skill generates it; the person runs it.
_Avoid_: setup script, HITL loop, installer, walkthrough

**Stage**:
One focused task in a Wizard, typically one screen.
_Avoid_: Step, prompt

**Spec**:
The body an **Issue** carries once its status is `ready-for-agent` or `ready-for-human` — problem, solution, user stories, implementation and testing decisions — replacing whatever the Issue said before. The input to `/implement`, `/implement-oneshot`, and `/implement-yolo`. Written only when there is a change to implement; its Issue is blocked by another Issue when that one must land first. Work we will not do is not a Spec.
_Avoid_: PRD, plan, design doc

**ADR**:
A decision in force and the reason it holds, at `docs/adr/<NNNN>-<slug>.md`, stated as things stand today. It carries no history: how the decision got here lives in git. An option once chosen and later dropped appears only as a rejected option with its reason, and only when someone might propose it again.
_Avoid_: decision log, superseded ADR, partially superseded ADR

**Chain**:
The set of ADRs that record one decision at different points in time — an older ADR marked superseded or partly superseded, or replaced in part by a newer ADR's body, together with the ADRs that replaced it. What a **Fold** merges.
_Avoid_: ADR history, supersession chain, lineage

**Fold**:
Merging the ADRs that record one decision at different times into a single ADR that states the decision as it stands, keeping the number of the newest.
_Avoid_: squash, consolidate, supersede

**Unstated claim**:
A claim a Spec treats as settled that it never states as a decision and that the code does not establish as fact.
_Avoid_: assumption

**Step**:
One implementation slice of a Spec, at `.agents/steps/<run-slug>/<NN>-<slug>.md`. A tracer bullet: a narrow but complete path through every layer, sized to one fresh agent context, verifiable on its own. Its `Status:` reads `pending` until its Step agent sets `built`, then `done` once its Checker finishes it. A run with no Planner — `/implement-oneshot` or `/implement-yolo` — has exactly one Step, the whole Spec, with no Footprint. Steps exist only for the duration of a run and are deleted when it lands.
_Avoid_: ticket, task, chunk, phase

**Decision ticket** (everyday: **ticket**):
A child of a **Map** in the **Tracker** whose resolution is a decision — not a slice of a build to execute. The unit of claim and resolution. Distinct from a Step, which delivers code and decides nothing.
_Avoid_: investigation ticket, implementation ticket

**Claimed**:
A Decision ticket a `/wayfinder` session holds through the **Tracker**'s claim. Concurrent `/wayfinder` sessions skip it. The claim stands until the ticket is resolved or the user clears it.
_Avoid_: in progress, locked, assigned, researching

**Fork**:
A place a `/wayfinder` effort could go two ways, and the one it takes changes what gets built. What the map charts.

**Focused**:
A grilling **Decision ticket** whose **Fork** is a tree: more than one question already nameable, or one-question forks that block each other.

**Small questions**:
A grilling **Decision ticket** that holds leftover unblocked one-question **Forks**, even when the subjects differ. Its title is Small questions.
_Avoid_: leftovers ticket, bundle, grab-bag

**Map**:
An **Issue** in status `wayfinding` whose body is the index of a `/wayfinder` effort — Destination, Notes, Decisions so far, fog — and whose children are its **Decision tickets**. Every Map ends in one or more Specs, so its Destination names the whole change those Specs will cover rather than which artifact the effort produces. How many Specs, and where one ends and the next begins, is decided only once no tickets remain — a ticket remains until it is resolved or ruled out of scope — and by a fresh `/wayfinder` session, not the one that resolved the last ticket: each Spec is a change that can land green and is worth shipping on its own, and one Spec may be blocked by another that must land first. The Map's own Issue becomes the first of those Specs; the rest are new Issues.

**Context subfolder**:
The folder level, named for one context or `common`, that sits right after the kind folder in a work document's path in a multi-context repo — the `billing` in `.agents/prototypes/billing/<slug>/`. Distinct from a context's own folder, the one holding its `CONTEXT.md`.
_Avoid_: context folder, app folder

**Common**:
The folder that stands where a context's name would in a work document's path, in a multi-context repo, when the work belongs to no single context: it spans two or more contexts, or it touches code no context owns. `.agents/prototypes/common/<slug>/`.
_Avoid_: shared, global, cross-app

**Changelog**:
The product-facing history of a context, at `CHANGELOG.md` beside that context's `CONTEXT.md` (one file per context in a multi-context repo). Newest **Changelog entry** at the top. Written for people who use the product, not for people who build it.
_Avoid_: release notes, Keep a Changelog, commit log, NEWS

**Changelog entry**:
One shipped, product-visible change recorded in a Changelog: a dated title of at most six words and a body of at most three sentences, in **Plain language** with no development jargon. One entry per `/implement`, `/implement-oneshot`, or `/implement-yolo` run per context that changed; backfill groups git history into the same shape by logical product feature, not by merge commit.
_Avoid_: release bullet, commit message, patch note

**Coding standards**:
A repo's own documents on how its code should be written — at `.agents/refs/` first, or a root-level `CODING_STANDARDS.md` or `CONTRIBUTING.md` when that is where the repo keeps them. Each repo writes its own rules; the skills name where to find them, never what they say. Distinct from `/code-review`'s smell baseline, which applies even when a repo documents nothing.
_Avoid_: style guide, conventions, coding-standards.md

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
_Avoid_: open question — that is a parked item, not a live Question

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

**Direction**:
One of the very different ways to tackle a vague problem that a `/brainstorm` run lays out side by side — a pitch, how it works, what it costs, what it is best at, and its biggest risk. Each comes from its own angle, so the set spreads rather than clusters. A Direction the user keeps becomes an Issue in `needs-grilling`; the rest are dropped with their reason. When the user stops without keeping one, none is dropped: every Direction shown goes to the Open questions of one Issue. Distinct from an option, which is one lettered answer inside a Question.
_Avoid_: option, approach, alternative, candidate

**Subject**:
The altitude a `/grilling` session grills at, named on one line in its first Round and classified `functional` or `technical` by where the user's judgement is needed rather than by which half is bigger.

**Altitude**:
How deep a Round grills, set by the Subject. Raised by turning Questions into Declarations, lowered when the user asks for detail. It bottoms out at the functional decisions, which stay Questions however high it goes.

**Owned file**:
A file this git repository contains in its working tree as its own file. Not a cached plugin copy, and not a file in the user config tree.
_Avoid_: in-scope file, workspace file

**Retrospective**:
Suggestions for the agent's environment after a session. **High-priority** suggestions for **Owned files** are applied without asking; everything else appears only in the summary, including suggestions for files this repository does not own. A **Named session skill** starts one when it finishes; you can also type `/retro`.
_Avoid_: postmortem, wrap-up, retro as a meeting

**Named session skill**:
A user-typed skill that starts a **Retrospective** when it finishes.
_Avoid_: host skill, wrapping skill, parent skill

**High-priority**:
A **Retrospective** suggestion whose pain will recur every turn or every session. Includes a judgement-call coding standard and a new check when this session demonstrated them, and the rule a **Correction** points to.
_Avoid_: mechanical-only, severity

**Correction**:
A change a session made to code, or to a **Run recipe**, that existed before that session started, where the session also shows the old code was wrong — the user said so, a bug was being fixed, a test failed, or a review flagged it. Code written earlier in the same session is not a Correction, however soon it was fixed; neither is a change that follows a changed requirement. Who wrote the old code, a person or an agent, does not matter. A **Retrospective** turns a Correction into a Coding standards rule only when the fix points to a pattern future code could repeat.
_Avoid_: fix, bugfix, regression

### Execution

**Planner**:
The sub-agent (`skills:planner`) that reads a Spec, walks the code only until every Step's Footprint can be filled, and writes the Step files — each with that Footprint and the earlier Steps whose Outcomes it needs, numbered in dependency order. It closes leftover behaviour the Spec did not name, commits the files in one commit, and returns only a compact index to the Driving session — never the Step bodies.
_Avoid_: Plan, Plan agent, host Plan

**Step agent**:
The sub-agent (`skills:implementer`) that implements exactly one Step, in the run's working tree, after the Step before it is done — under all three implement commands. Reads the Outcomes of the earlier Steps its Step depends on, closes any gap in the Spec or Step from the code and existing patterns, leaves the tests of its Footprint's projects passing, records its **Safety fact** and **Proof** in its Outcome, commits, and returns a fixed three-line report. The **Checker** finishes the Step from there.
_Avoid_: Oneshot agent, implementer

**Checker**:
The sub-agent (`skills:checker`) that finishes a Step once its Step agent has committed it. It re-runs the Step's **Proof**, raising it to the rung **Green** requires when it falls short, reviews the Step's commit on both axes, fixes every finding, returns the Step to **Green**, and folds its fixes into that commit. It starts from the Step file and the Step's diff, not from the Step agent's context, and it is what marks the Step done.
_Avoid_: verifier, step reviewer, finisher

**Validator**:
The sub-agent (`skills:validator`) that checks a Spec `/to-spec` has just drafted. It works from the draft's path, corrects facts in that file, and returns the report of corrections and open questions; `/to-spec` then writes the corrected Spec to its Issue in one update.
_Avoid_: spec checker, spec reviewer, linter

**Fixer**:
A `general-purpose` sub-agent the Driving session sends, at its own model and effort, to fix what a review or a build found. The final review of all three implement commands sends a **Spec fixer** with the Spec axis's findings, then a **Standards fixer** with the Standards axis's findings, each starting fresh, so no single fixer carries both axes. A red post-rebase build at land gets one fixer too.

**Footprint**:
The section of a Step file naming where that Step's work lands — the files it is expected to touch, the symbols inside them that matter, and the projects that must be green when it finishes. Written by the Planner from the codebase walk it does anyway, and read by the Step agent as a starting point rather than a contract: where the code and the Footprint disagree the code wins, and the Step agent records the drift in its Outcome. Its list of projects also fixes how much test suite that Step runs.
_Avoid_: entry map, landing, touch list, blast radius — the last is a property of a Wide refactor, not of a Step

**Base branch**:
The branch the session was on when an implement command started, read again on a resume. The run branches from it, is reviewed and measured Green against it, and lands back on it. It is the repository's default branch only when the session started there.
_Avoid_: master, main, default branch, trunk

**Green**:
Zero failures in the projects a Step's Footprint names, or in the whole suite for the last Step or a Step with no Footprint, plus a **Proof** of its **Safety fact** that the Checker re-ran — at rung 3 of the **Proof ladder**, or rung 4 when the change alters a running surface; a change to no code that runs needs none — measured against the **Base branch**: a failure that also fails on the Base branch at the merge-base is a Deviation to report, not the run's to fix, and does not block landing.
_Avoid_: passing, all tests pass, mostly green

**Outcome**:
The section a Step agent appends to its own Step file, recording what it built and where its Footprint proved wrong; the Checker adds to it when a fix changes something a later Step needs. The channel by which a Step informs the later Steps that depend on it, bypassing the Driving session's context entirely.

**Deviation**:
Anything a Step agent or Checker did that contradicts the Spec or changes what a later Step must do, any failure it left red because the Base branch already fails it, and any post-rebase failure that passed on the Driving session's re-run. The one piece of a run's detail the Driving session does carry forward.

**Spec-bound dispatch**:
A sub-agent whose assignment is a document decided before it was dispatched — a Spec, a Step, a research question. It runs at reduced effort because the scope of the work was already settled. Its opposite carries design or review judgement and is dispatched at the Driving session's own settings.
_Avoid_: cheap agent, worker, low-tier agent

**Tracer bullet**:
A vertical slice that cuts a narrow but complete path through every layer (schema, API, UI, tests), rather than a horizontal slice of one layer. The shape every Step takes.

**Wide refactor**:
One mechanical change whose blast radius fans across the codebase, so a single edit breaks call sites everywhere and no tracer bullet can land green. Sequenced as expand–contract instead of sliced vertically.

**Safety fact**:
The one fact a change is safe because of, stated so that it names what breaks if the fact is false. "It compiles" names nothing that breaks, so it is not a Safety fact. Recorded in an Outcome together with its rung on the **Proof ladder** and its **Proof**.
_Avoid_: safety claim, invariant, assumption

**Proof**:
The evidence for a **Safety fact** that a fresh agent re-ran and saw for itself: the command run, its exit code and an excerpt of its output, or a screenshot or transcript saved for the run. Output an agent quotes without that fresh re-run is not Proof.
_Avoid_: evidence, verification, test result

**Proof ladder**:
The scale that ranks how strongly a **Proof** shows its **Safety fact** holds, in four rungs: (1) stated, or read in the code, which is not Proof at all; (2) the existing tests pass; (3) a test or throwaway script calls the real code on the risky path and would fail if the fact were false; (4) reproduced in the running app through the **Run recipe**.
_Avoid_: evidence rung, confidence level, verification level

**Run recipe**:
The record, kept in the consuming repo, of how to launch its app, tell that it is ready, drive it, keep evidence from it, and clean up afterwards — runnable from a plain shell command on any host. It lives at `.agents/refs/run-recipe.md`; in a repo with a `CONTEXT-MAP.md`, each context with a running surface keeps its own under that context's folder. Written by the first agent that has to drive the app, and edited only when it steers an agent wrong.
_Avoid_: verify recipe, run skill, smoke script, test plan
