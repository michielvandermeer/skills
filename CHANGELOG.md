# Changelog

## 2026-10-10: Fewer blocked commands in implement runs
`/implement`, `/implement-oneshot`, and `/implement-yolo` now run each command as a simple command from the run's working folder, and write files with the agent's file tools. Claude Code blocks a command in a worktree when it cannot tell that the command stays inside, for example one that starts with `cd` or uses a variable. On 9 and 10 October that blocked about 70 commands across nine runs, and each one cost the agent an extra try.

## 2026-10-10: Implement saves its proofs in its own working folder
`/implement`, `/implement-oneshot`, and `/implement-yolo` now save each step's proof files in `.agents/proof/` inside the run's own working folder, not in your repo's `.git` folder. Claude Code blocks a session in a worktree from writing outside that worktree. Because of this, steps often could not save their proofs and wrote the results into the step file instead. The new proof folder carries its own git ignore rule. Your repo's ignore files stay as they are, and no proof file ends up in a commit.

## 2026-10-10: Re-sending implement no longer resets work
If you send `/implement`, `/implement-oneshot`, or `/implement-yolo` again while that same run is still working in the same session, it now says the run is still going and keeps waiting. Before, it could reset the run's working folder and delete what its helper agents had not saved yet, such as the plan being written. A run that stopped, or one you pick up in a new session, still resumes where it left off.

## 2026-10-09: Grilling learns how you choose
Grilling sessions now learn your habits, such as widening a change or leaving out safeguards nobody needs yet, and recommend the option you would likely pick, with a line saying which habit moved it. Each person gets a profile per repo under `.agents/refs/profiles/`, so the round also names which option each teammate would likely pick. The profile updates when a grilling session ends, and the new `/learn-habits` command rebuilds yours from your last 100 grilling sessions in the repo.

## 2026-10-08: Implement lands as one commit
`/implement`, `/implement-oneshot`, and `/implement-yolo` now put one commit on your branch per run, named after the change and ending with the Issue's reference, in place of 7 to 18 commits named for the run's own bookkeeping. The run then pushes right away, so your CI run carries the change's name, and pushes again only if its retrospective changed a file. The step-by-step commits still exist while the run works, so a stopped run can pick up where it left off.

## 2026-10-08: Hillclimb a number toward a target
The new `/hillclimb` command improves one measured number, such as how long your test suite takes, by trying one change at a time and keeping only the changes that measurably help. It records every attempt in your repo under `.agents/hillclimbs/`, so the next effort skips ideas already proven not to help, and it lands the result on your branch the way `/implement` does. The agent also starts it on its own when you ask for something to be made faster, smaller, or cheaper.

## 2026-10-08: Implement skips the re-test after a docs-only update
When your main branch gains commits while `/implement` or `/implement-oneshot` is running, the run rebuilds and re-runs its tests before it lands. It now skips that when the new commits only change documents that no build or test reads, such as another run's notes or Markdown docs, and its final report says which commits it compared and why it skipped. A new commit that touches code, project files, test data or config, or one the run is unsure about, still gets the full re-test.

## 2026-10-08: Proofs run only the tests they need
In `/implement`, `/implement-oneshot`, and `/implement-yolo`, each step's proof now names the narrowest check that shows the step is safe, such as a single test, instead of the whole test suite. The final proof pass no longer re-runs the whole suite, which could add a quarter of an hour to a run. The full test run still happens once per step, as before.

## 2026-10-07: Checker finishes with a new commit
The Checker that finishes each `/implement` Step now lands its fixes and the `done` status flip in a **new commit**. Before, it amended the Step agent's commit, and auto mode could refuse that amend — leaving the Step stuck at `built`.

## 2026-10-07: Pull request descriptions show evidence
When the agent writes a pull request description, it now follows one shape: a small picture of the change, before-and-after output showing it works, and how risky it is to merge. A screenshot of a visual change is uploaded with `gh` and never committed to your repo. `/implement`, `/implement-oneshot`, and `/implement-yolo` now also say for each step how hard it would be to undo, and the final report lists that next to each step's proof.

## 2026-10-07: Each ADR gets its own number
Skills that write an ADR now pick its number from your git history across every fetched branch, and check it again just before committing, so two sessions working at once no longer give two ADRs the same number. A deleted ADR's number is no longer handed out again. `/doctor` now finds ADRs in one folder that share a number, gives the newer one the next number, and fixes every link to it.

## 2026-10-06: Implement runs push your branch
`/implement`, `/implement-oneshot`, and `/implement-yolo` now push your branch once the run has finished, so an Issue the work closes, such as one named in `Closes #42`, closes without you pushing by hand. If someone else pushed to the branch first, the run tells you and leaves the work on your machine for you to pull and push. To keep runs from pushing, for example because a push to your main branch deploys, add a line to your repo's `AGENTS.md` or `CLAUDE.md` saying implement runs do not push.

## 2026-10-06: Implement tests each step once
`/implement`, `/implement-oneshot`, and `/implement-yolo` now run each step's full set of tests once instead of twice. The agent that builds a step runs only the tests closest to its change, and the agent that checks the step runs the full set after its fixes, so a second agent still sees every test pass. Runs on Claude Code should finish roughly a tenth faster, and an agent now waits for a long test run to finish instead of starting it again.

## 2026-10-06: Implement re-proves the code that lands
`/implement`, `/implement-oneshot`, and `/implement-yolo` now prove each step one more time at the end of a run, on the code that actually lands, after the final fixes and the rebase have changed it. If a proof fails there, a fixer repairs the code or the proof, or reports that a later step changed that behaviour on purpose, and a second failure stops the run. Runs take slightly longer, and the final report no longer warns that the proofs predate the rebase.

## 2026-10-05: Implement claims its Issue
`/implement`, `/implement-oneshot`, and `/implement-yolo` now claim the Issue they build before they start, so two runs do not build the same Issue. On GitHub and Jira, claiming assigns the Issue to you. If the Issue is already assigned to someone else, the run stops and tells you who has it. The Issue stays assigned to you after the run stops or finishes, so you can pick it up again. Before, the implement commands never wrote to your tracker at all. If you set up your tracker before today, copy the new Claim line from the plugin's GitHub or Jira template into the Issues section of your `.agents/refs/tracker.md`. Without that line, runs do not claim anything.

## 2026-10-04: Explain with pictures
The new `/explain` command explains anything with a picture instead of a wall of text: a diagram in the chat, a web page, or a short narrated video. It picks the format that fits and checks with you first, unless you name the format yourself. Videos use xAI's voice when you have an xAI key, and otherwise a free voice that runs on your own machine.

## 2026-10-04: Bug diagnosis hides secrets
`/diagnosing-bugs` now replaces API keys, tokens, passwords and other secrets with `<REDACTED>` in every command, output and log it shows you. It builds its test loops on environment variables, so a credential stays out of the files it writes. When it finds that the bug came from how the code is structured, it now tells you to run `/improve-codebase-architecture`. Before, it tried to start that command itself, which a skill cannot do.

## 2026-10-04: Domain modeling loads when you edit the glossary
The `domain-modeling` skill now loads when you talk about your project's terms, or when you write or edit a `CONTEXT.md` or an ADR directly. Before, it loaded mainly when you asked to pin down terms or record a decision.

## 2026-10-04: Retro looks for checks you already have
Before suggesting a new automated check, `/retro` now reads your repo's existing lint and check commands and its CI workflow. If a check that would have caught the mistake already exists but is not running, or is broken, it says so instead of suggesting a new one.

## 2026-10-04: Implement picks up a leftover branch
`/implement` now carries on from an earlier run's branch when that run stopped and its worktree was removed. Before, it started the run again and could throw away the work already on that branch. `/implement-oneshot` already worked this way.

## 2026-10-04: Yolo works on a same-named branch
`/implement-yolo` no longer stops when the branch you have checked out has the same name as the Issue. Before, it wrongly said another run was already in progress somewhere else. It still stops when another run really is in progress in another worktree or on another branch.

## 2026-10-04: Wayfinder retro after writing Specs
The `/wayfinder` session that writes a map's Specs now ends with a retrospective, like every other `/wayfinder` session. Before, only that session skipped it.

## 2026-10-04: Map tickets sorted by app
In a repo with a `CONTEXT-MAP.md` that keeps its Issues as local files, a map's decision tickets now sit in the same app folder as the map, such as `.agents/issues/billing/<map>/`. Before, the instructions put them in a folder outside every app.

## 2026-10-04: Work lives in your own tracker
The skills can now keep your work in GitHub Issues, Jira, or another tracker, not only as files in your repo: run the new `/setup` to choose, and it can move your existing work across. Ideas, reports, and Specs are now one Issue whose status says where it stands, so writing a Spec updates that Issue rather than replacing one file with another. When an implement run finishes, its commit closes the Issue once you push, where your tracker supports that; otherwise the final report tells you which Issue to close.

## 2026-10-02: Documents sorted by app
In a repo with a `CONTEXT-MAP.md`, the skills now keep Specs, Ideas, Issues, Prototypes and reports in a folder per app, such as `.agents/specs/billing/`. Work that spans apps, or touches no app, goes in `common/`. `/doctor` moves existing documents into these folders instead of pulling them back to one shared folder, and repos without a map are unchanged.

## 2026-10-01: Proof files are deleted after a run
`/implement`, `/implement-oneshot`, and `/implement-yolo` now delete the folder of proof files when a run finishes. Before, every run left its scripts and screenshots in your repo's `.git` folder, where they piled up. If a run stops partway, the folder stays so the run can carry on later. The final report still lists what each step proved.

## 2026-10-01: Implement lands on your current branch
`/implement` and `/implement-oneshot` now start from the branch you have checked out, compare test results against it, and merge the finished work back onto it. Before, they always used `master`, so a run you started on a feature branch ended up on `master`. If no branch is checked out, the run stops and says so. `/implement-yolo` already stayed on your branch and still does.

## 2026-10-01: Each step proves it works
`/implement`, `/implement-oneshot`, and `/implement-yolo` now finish a step only when a fresh agent has re-run evidence that the risky part of the change works. That evidence must go beyond passing tests, and for a web page, command-line tool, or HTTP service it comes from running your app, using a run recipe the first run saves in your repo. `/implement-oneshot` and `/implement-yolo` now check their work the same way `/implement` does, and the final report lists what each step proved and where the evidence is kept.

## 2026-09-26: Implement checks each step afresh
`/implement` now sends a fresh agent to check each Step once it is built: it runs the browser pass, reviews the Step's commit, and fixes what it finds, so the agent that built the Step no longer does this at the end of a long session. The final review of `/implement`, `/implement-oneshot`, and `/implement-yolo` now sends one fixer for the Spec findings and then one for the Standards findings, each starting fresh, and the `/implement-oneshot` and `/implement-yolo` agent no longer reviews its own work first. Each Step also reads only the results of the Steps it depends on, so runs build the same thing as before but use less of your usage limits.

## 2026-09-26: Implement runs use fewer tokens
The agents that build your code for `/implement`, `/implement-oneshot`, and `/implement-yolo` now read it in fewer, larger pieces. They search for the place first, read a short file whole, and read several files at the same time when they can. They see the same code as before, so what they build does not change, but a run uses less of your usage limits.

## 2026-09-26: Brainstorm explores very different options
New `/brainstorm` takes a vague problem in plain words, or an Idea that is still too loose to grill, and explores it from four very different angles. One angle always searches the web for how other people already solve it, so it names real, current tools. You get a short card per option and its own pick, can go deeper or combine options until you choose, and each option you keep is saved as its own Idea, ready for `/grill-with-docs` or `/refine`.

## 2026-09-25: Doctor fixes ADRs the code outgrew
`/doctor` now checks every ADR against your code. When a migration, a commit, or a newer spec or ADR shows the decision changed on purpose, it rewrites the ADR to say what the code does, or deletes it when nothing of the decision is left. When nothing shows the change was chosen, it leaves the ADR as it is and lists the mismatch in its report as a bug to take to `/triage`, with the evidence it found.

## 2026-09-25: Doctor ends with a retrospective
After `/doctor` posts its report, it now runs `/retro`, as `/implement`, `/triage`, `/codebase-audit`, and the other skills you type already do. `/retro` applies its high-priority suggestions for your agent setup in a second commit after `/doctor`'s own, and lists the rest in its summary. It runs on every `/doctor` run, even when there was nothing to tidy.

## 2026-09-25: Doctor also moves your documents
`/migrate-doc-layout` is gone, and `/doctor` now does its job without asking first: before it checks specs, ideas, and ADRs, it moves every document it can recognise into its place under `.agents/` or `docs/adr/`. Old refinements become ideas, and issues and maps move into `.agents/issues/`. The moves go in `/doctor`'s one commit with every link to the old paths fixed, and the report lists any document it left where it was and why.

## 2026-09-25: ADRs show today's decision
When a decision changes, the skills now rewrite its ADR in place instead of adding a new one on top, and delete the ADR of a decision dropped with nothing in its place. `/cleanup-specs` is now `/doctor`: it still removes finished specs and ideas, and it also merges ADRs that record one decision into one, rewrites ADRs that tell history, and fixes every link to them. It makes all its changes in one commit and then tells you what it merged, rewrote, deleted, and found the code contradicting.

## 2026-09-25: Wayfinder no longer repeats research
When `/wayfinder` starts research on a ticket, it now marks that ticket as claimed before the research begins. If you run `/wayfinder` on the same map while that research is still running, it skips those tickets and works another open one. When only research is left, it tells you research is still running and stops, instead of paying for the same research twice.

## 2026-09-25: Retro learns from fixed mistakes
`/retro` now also reads the code your session changed, including work not yet committed. When the session fixed code that an earlier session got wrong, and the fix holds a lesson future code could repeat, `/retro` adds a rule for it to your repo's coding standards without asking. The agents that write and review code already read those standards, so later sessions avoid the same mistake.

## 2026-09-25: Coding agents check your standards
The agents that write code for `/implement`, `/implement-oneshot`, and `/implement-yolo` now treat your repo's coding standards as rules for every line they write, comments and tests included. Before handing back, each one runs `/code-review` on its own work and fixes what it finds. The agents that fix review findings afterwards also get your coding standards.

## 2026-09-25: Finished specs no longer leave stale waits
When `/implement`, `/implement-oneshot`, `/implement-yolo`, or `/cleanup-specs` removes a finished spec, it now also removes the line in any other spec that said it was waiting on that one. Specs no longer point at a spec that is already gone.

## 2026-09-24: Coding agents use your model
The agents that write code for `/implement`, `/implement-oneshot`, and `/implement-yolo` no longer switch to Sonnet. They now run on the same model as your session, at a lower effort level. This keeps the cost down while your chosen model writes the code.

## 2026-09-24: Wayfinder writes specs in a fresh session
When you finish the last ticket on a `/wayfinder` map, that session no longer writes the specs. It tells you to run `/wayfinder` on the map once more in a fresh session, and that session reads every finished ticket and writes the specs. If you run `/wayfinder` when every open ticket is already being worked on or waiting on another, it tells you which ones and stops.

## 2026-09-24: Wayfinder can end in several specs
When a `/wayfinder` map has no tickets left, it can now split the work into several specs, each one a change worth shipping on its own. It shows you the split first and writes the specs only after you agree, then removes the finished map. A spec that needs another to land first says so, and `/implement` waits until that other spec has landed.

## 2026-09-23: Flaky tests no longer stop runs
When `/implement` or `/implement-oneshot` finishes, it runs the tests again on the latest `master`. If a project fails there, the run now tests that project once more before it tries to fix anything. A test that passes the second time is named as flaky in the final report, and the run still finishes.

## 2026-09-23: Implement runs steps in order again
When you type `/implement`, steps run one at a time, in order, in the run's single copy of the project. Steps no longer get their own copies, so you will not see extra step worktrees or step branches. A run may take a little longer when steps could have run side by side.

## 2026-09-19: Type wizard for setup
Type `/wizard` when you need to provision a service, save credentials, walk a dashboard, or run a one-off migration. The agent can also start it when it hits a step only you can do. It writes a bash script that you run yourself; the script opens each page, captures what you paste, and writes it to `.env` or GitHub secrets.

## 2026-09-17: Planner writes Step files
When you type `/implement`, the Planner is now an agent that can write the Step files, so the first pass leaves those files on disk and the run starts building. A host that has not loaded that agent still uses one that can write files. The run still stops if that pass writes no files or replies with a long note instead of the step list.

## 2026-09-17: Finished steps drop leftover branches
When you type `/implement`, each finished step's branch is deleted once that step is on the run. You will not see leftover step branches in the repository after that.

## 2026-09-17: Implement on this checkout
Type `/implement-yolo` to build a spec in this checkout, on the branch you are already on. It does not open a second copy of the project and does not merge onto master. Review, the Changelog, and `/retro` still run.

## 2026-09-17: Failed land keeps the worktree
When `/implement` cannot merge the run onto the default branch, it leaves the run's worktree and branch in place. The session rebases there and tries the merge again. `/implement-oneshot` does the same.

## 2026-09-17: Step agents read your standards
When you type `/implement`, each Step agent reads the documents that say how this repo wants code written, before it writes tests or code. `/implement-oneshot` does the same. A repo with no such document is unchanged.

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
