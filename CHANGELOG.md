# Changelog

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
