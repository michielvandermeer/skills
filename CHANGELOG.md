# Changelog

## 2026-09-16: No-change grilling writes no Spec
When you confirm a `/grill-with-docs` Read-back (the settled design restated) that we will not do the work, the session writes no Spec. It deletes the Issue or Idea it started from, says it wrote no Spec because nothing will be built, and still runs `/retro`. A Read-back that still names a change still writes a Spec.

## 2026-09-16: Specs carry only ready-for-agent
`/validate-spec` now accepts only `Status: ready-for-agent` on a Spec. It rewrites a leftover `needs-triage`, `needs-info`, or `ready-for-human` line to that value. A `wontfix` Status is a question rather than work to build.

## 2026-09-16: Retro writes this repo only
`/retro` now changes only files in the repository you have open. A suggestion for a skill, a user-wide file, or anything else outside that tree stays in the list so you can do it yourself. The important ones are marked and listed first.

## 2026-09-16: Refine finishes with a Spec
Type `/refine` with an Idea or a Jira ticket. The session asks you what the change should do, offers a prototype, writes a Spec, and puts a short summary back on that Idea or ticket. It finishes in one sitting, and the records that remain are the Spec and the updated Idea or ticket.

## 2026-09-15: Retro runs after session skills
`/implement` and the other session skills now finish by updating the files and tools that steer later runs, then listing what they did. You can still type `/retro`. The important changes land without a confirm step.

## 2026-09-14: Planner stops at the footprint
When you type `/implement`, the Planner stops as soon as it can name the files each Step will touch, writes those files, and starts building. A plan that writes no files, or replies with a long note instead of the step list, stops the run so you can type `/implement` again. It does not send a second agent to invent the files.

## 2026-09-14: Review a spec before building
Type `/review-spec` on the model you want as a second opinion. It proposes edits to the spec, writes the ones you pick by number, and then checks the file still holds together.

## 2026-09-13: Architecture review writes several files
When the architecture report is ready, you choose which suggestions become Ideas and which become Specs. Only a change that is ready to build becomes a Spec. The session then stops so you can grill or implement those files yourself.

## 2026-09-13: Implement runs independent steps together
When you type `/implement`, steps that do not wait on each other now run at the same time, each in its own copy of the project. They join one branch as they finish, so the history stays a straight line. A step that needs another still waits.

## 2026-09-13: Type retro after a session
Type `/retro` to get suggestions for the files and tools that steer later agent runs. Skills do not start this on their own. You apply a suggestion later if you want.

## 2026-09-13: A skill for merge conflicts
When a merge or rebase stops on a conflict, `/resolving-merge-conflicts` works through each hunk, keeps both sides' intent where it can, and finishes the operation. `/implement` uses it when folding steps together or landing the branch.

## 2026-09-09: Oneshot implement without planning
Type `/implement-oneshot` to build a spec in one agent session, without a plan of steps first. `/implement` still slices work into steps. Both still review, improve data structures, and land.

## 2026-09-09: Triage splits and parks
When you run `/triage` on an email, a file, or a ticket, each separate problem becomes its own Spec or issue. Unclear work is saved as an issue that still needs information, a person, or a later grilling session. Work you will not do is not kept as a file.

## 2026-09-07: Grilling waits for its facts
A `/grill-with-docs` session pulls first, sends background readers for every fact it needs from the code, and waits for their reports before asking the questions that depend on them. Facts only you hold are asked as questions.

## 2026-09-07: Grilling ends with a read-back
When nothing is left to ask, the session restates the settled design once, surface by surface, and asks you to confirm before it writes the spec. Glossary entries land as terms settle, ADRs are declarations you can decline, and a screen question goes to `/prototype` instead of lettered options.

## 2026-09-07: Implement runs never push or publish
An `/implement` run never pushes, publishes, or changes a live system; a Step that needs that stops the run and says so. Work in a second repository stays on an unpushed branch named in the final report.

## 2026-09-07: Implement measures green against master
A test that already fails on master is reported, not fixed, and does not block landing. When master moved during the run, `/implement` re-runs the affected projects before landing.

## 2026-09-07: Implement plans survive a retry
The Planner commits the Step files before the first Step runs, so a retry or resume cannot delete them. The Driving session hands paths and reads no Step or Spec itself. It also works on hosts whose shell forgets its directory, and in repos whose default branch is `main`.

## 2026-08-28: Implement agents decide themselves
When `/implement` hits something the Spec or a Step did not settle, the agent working on it decides and keeps going. You still see a Deviation when the choice contradicts the Spec or changes a later Step.

## 2026-08-25: Refine close is simpler
A `/refine` session overwrites the Jira ticket or markdown file it started from after you confirm the text, and no longer asks whether to replace, comment, or skip. It keeps the prototype in the refinement folder next to the briefing, and no longer writes an HTML report.

## 2026-08-25: No suggestions after a session
Skills no longer suggest environment changes when they finish, and you can no longer type `/retrospective`. A session ends when its own work is done.

## 2026-08-24: Retrospective after more skills
`/grill-with-docs`, `/triage`, `wayfinder`, `refine`, `/codebase-audit`, and `improve-codebase-architecture` now finish by suggesting environment changes, the same as `/implement`. The skill you typed runs it. A session still waiting for you does not.

## 2026-08-24: Retrospective after every implement
`/implement` finishes by suggesting changes to the files and tools that steer later agent runs, so the next session is cheaper or more reliable. You can also type `/retrospective` yourself. Suggestions appear in the chat; you apply them later if you want.

## 2026-08-21: Fewer tiny grilling tickets
`/wayfinder` puts leftover one-question grilling work in one Small questions ticket, so you start the skill less often. A tree of related questions still gets its own ticket. You still finish one ticket per session.

## 2026-08-21: Refine scopes through a prototype
`/refine` now settles what is in a project and what is not. After a short grilling it builds a prototype the room can steer, then writes a briefing a developer takes into `/grill-with-docs`.

## 2026-08-15: Prototypes stay for Specs
After you give a verdict, `/prototype` keeps the demo at `.agents/prototypes/<slug>/` and the Spec points at that folder. The worktree and its branch still go, so your working copy stays clean.

## 2026-08-14: Audit a whole codebase
You can now ask for a read-only check of a whole app that looks for simpler data structures and clearer ownership. It writes a report and does not change your code.

## 2026-08-11: Prototype sessions end in a Spec
`/prototype` now builds in a worktree of its own, so your working copy stays clean while you try the demo out. Once you give your verdict, the session writes a Spec naming the question the prototype answered and what you settled, then removes the worktree and deletes its branch. The prototype itself does not survive, so the Spec is the record, and `/implement` builds the real code from it.

## 2026-08-07: Triage ends as Spec
When `/triage` finishes work you can build, it writes a Spec and removes the issue file. Clear issues skip the interview; unclear ones use `/grill-with-docs` first. Open issues still use needs-info, ready-for-human, and wontfix — agent-ready briefs on issues are gone.

## 2026-08-05: Changelog of product changes
`/document-changes` writes a Changelog beside each CONTEXT.md — one plain entry per shipped product change, newest first. `/implement` runs it before land, so each run that changes a context leaves a record a product user can read.

## 2026-08-05: Upstream upgrades for four skills
Architecture scans drop work that is not needed yet, and logic prototypes produce shareable HTML as the main artifact. Wayfinder treats each unit as a decision ticket and can burn down research in parallel. Writing guidance now covers any document an agent reads, not only skills.

## 2026-08-05: Refine stays functional only
User-facing refine surfaces — rounds, HTML, the Complete document, and the Jira write-back — describe behaviour only and no longer carry a Technical details section. Domain modeling still updates CONTEXT.md during refine and no longer offers ADRs from that path.

## 2026-08-04: Easier-to-read grilling rounds
Each question opens with a short explainer, uses a Q prefix, and letters closed choices with costs on the option lines. Round 1 starts with a plain orientation so a cold tab still makes sense, and each declaration sits on its own line.

## 2026-08-03: Smaller wayfinder maps
A wayfinder map charts only forks in the road, not every piece of road between them, and aims at the smallest change that does the work. Every map ends in a Spec ready for `/implement`.

## 2026-08-01: Steps name their footprint
Each Step names the files, symbols, and projects it touches. Green means those projects pass; only the last Step runs the whole suite.

## 2026-07-31: Plain language for people
Every sentence a skill puts in front of a person runs in plain language. Skill source stays dense for agents; people get words they already hold.

## 2026-07-31: Architecture reviews describe function
Each architecture-review candidate leads with what the affected functionality does and what triggers it, so a mixed room can read the card without opening the code.

## 2026-07-31: Refine keeps the room moving
Exploration runs in the background while the room grills, so people are not idle waiting on a code walk. A session ends with a Complete document in a fixed section shape, in its own folder under `.agents/refinements/`.

## 2026-07-30: Cheaper agents for decided work
Step agents, explorers, and researchers run at a pinned lower cost tier. Design and review work still uses your session's own model and effort. These skills assume an Opus-or-above session.

## 2026-07-29: Implement slices work into steps
`/implement` plans Steps and runs each in its own agent, so a large Spec fits one session. A halted run picks up where it left off.

## 2026-07-29: Add the refine skill
`/refine` takes Product, QA, and Development through a change on functional terms only. It writes a Refinement with a live HTML view.

## 2026-07-29: Grilling format and altitude
Grilling pins a fixed round format and classifies the subject as functional or technical so the altitude matches. One-answer items become declarations; silence accepts them.

## 2026-07-29: Remove the tdd skill
The tdd skill is gone from the plugin. Install checks and docs point at other skills instead.

## 2026-07-28: Grilling waits for exploration
A grilling session now waits until background exploration finishes before it asks questions that depend on that reading.

## 2026-07-26: Correct install and update steps
Install and update docs match how Claude Code treats third-party marketplaces: auto-update is off until you opt in, and updates need the qualified plugin id and the right scope.

## 2026-07-23: Issues live under .agents
Triage and wayfinder store issues under `.agents/issues/` instead of `.scratch/`. `migrate-doc-layout` can move a legacy tracker.

## 2026-07-22: Linear history after implement
`/implement` lands with rebase and fast-forward so the default branch stays linear, with no merge commit.

## 2026-07-20: Round-by-round grilling
Grilling asks a full round of frontier questions at once, then waits for answers. Skills that use grilling inherit that cadence.

## 2026-07-20: Fixed local tracker layout
Skills hardcode the local markdown issue tracker and a canonical `.agents/` layout for Specs, ideas, and related docs. `migrate-doc-layout` brings older repos into line.

## 2026-07-20: Install as a plugin
The repo is a Claude Code plugin and its own marketplace. Install with `/plugin marketplace add` and `/plugin install skills@mvdmio`.

## 2026-07-12: Add cleanup-specs skill
`/cleanup-specs` removes Spec, Plan, and Idea documents that have already been implemented.

## 2026-07-12: Initial skills catalog
The first ship of the skill set for Claude Code, covering implement, review, grilling, triage, wayfinder, and related workflows.
