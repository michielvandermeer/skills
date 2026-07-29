# mvdmio Skills

A collection of software-engineering skills for Claude Code, distributed as a plugin. This context covers the vocabulary the skills use to talk about the documents they read and write, and about each other.

## Language

### Work documents

**Idea**:
A loose, untriaged thought captured at `.agents/ideas/<slug>.md`. Not yet shaped into anything actionable.

**Refinement**:
The functional description of a change agreed by Product, QA, and Development in a `/refine` session, at `.agents/refinements/<slug>.md` with an HTML twin beside it — intent, use cases, and the delta against today, deliberately silent on implementation. Terminal: a Spec may be grilled out of it later, but nothing consumes it automatically.
_Avoid_: functional spec, requirements doc, BRD

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

### Execution

**Driving session**:
The main agent session a user invokes a skill in. It orchestrates and holds the low-resolution view; it delegates detail work to sub-agents so its context stays small.

**Planner**:
The sub-agent that reads a Spec, explores the codebase, and writes the Step files. Returns only a compact index to the Driving session — never the Step bodies.

**Step agent**:
The sub-agent that implements exactly one Step. Reads the prior Steps' Outcomes itself, leaves the test suite green, commits, and returns a fixed three-line report.

**Outcome**:
The section a Step agent appends to its own Step file recording what it built. The channel by which a Step agent informs its successors, bypassing the Driving session's context entirely.

**Deviation**:
Anything a Step agent did that contradicts the Spec or changes what a later Step must do. The one piece of a Step's detail the Driving session does carry forward.

**Tracer bullet**:
A vertical slice that cuts a narrow but complete path through every layer (schema, API, UI, tests), rather than a horizontal slice of one layer. The shape every Step takes.

**Wide refactor**:
One mechanical change whose blast radius fans across the codebase, so a single edit breaks call sites everywhere and no tracer bullet can land green. Sequenced as expand–contract instead of sliced vertically.
