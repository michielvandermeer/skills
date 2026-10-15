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
The body an **Issue** carries once its status is `ready-for-agent` or `ready-for-human` — problem, solution, **Hand checks**, user stories, implementation and testing decisions — replacing whatever the Issue said before. Its problem, solution, Hand checks, and user stories are written for the **Product reader**; the rest is written for a developer new to the repo. The input to `/implement` and `/implement-yolo`. Written only when there is a change to implement; its Issue is blocked by another Issue when that one must land first. Work we will not do is not a Spec.
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
One check in a **Spec**'s How to Check It section: what a person does on the running product, and what they should see, written so a QA tester can follow it by hand. The **Verifier** runs every Hand check too, at the end of an implement run, on the code that lands. A Spec where nothing changes for a person has none, and says so.
_Avoid_: acceptance check, acceptance criterion, test case, manual test, QA script

**Unstated claim**:
A claim a Spec treats as settled that it never states as a decision and that the code does not establish as fact.
_Avoid_: assumption

**Decision ticket** (everyday: **ticket**):
A child of a **Map** in the **Tracker** whose resolution is a decision — not a slice of a build to execute. The unit of claim and resolution. Distinct from an implement run's unit of work, which delivers code and decides nothing.
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
A repo's own documents on how its code should be written — at `.agents/refs/` first, or a root-level `CODING_STANDARDS.md` or `CONTRIBUTING.md` when that is where the repo keeps them. Each repo writes its own rules; the skills name where to find them, never what they say. Distinct from `/code-review`'s smell baseline, which applies even when a repo documents nothing.
_Avoid_: style guide, conventions, coding-standards.md

### Communication

**Plain language**:
Writing pitched at a reader who does not know this repo, in the sense of ISO 24495-1:2023. The standard every piece of text a skill puts in front of a person is held to.
_Avoid_: simple English, simplified language, readability

**Product reader**:
Someone who knows the product but not its code — a QA tester, a product owner. The reader of the part of a **Tracker** document that says what is wrong and what changes: a **Spec**'s problem, solution, **Hand checks**, and user stories, a `needs-` **Issue**'s motivation and goal, a **Map**'s Destination. That part names only what this reader sees on the product, in words `CONTEXT.md` defines; the rest of the document keeps the developer reader of **Plain language**.
_Avoid_: QA reader, business reader, non-technical reader, end user

**Definition site**:
Text whose job is to fix the meaning of a term — a `CONTEXT.md` entry, a glossary heading, an ADR passage that coins a name. The one place precision outranks **Plain language**, because careful words paid once are what make the shorthand safe to use everywhere else.
_Avoid_: definition block, glossary entry

**Gloss**:
The plain-words introduction a skill gives its own vocabulary the first time that vocabulary appears — "the frontier (the questions I can ask now)". What buys a skill the right to use a term it defined rather than spelling the idea out every time.
_Avoid_: definition, footnote, explainer, aside

**Explanation**:
What an `/explain` run makes instead of prose: a diagram drawn with text characters in the chat, or a self-contained HTML page or narrated video in a temp folder outside any repo. Distinct from an **Explainer**, the opening sentences of a grilling **Question**.
_Avoid_: explainer, explainer video, visual

### Sessions

**Driving session**:
The main agent session a user invokes a skill in. It orchestrates and holds the low-resolution view; it delegates detail work to sub-agents so its context stays small. In an implement run it is the lead the `poteto-mode` skill describes: it owns the playbook, the **Run directory**'s `todo.md` and trail, and every delegate, and it decides the calls its full-autonomy grant covers.

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
A change a session made to code that existed before that session started, where the session also shows the old code was wrong — the user said so, a bug was being fixed, a test failed, or a review flagged it. Code written earlier in the same session is not a Correction, however soon it was fixed; neither is a change that follows a changed requirement. Who wrote the old code, a person or an agent, does not matter. A **Retrospective** turns a Correction into a Coding standards rule only when the fix points to a pattern future code could repeat.
_Avoid_: fix, bugfix, regression

### Execution

**Climber**:
The sub-agent (`skills:climber`) that writes one **Attempt** of a **Hillclimb**. It gets one idea, changes the code in the Hillclimb's worktree, builds, runs the tests nearest its change, and leaves the change uncommitted. The Driving session measures it and keeps or reverts it, so the Climber never judges its own change.
_Avoid_: attempt agent, hillclimber, worker

**Validator**:
The sub-agent (`skills:validator`) that checks a Spec `/to-spec` has just drafted. It works from the draft's path, corrects facts in that file, and returns the report of corrections and open questions; `/to-spec` then writes the corrected Spec to its Issue in one update.
_Avoid_: spec checker, spec reviewer, linter

**Reviewer**:
The sub-agent (`skills:reviewer`, pinned to Opus) that `/code-review` dispatches once per axis — Standards and Spec — in parallel, each starting fresh, or once carrying both axes when the caller asks for one. It reads the changes since the fixed point and reports findings; it fixes nothing, so a **Fixer** does that.
_Avoid_: review agent, critic, review bot

**Fixer**:
A sub-agent the Driving session sends to fix what a review or a build found. In an implement run it is the `Fix:` delegate, a fresh `skills:poteto-agent` with consolidated scope (the original brief, every later directive, the prior report, and the branch), one per fix round, for an Act-on finding of `interrogate`, a NOT VERIFIED item from the **Verifier**, or a red post-rebase check; its description starts with `Fix:`, and it never resumes the delegate whose work it fixes. The final review of a **Hillclimb** sends a **Spec fixer** with the Spec axis's findings, then a **Standards fixer** with the Standards axis's findings, each `general-purpose` at the Driving session's own settings and each starting fresh, so no single fixer carries both axes.

**Merge risk**:
How hard a change is to undo once it lands, and what it would affect if it went wrong. It says whether reverting the change's commits restores the old behaviour, and when it does not, what stays changed after the revert, such as data written, a migration run, or a release published, and names who or what would notice if the change went wrong. The closing section of every pull request description `/pr` shapes, and one line per kept change in a **Hillclimb**'s final report.
_Avoid_: merge danger, one-way door, two-way door

**Base branch**:
The branch the session was on when an implement command started, read again on a resume. The run branches from it, is reviewed and verified against it, and lands back on it. It is the repository's default branch only when the session started there.
_Avoid_: master, main, default branch, trunk

**Landing commit**:
The one commit an implement run leaves on the **Base branch** when it lands: the whole run's change, named after what it does, carrying each unit's title, a Bug fix's red and green output, and the Issue's closing reference. It replaces every commit the run made on its branch — a unit, a fixer, a `wip:` from a halt — so none of those stays on the Base branch, and it holds nothing from the **Run directory**. A **Retrospective**'s commit, when there is one, follows it as a commit of its own.
_Avoid_: squash commit, land commit, cleanup commit, merge commit

**Deviation**:
Anything a delegate did that contradicts the Spec or the design, any failure it left red because the Base branch already fails it, and any post-rebase failure that passed on the Driving session's re-run. A deviation from the design is recorded in `design.md`'s Implementation reconciliation section and the trail; every Deviation is named in the report.

**Spec-bound dispatch**:
A sub-agent whose assignment is a document decided before it was dispatched — a research question, a Spec draft, an **Attempt**'s idea. Its agent file pins a cheaper model and a fixed effort, because the scope of the work was already settled. Its opposite carries design or review judgement: the **Reviewer** is pinned to the model and effort that judgement needs, while a Hillclimb's **Fixer** or a fan-out agent runs at the Driving session's own settings. An implement run's delegates are neither: they take their model from the operator's `pstack-models.md` by role, as the `poteto-mode` skill says.
_Avoid_: cheap agent, worker, low-tier agent

**Run directory**:
`.agents/runs/<slug>/` in an implement run's working tree, with its own `.gitignore` holding `*` so no commit sweeps it in: `spec.md`, the run's copy of its **Spec**; `todo.md`, the run's only todolist and its state machine, generated by `open-todo.mjs` from the playbook and the **Overlay**, each item open, done, or skipped by a `skip:` or `n/a:` line under it, an indented `BLOCKED:` note under the Review gate a closed gate, a `## Playbook` section holding the playbook's prose outside its steps, and a `Landed:` header once the run landed; `trail.tsv`, the decision trail; `design.md`, the architect's synthesized design, with each candidate's package under `design/`; and `evidence/`, what the repro and the **Verifier** saved. The run's only state: a resume reads `todo.md`'s first open item, and `check-run.mjs` reads the directory at the landing gate, regenerating `todo.md` from its own headers and wanting each checked gate's trail row and evidence. Copied to the original checkout once the fast-forward succeeded and before the run worktree is removed, where `/retro` and the person reviewing the trail read it; a later run on the same slug replaces it, and a run whose `todo.md` is gone restarts at the route step with its commits kept.
_Avoid_: steps folder, proof folder, run folder, bookkeeping, scratch

**Overlay**:
The project playbook at `skills/implement/.agents/playbooks/implement.md`, written in the `poteto-mode` skill's own grammar (`extends`, `when`, and a `**Replace**` or `**In**` change anchored on a bundled step's quoted words), whose every change is a one-line pointer at the `/implement` rule that alters that step: the landing in place of a pull request, one writer in place of a worktree per delegate or per design candidate, a halt in place of each "ask the user", a report item in place of a stacked follow-up. It inserts no step of its own: `open-todo.mjs` applies it after the consuming repo's own project playbooks and adds the three gates itself, and the design-skip rule lives in `/implement`'s route step. poteto-mode's `check-playbooks.mjs` proves every anchor before a run starts, and a line it prints halts the run.
_Avoid_: patch, playbook fork, workflow file, WORKFLOWS.md

**Verifier**:
The fresh `skills:poteto-agent` that wrote none of an implement run's code, sent after the review gate, on the head that will land, to build, run the tests of every project the run touched against the **Base branch**, drive the matching surface, run every **Hand check** in the Spec, save artifacts under the **Run directory**'s `evidence/`, and return VERIFIED, NOT VERIFIED, or INCONCLUSIVE per item with the evidence path. VERIFIED on the change and on every Hand check it can reach passes the verification gate, with an unreachable Hand check skipped as a flag; a NOT VERIFIED item goes to a fresh **Fixer** and then a fresh Verifier, and so does any code change after it ran, a rebase onto a moved Base branch included.
_Avoid_: Checker, Prover, Judge, QA agent, tester

**Benchmark mode**:
The state of an `/implement` run the `benchmark/` runner starts to measure what it costs: `SKILLS_BENCHMARK=1`, named in the session's system prompt. The claim and every push become no-ops that write one line to a log, and every other part of the run goes as it does in production. Compared with what the run does, it changes only whether the run reaches outside the checkout.
_Avoid_: dry run, test mode, simulation
