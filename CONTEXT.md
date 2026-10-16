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

**Models ref**:
The repo's own choice of the model and effort each of the plugin's agents runs at, at `.agents/refs/models.md`, with a pointer line in the repo's `CLAUDE.md` or `AGENTS.md`. A row overrides that agent's pin on every dispatch; an agent without a row runs at its pin. Skills keep their own pins. Written and changed by `/setup models`; a plain `/setup` writes it with every agent at its pin when it is missing.
_Avoid_: model config, model overrides, models sheet

**Issue**:
One piece of work in the repo's **Tracker**, from a first rough thought to a finished **Spec**, carrying exactly one status: `needs-triage` (nobody has triaged it), `needs-info` (waiting on the reporter), `needs-grilling` (a person must decide the solution), `needs-human` (waiting on a secret or a manual test), `wayfinding` (it is a **Map**), or `ready-for-agent` / `ready-for-human` (it carries a Spec, for an agent or a person to build). A `needs-` status means it waits on something; a `ready-for-` status means it carries a Spec. Moving from one stage to the next updates the same Issue; finished or rejected work is closed. `/triage` may also give it a `bug` or `enhancement` category.
_Avoid_: Idea, ticket, card, work item, PRD

**Buildable**:
A proposed change whose Solution is clear enough that `/implement` can start without a further grilling session. `/triage` writes a Spec only when the change is Buildable.
_Avoid_: ready, agent-ready, clear solution

**Prototype**:
Throwaway code built to answer one design question — whether a state model holds up once pushed through real cases, or what a screen should look like. A **Spec** points at `.agents/prototypes/<slug>/`, or `.agents/prototypes/<context>/<slug>/` in a multi-context repo.
_Avoid_: spike, POC, demo, mockup

**Hillclimb**:
One effort to push one measured number in one direction by trying changes one at a time and keeping each only when the measurement shows it helped and the tests still pass. It starts once the number, its target, a minimum number of **Attempts**, and any time limit are agreed, works in its own worktree, and ends by landing on the **Base branch**. Hillclimbs on the same number share one folder at `.agents/hillclimbs/<slug>/` (`.agents/hillclimbs/<context>/<slug>/` in a multi-context repo).
_Avoid_: optimization run, perf drive, benchmark loop

**Attempt**:
One change a **Hillclimb** tries: a single idea, written by the **Climber**, measured against the commit before it, then kept as its own commit or reverted in full.
_Avoid_: iteration, experiment, trial

**Attempt log**:
The record of every **Attempt** on one measured number, in that number's **Hillclimb** folder beside its measurement script: one row per Attempt with its idea, its change, the number before and after, and whether it was kept or reverted. Committed and kept across Hillclimbs, so the reverted rows tell the next one which ideas are proven not to help.
_Avoid_: decision log (that is an ADR), decision.tsv, experiment log

**Spec**:
The body an **Issue** carries once its status is `ready-for-agent` or `ready-for-human` — problem, solution, **Hand checks**, user stories, implementation and testing decisions — replacing whatever the Issue said before. Its problem, solution, Hand checks, and user stories are written for the **Product reader**; the rest is written for a developer new to the repo. The input to `/implement`, held to the **Planning principles** so one run can build it with no one to ask. Written only when there is a change to implement; its Issue is blocked by another Issue when that one must land first. Work we will not do is not a Spec.
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

**Hand check**:
One check in a **Spec**'s How to Check It section: what a person does on the running product, and what they should see, written so a QA tester can follow it by hand. The **Verifier** runs every Hand check too, in each **Iteration** of an implement run. A Spec where nothing changes for a person has none, and says so.
_Avoid_: acceptance check, acceptance criterion, test case, manual test, QA script

**Unstated claim**:
A claim a Spec treats as settled that it never states as a decision and that the code does not establish as fact.
_Avoid_: assumption

**Decision ticket** (everyday: **ticket**):
A child of a **Map** in the **Tracker** whose resolution is a decision — not a slice of a build to execute. The unit of claim and resolution. Distinct from a Spec, which an implement run builds.
_Avoid_: investigation ticket, implementation ticket

**Claimed**:
An Issue a session holds through the **Tracker**'s claim: a Decision ticket a `/wayfinder` session holds, or the Issue an implement run builds. Concurrent sessions skip it, and an implement run on an Issue another user holds stops. The claim stands until the Issue is resolved or closed, or the user clears it.
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

**Coding standards**:
A repo's own documents on how its code should be written — at `.agents/refs/` first, or a root-level `CODING_STANDARDS.md` or `CONTRIBUTING.md` when that is where the repo keeps them. Each repo writes its own rules; the skills name where to find them, never what they say. Distinct from the **Design principles**, which apply even when a repo documents nothing.
_Avoid_: style guide, conventions, coding-standards.md

### Communication

**Writing bar**:
The standard every piece of text a skill puts in front of a person is held to, set by `/technical-writing`: pitched at a developer who does not know this repo, with no em dash, en dash, or semicolon, and none of the AI tells its `UNSLOP.md` lists.
_Avoid_: plain language, style guide, house style, readability

**Product reader**:
Someone who knows the product but not its code — a QA tester, a product owner. The reader of the part of a **Tracker** document that says what is wrong and what changes: a **Spec**'s problem, solution, **Hand checks**, and user stories, a `needs-` **Issue**'s motivation and goal, a **Map**'s Destination. That part names only what this reader sees on the product, in words `CONTEXT.md` defines; the rest of the document keeps the developer reader of the **Writing bar**.
_Avoid_: QA reader, business reader, non-technical reader, end user

**Definition site**:
Text whose job is to fix the meaning of a term — a `CONTEXT.md` entry, a glossary heading, an ADR passage that coins a name. The one place precision outranks the **Writing bar**, because careful words paid once are what make the shorthand safe to use everywhere else.
_Avoid_: definition block, glossary entry

**Gloss**:
The plain-words introduction a skill gives its own vocabulary the first time that vocabulary appears — "the frontier (the questions I can ask now)". What buys a skill the right to use a term it defined rather than spelling the idea out every time.
_Avoid_: definition, footnote, explainer, aside

**Explanation**:
What an `/explain` run makes: a written walkthrough or a diagram drawn with text characters in the chat, or a self-contained HTML page or narrated video in a temp folder outside any repo. Distinct from an **Explainer**, the opening sentences of a grilling **Question**.
_Avoid_: explainer, explainer video, visual

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

**Grilling profile**:
One person's **Habits** in one repo, learned only from their grilling sessions in that repo and kept there at `.agents/refs/profiles/<name>.md`, so it travels with git to everyone who works there. The same person may have different Habits in different repos. A grilling session reads every profile in the repo to predict which option each person would pick. A profile changes only when a person types `/learn-habits`.
_Avoid_: user profile, preferences, persona, agent memory

**Habit**:
A pattern in how one person answers grilling **Questions**, stated as a rule that names the kind of question it applies to — such as widening a change to every related area when asked where it should stop — with how many sessions support it and when it was last seen. A corrected fact about the domain is not a Habit; it belongs in the glossary or an ADR.
_Avoid_: preference, tendency, pattern, choice

**Owned file**:
A file this git repository contains in its working tree as its own file. Not a cached plugin copy, and not a file in the user config tree.
_Avoid_: in-scope file, workspace file

**Retrospective**:
Suggestions for the agent's environment after a session. **High-priority** suggestions for **Owned files** are applied without asking; everything else appears only in the summary, including suggestions for files this repository does not own. A **Named session skill** starts one when it finishes; you can also type `/retro`.
_Avoid_: postmortem, wrap-up, retro as a meeting

**Named session skill**:
A skill that starts a **Retrospective** when it finishes, unless another Named session skill started it. Most are typed by the user and cannot be loaded by the agent; `/hillclimb` also starts one when the agent loaded it.
_Avoid_: host skill, wrapping skill, parent skill

**High-priority**:
A **Retrospective** suggestion whose pain will recur every turn or every session. Includes a judgement-call coding standard and a new check when this session demonstrated them, and the rule a **Correction** points to.
_Avoid_: mechanical-only, severity

**Correction**:
A change a session made to code, or to a **Verify skill**, that existed before that session started, where the session also shows the old code was wrong — the user said so, a bug was being fixed, a test failed, or a review flagged it. Code written earlier in the same session is not a Correction, however soon it was fixed; neither is a change that follows a changed requirement. Who wrote the old code, a person or an agent, does not matter. A **Retrospective** turns a Correction into a Coding standards rule only when the fix points to a pattern future code could repeat.
_Avoid_: fix, bugfix, regression

### Execution

**Planner**:
The sub-agent (`skills:planner`) that starts an implement run: it walks the code, slices the Spec into **Steps** by `skills/implement/STEPS.md`, commits the Step files, and returns a one-line-per-Step index. It writes no code.
_Avoid_: slicer, architect

**Step**:
One slice of a Spec that a single fresh **Implementer** builds on an implement run's first **Iteration**, recorded as a file under `.agents/runs/<slug>/` with what to build, a **Footprint**, acceptance criteria, and, once built, an Outcome. Steps run in number order, and each reads the Outcomes of the Steps before it. Most Specs are one Step. Review and Verify judge all Steps together, never one alone.
_Avoid_: task, ticket, phase, slice

**Footprint**:
The **Planner**'s guess, in a **Step** file, at where that Step's work lands: the files, the symbols in them, and the projects that must stay green. The **Implementer** starts from it, and where the code disagrees, the code wins and the drift goes in the Step's Outcome.
_Avoid_: scope, file list

**Iteration**:
One pass of an implement run's loop over the whole Spec: Implement, then Review, then Verify. A Review finding ends the Iteration before Verify; a Verify finding ends it after. The next Iteration starts at Implement with those findings. The first Iteration's Implement builds the **Steps** in order; a later one's fixes the findings. A run lands when one Iteration passes both, and halts when its third does not.
_Avoid_: round (a grilling term), cycle, attempt (a Hillclimb term)

**Implementer**:
The sub-agent (`skills:implementer`) that does the Implement part of an **Iteration**, under `/implement`. On the first Iteration a fresh one builds each **Step**, appends its Outcome to the Step file, and marks it done; on each later Iteration one fresh Implementer fixes every Verify finding it was handed, and fixes or declines each Review finding, with a reason for each decline. It builds what it touched, runs the tests closest to its change, commits, and returns a fixed four-line report.
_Avoid_: Step agent, coder, worker

**Verifier**:
The sub-agent (`skills:verifier`) that does the Verify part of an **Iteration**: it reads the Spec against the diff, builds and runs the whole test suite, and runs the Spec's **Hand checks**, driving the app through the **Verify skill** when the change alters a running surface. It changes no code, and corrects the Verify skill only where the skill steered it wrong. It reports `passed`, or the findings that send the run back to Implement. The land dispatches a fresh one when a rebase brought in code the last one did not check.
_Avoid_: Checker, Prover, tester, QA agent

**Climber**:
The sub-agent (`skills:climber`) that writes one **Attempt** of a **Hillclimb**. It gets one idea, changes the code in the Hillclimb's worktree, builds, runs the tests nearest its change, and leaves the change uncommitted. The Driving session measures it and keeps or reverts it, so the Climber never judges its own change.
_Avoid_: attempt agent, hillclimber, worker

**Validator**:
The sub-agent (`skills:validator`) that checks a Spec `/to-spec` has just drafted. It works from the draft's path, corrects facts in that file, and returns the report of corrections and open questions; `/to-spec` then writes the corrected Spec to its Issue in one update.
_Avoid_: spec checker, spec reviewer, linter

**Reviewer**:
The sub-agent (`skills:reviewer`, pinned to Opus) that `/code-review` dispatches once per axis — Standards and Spec — in parallel, each starting fresh, or for one axis alone when the caller names it. An implement run's Review is the Standards axis alone. It reads the changes since the fixed point and reports findings; it fixes nothing.
_Avoid_: review agent, critic, review bot

**Design principles**:
The fixed set of judgement calls in `skills/code-review/PRINCIPLES.md` — boundary discipline, type system discipline, idempotent operations, and the rest — that the Standards axis of `/code-review` applies on top of a repo's **Coding standards**, even when a repo documents nothing. A documented repo standard always wins over a principle. The **Implementer** reads them before it writes code.
_Avoid_: smell baseline, best practices

**Planning principles**:
The fixed set of judgement calls in `skills/to-spec/PRINCIPLES.md` — leave the implementer nothing to ask, fit one run, experience first, explain the number, and the rest — that a **Spec** is held to. `/grilling` recommends by them, `/to-spec` writes to them, and the **Validator** reports a miss as an open question. Distinct from the **Design principles**, which judge code.
_Avoid_: process principles, spec rules

**Fixer**:
A `general-purpose` sub-agent a **Hillclimb**'s Driving session sends, at its own model and effort, to fix what its final review found: a **Spec fixer** with the Spec axis's findings, then a **Standards fixer** with the Standards axis's findings, each starting fresh. An implement run has no Fixer: the next **Iteration**'s **Implementer** fixes what the last one's Review or Verify found.

**Base branch**:
The branch the session was on when `/implement` started, read again on a resume. The run branches from it, is reviewed and verified against it, and lands back on it. It is the repository's default branch only when the session started there.
_Avoid_: master, main, default branch, trunk

**Landing commit**:
The one commit an implement run leaves on the **Base branch** when it lands: the whole run's change, named after what it does, carrying the Issue's closing reference. It replaces every commit the run made along the way — the Spec copy, the plan, each **Step**'s, and each Iteration's — so none of those stays on the Base branch, and it holds no run folder. A **Retrospective**'s commit, when there is one, follows it as a commit of its own.
_Avoid_: squash commit, land commit, cleanup commit, merge commit

**Green**:
Zero failures in the **Verifier**'s run of the whole test suite, measured against the **Base branch**: a failure that also fails on the Base branch at the merge-base is a Deviation to report, not the run's to fix, and does not block landing. A test that passes on the Verifier's one re-run is a flake, reported the same way.
_Avoid_: passing, all tests pass, mostly green

**Deviation**:
Anything an **Implementer** or **Verifier** reports that the Driving session carries forward without acting on: a contradiction with the Spec, a change a later **Step** must know about, a failure left red because the Base branch already fails it, a flaky test, a Hand check skipped for what it needs, a missing **Verify skill** among them, or a Verify skill corrected.

**Spec-bound dispatch**:
A sub-agent whose assignment is a document decided before it was dispatched — a Spec, a research question, an **Attempt**'s idea. Its agent file pins a cheaper model and a fixed effort, which a repo's **Models ref** may override, because the scope of the work was already settled: the **Planner**, the **Implementer**, and the **Verifier** run on Sonnet. Its opposite carries design or review judgement: the **Reviewer** is pinned to the model and effort that judgement needs, while a **Fixer** or a fan-out agent runs at the Driving session's own settings.
_Avoid_: cheap agent, worker, low-tier agent

**Merge risk**:
How hard a change is to undo once it lands, and what it would affect if it went wrong. It says whether reverting the change's commits restores the old behaviour — and when it does not, what stays changed after the revert, such as data written, a migration run, or a release published — and names who or what would notice if the change went wrong. The closing section of every pull request description `/pr` shapes; `/pr` works it out from the diff.
_Avoid_: merge danger, one-way door, two-way door

**Benchmark mode**:
The state of an `/implement` run the `benchmark/` runner starts to measure what it costs: `SKILLS_BENCHMARK=1`, named in the session's system prompt. The claim and every push become no-ops that write one line to a log, and every other part of the run goes as it does in production. Compared with what the run does, it changes only whether the run reaches outside the checkout.
_Avoid_: dry run, test mode, simulation

**Verify skill**:
The project skill at `.claude/skills/verify/` in the consuming repo that drives its app the way a user does: launch, doctor, drive, evidence, and cleanup, with a feature map holding one recipe per user-facing feature. Named `verify`, so it replaces Claude Code's bundled `/verify`. In a repo with a `CONTEXT-MAP.md`, each context with a running surface keeps its own under that context's folder. Written and kept current by `/setup verify`; a **Verifier** corrects it only where it steered it wrong.
_Avoid_: run recipe, verification skill, driver skill, control skill, smoke script
