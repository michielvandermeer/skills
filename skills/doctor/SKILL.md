---
name: doctor
description: "Moves documents into this project's canonical layout, closes local Issues the code already implements, brings every ADR to state the decision in force, trims oversized Coding standards to one short line per rule, and cleans repeats, dead paths, and contradictions out of Steering files."
disable-model-invocation: true
model: sonnet
effort: high
---

# Doctor

Keep a project's documents healthy: move every document into its canonical location, close the local Issues that already shipped, bring every ADR in `docs/adr/` to the shape where it states the decision in force, as things stand today — see [domain-modeling/ADR-FORMAT.md](../domain-modeling/ADR-FORMAT.md) for that shape — trim the Coding standards to one short line per rule, and clean repeats, dead paths, and contradictions out of the Steering files. Act on your own judgement from start to finish: make every change below, commit them all in one commit, then report.

Issues live in the repo's **Tracker**: carry out each operation on one — file, read, list, rewrite, set status, comment, link, close — as `.agents/refs/tracker.md` says, or as [setup/LOCAL.md](../setup/LOCAL.md) says when the repo has no ref.

Check for that ref first: only a repo with none gets its old local work converted onto the local Tracker and its implemented Issues closed ([ADR-0001](../../docs/adr/0001-each-repo-describes-its-tracker.md)). Every other step runs either way.

## Layout

Run this pass first, so an Issue converted from an old document is also visible to the Implemented Issues pass below.

Find every Markdown and near-Markdown (`.html`) document in the project, skipping `.git/`, `node_modules/`, `vendor/`, build output, `.agents/runs/`, `.agents/worktrees/`, the Tracker ref and any old `issue-tracker.md` or `triage-labels.md`, and anything already sitting in its canonical location. Work only on the checkout you're running in — never touch another worktree or branch.

When a root `CONTEXT-MAP.md` exists, read [MULTI-CONTEXT.md](MULTI-CONTEXT.md) before moving anything: it decides which `docs/adr/` an ADR goes to, and which context subfolder every other document goes to.

### Canonical locations

| Document type | Canonical location |
|---|---|
| Issue, Map, and Decision ticket | `.agents/issues/`, in [setup/LOCAL.md](../setup/LOCAL.md)'s shape — in a repo with no Tracker ref |
| ADR | `docs/adr/<NNNN>-<slug>.md`, or a context's own `docs/adr/` in a multi-context repo |
| Coding standards (also contribution guidelines) | `.agents/refs/<slug>.md` |
| Grilling profile | `.agents/refs/profiles/<name>.md` |
| Prototype | `.agents/prototypes/<slug>/` |

In a multi-context repo, every location above except ADR, Coding standards, and Grilling profile gains a context subfolder after its kind folder, as [MULTI-CONTEXT.md](MULTI-CONTEXT.md) sets out. Specs, Ideas, and refinements have no location of their own: each converts to an Issue — see below.

### Mechanical moves

Read [LEGACY-MOVES.md](LEGACY-MOVES.md) for the old layouts whose destination follows from the source path alone — a `.scratch/` tracker, flat session output that should be a folder, a flat refinement, an app-first layout. Relocate the whole tree; don't read these file by file.

### Classify everything else by content shape

Classify each remaining document by what it actually contains. Filename and current directory are hints at best — a document could be anywhere.

- **Spec** (also plan and PRD): has (or is clearly meant to have) sections like Problem Statement, Solution, How to Check It, User Stories, Implementation Decisions, Testing Decisions, Out of Scope — the `/to-spec` template — or a `Status:` line with a triage role plus prose describing a feature to build.
- **Idea**: has sections like Motivation, Goal, Decisions (locked), Out of scope, Open questions — the shape `/validate-spec` checks on an Issue in `needs-grilling`. Looser and earlier-stage than a Spec; no implementation detail.
- **ADR**: the shape in [domain-modeling/ADR-FORMAT.md](../domain-modeling/ADR-FORMAT.md) — a short title plus 1-3 sentences of context/decision/why, with or without a `status:` line, optionally Considered Options or Consequences. Usually sequentially numbered. The ADRs pass below strips any status line once the ADR lands.
- **Coding standards**: documents how code should be written or how the repo/team works, contribution guidelines included. Common filenames: `CODING_STANDARDS.md`, `CONTRIBUTING.md`, `STYLEGUIDE.md`.
- **Old refinement**: the legacy refinement shape — Intent, How it works today, In scope, Out of scope, Prototype, Open Questions — or an older variant: Introduction, Use cases, Scope, Notes, and older still a Technical details section. Functional throughout, with no implementation decisions and no `Status:` line. It is a source only, and it converts to an Issue (below).
- **Issue**: a `Category:` line and a `Status:` line near the top.
- **Decision ticket**: a `Type:` line and a `## Question` section.
- **Map**: a file named `map.md` with `## Destination` and `## Decisions so far` sections.

Prototypes get no content shape: a Prototype has no marker file and is plain app code or HTML, so a content match would risk moving real code. A Prototype moves only as the `prototype/` folder of an old refinement (below).

A document that matches no shape cleanly is **unclassified**. Leave it where it is and list it in the report.

### Converting to the local Tracker

In a repo with no Tracker ref, every Spec, Idea, Issue, and Map found becomes an Issue on the local Tracker at `.agents/issues/<slug>.md`: move it with `git mv`, set its header lines under the H1 as [setup/LOCAL.md](../setup/LOCAL.md) lays them out, and keep its body as it stands.

- **Spec** → `Status: ready-for-agent`; the slug is its file name. A `Blocked by: <spec-slug>` line stays as written, since that Spec keeps its slug.
- **Idea** → `Status: needs-grilling`; the slug is its file name.
- **Issue** → keeps its `Status:` and `Category:` lines; the slug is its file name without the `NN-` prefix. A `## Triage Notes` section and any comments fold under one `## Comments` heading that ends the file. An Issue whose status LOCAL.md does not list stays where it is and goes in the report.
- **Map** → `.agents/issues/<effort>.md` with `Status: wayfinding`, where `<effort>` is the name of the folder holding `map.md`. Its Decision tickets move unchanged to `.agents/issues/<effort>/`; an Issue in that folder converts on its own. A Map with no folder of its own around it, such as a loose file at the repo root, and a Decision ticket with no Map beside it stay where they are and go in the report: `/doctor` never invents an effort to hold them.

An Idea or Issue whose `Spec:` line names a Spec that exists is deleted, and the Spec converts in its place. Drop every other `Spec:` line.

A slug an Issue in another context subfolder already holds is a collision too (see Moving).

In a repo with a Tracker ref, every Spec, Idea, Issue, Map, Decision ticket, and old refinement stays where it is; list each one outside the Tracker in the report.

### An old refinement becomes an Issue

Apply this to every folder under `.agents/refinements/`, and to a flat or loose refinement-shaped document found anywhere. The slug is the folder's name, or the file's own name for a flat or loose document.

- The Issue at `.agents/issues/<slug>.md` is `complete.md`, converted as an Idea. When the folder has no `complete.md`, the Issue is `session.md`, converted the same way.
- Delete `session.md` once `complete.md` exists to read from. Always delete `complete.html`.
- Move a `prototype/` folder inside the refinement to `.agents/prototypes/<slug>/`, and add one line to the Issue naming that path.
- Remove the emptied refinement folder, and `.agents/refinements/` itself once nothing is left in it.
- An Issue or Prototype folder that already holds that slug is a collision (see Moving).

### ADR numbers

A moved ADR keeps its number when that number is free in its target `docs/adr/`. One with no number gets the next number there, as [domain-modeling/ADR-FORMAT.md](../domain-modeling/ADR-FORMAT.md#numbering) picks it. One whose number is already taken there is a collision (see Moving), not a move.

### Moving

Move with `git mv`, creating destination folders as needed — this keeps each file's history. A move whose destination already exists is a **collision**, and so are two moves that want one destination: leave each document where it is and list it in the report, with the file already occupying the destination.

Done when every document found sits in its canonical location or is listed in the report.

## Implemented Issues

In a repo with no Tracker ref, go through every Issue on the local Tracker and close as done each one the codebase already implements. Judge that from the codebase; the status an Issue carries is a hint at most.
When an Issue you close is in a `needs-` status and names a folder under `.agents/prototypes/` as its Prototype, delete that folder too — no document points at it any more.

Done when every Issue left describes work the codebase does not have yet.

## ADRs

Read every ADR in every `docs/adr/` folder the project has: the root one, plus every folder a `CONTEXT-MAP.md` lists.

Every change in this section keeps the project's own section layout (Context / Decision / Consequences, or whatever it already uses) — reshape what an ADR says, not how it's laid out.

### Renumber duplicates

ADRs in one `docs/adr/` folder that share a number are a duplicate. Run this first, so every number the steps below read names one ADR. The ADR that reached the current branch first keeps the number: compare the committer date of the oldest commit `git log --diff-filter=A -- <path>` gives for each file. `git mv` each of the others to the next number, as [domain-modeling/ADR-FORMAT.md](../domain-modeling/ADR-FORMAT.md#numbering) picks it.

### Find chains

A **chain** is the set of ADRs that record one decision at different points in time. Find one from:

- a `status:` frontmatter line (`superseded by ADR-NNNN`, `partially superseded by ADR-NNNN`)
- a newer ADR whose body says it replaces part of an older one, even with no `status:` line pointing back to it

### Fold each chain

Fold each chain into the ADR with the newest number: merge only the parts that overlap, keeping whatever part of an older ADR no newer one replaced. Delete an older file once nothing of its own remains in the chain.

### Delete reversed decisions

An ADR whose `status:` line marks it superseded, deprecated, or rejected, with no newer ADR named there or found replacing it, records a decision reversed with nothing in its place. Delete it.

### Remove status lines

Remove the `status:` line from every ADR you keep: a Folded one, an older one keeping parts of its own, and every ADR outside any chain (`accepted`, `proposed`, and the like). Remove the frontmatter block too when `status:` was its only field. An ADR in `docs/adr/` is in force by being there.

### Rewrite ADRs that tell history

Rewrite every ADR whose text narrates history — "used to", "ADR-NNNN had…", "Superseded:" — so it states the decision as it stands today, whether or not anything ever replaced it.

### Align with the code

Check every ADR you keep against the code, and bring it in line where the decision moved on.

Dispatch `skills:explorer` agents, each with a batch of about ten ADRs. In a multi-context repo, a batch holds one context's ADRs and the explorer reads that context's code. Ask each explorer to return, for every claim an ADR makes that the code contradicts:

- the claim, and the code that contradicts it, with file and line
- any **intent** behind the change, made after the ADR's decision: a migration, a commit whose message states the change, or a newer Spec or ADR that covers it
- the reason the commit that changed the code gives, if any

Give each batch the Specs its ADRs came from, too. A commit that writes an ADR at Spec time names the Issue's reference in its message — an older one adds the Spec's file under `.agents/specs/` instead — so the newest such commit in `git log --follow` on the ADR leads to its Spec; an ADR with no such commit has no Spec to check. Read that Issue through the Tracker. A local Issue file or `.agents/specs/` file gone from the checkout is read from that commit with `git show <sha>:<path>`. When the Issue is closed or its file is gone, pass the explorer the Spec, or the commit's SHA and the file's path for it to read, and ask which parts of what the Spec planned the code has. Judge that ADR against what was built: delete it when nothing was, and rewrite it to describe the part that was built when the code lacks the rest.

Wait for every report; the judgement is yours. Judge each mismatch:

- **Moved on** — the change has intent. Rewrite the ADR in place as [domain-modeling/ADR-FORMAT.md](../domain-modeling/ADR-FORMAT.md) sets out, with the smallest edit that makes it state what the code does; the parts that still hold keep their wording. In the rewritten ADR, state the reason the commit that changed the code gives, or say that the reason was not recorded when git gives none. Delete the ADR when the code keeps nothing of its decision.
- **Bug** — the change has no intent. The ADR wins: leave that claim as written. Leftover code the decision already removed is a bug too, even when an older migration or commit built it.

Application code stays as it is, and the report is the only record of a bug.

Done when every ADR you keep has a number no other ADR in its folder holds, has no `status:` line, states the decision in force, and agrees with the code — or disagrees only where the code has a bug the report names.

## Standards health

Bring every Coding standards rule to the shape [ADR-0081](../../docs/adr/0081-a-coding-standards-rule-is-one-short-line.md) sets, because `/implement` copies each rule that applies into every Step file. This pass runs after the ADRs pass and before the Update every link pass, so that pass also fixes links to text this pass moved or merged. It changes the standards itself, in the one commit, and it writes no Spec, no ADR, and starts no `/implement` run.

**Files.** The documents `/implement` hands its agents as Coding standards, found the way `/code-review` finds them: `.agents/refs/` first, then a root `CODING_STANDARDS.md` or `CONTRIBUTING.md` (the Layout pass has already moved a root-level one), and only documents that say how code should be written. A testing document an index links to as standards counts. A reference document such as a linter catalogue, build commands, or a triage seed does not. A repo with no Coding standards skips this pass; the report says so in one line.

**Rule shape.** One imperative line of at most 40 words, counted as whitespace-separated words the way `wc -w` counts. It holds the requirement, its exceptions and scope, and at most one short example or reason. A leading `[judgement]` or `[hard]` marker stays and is not counted. Nested bullets under a rule belong to it and count toward its words. Split one long rule into several one-line rules when that fits. The cap is fixed here: no per-repo setting, no per-file or total budget.

**Never drop a requirement to fit.** Every requirement, exception, and scope limit in the old text is kept, moved to a named place, or covered by a check you have read. A rule that cannot fit in 40 words stays as long as it needs and goes in the report as over the cap. Write no new requirement.

Apply these to every rule:

- **History.** Cut an incident story, the issue it came from, and the commit that fixed it to an `(#n)` or SHA reference at the end of the rule.
- **Enforced.** Delete a rule when an analyzer rule, a lint rule or setting, or the repo's Pre-review check covers all of it. Coverage counts only after you have read that check's source or documented behaviour and confirmed it catches every case the rule names. When a check covers part of a rule, keep the uncovered part in full and drop the covered part. When you cannot confirm coverage, the rule stays and goes in the report. Leave no pointer line behind.
- **Duplicates.** Rules that state the same requirement, in one file or across files, become one rule in the file whose topic fits best, keeping every exception either source had.
- **Stale.** Drop a rule that names a path, type, or symbol absent from the codebase when nothing succeeds it. When the name's history in git shows a rename, give the rule the new name. When you cannot tell which happened, the rule stays and goes in the report.
- **Not a rule.** Move text that is not a rule (stack facts, process steps, config values, helper catalogues) to the `.agents/refs/` document whose topic fits it, or a new one there, by the same content-shape judgement the Layout pass uses. An index file that only links the standards documents stays.
- **`[judgement]`.** Never add, remove, or change a marker. List as candidates the unmarked rules whose break would be a style matter rather than a wrong result, a crash, or lost data ([ADR-0079](../../docs/adr/0079-a-coding-standards-rule-is-hard-unless-marked-judgement.md)).

Count words with `wc -w`, the same way before and after, over the same file set.

Done when every rule is one line of at most 40 words or is in the report as over the cap, every old requirement is kept, moved, or covered by a check you read, and every file's word count before and after is in hand for the report.

## Steering health

Keep the rules that steer agents in this repo free of repeats, dead paths, and contradictions. This pass runs after Standards health and before the Update every link pass, so that pass also fixes links to text this pass moved or merged; a path the Layout pass moved is fixed there and never counts as dead here.

**Files.** Every `AGENTS.md` and `CLAUDE.md` at any depth, every `SKILL.md` and the files it links to, and every agent definition file (such as `.claude/agents/*.md` or a plugin's `agents/*.md`), skipping the folders the Layout pass skips. The host's global files are out. The Coding standards documents, found as Standards health finds them, and any ADR or `CONTEXT.md` a `SKILL.md` links to are read for comparison only: this pass never edits them. A checkout with no Steering files skips this pass; the report says so in one line.

**Rule.** A line or bullet that tells the agent what to do or not do. Fenced code and quoted samples hold no rules and no paths for this pass: it neither changes a path inside an example block nor names it in the report, not even as ignored.

- **Repeats.** Rules that state the same requirement, in one file or across files, become one rule in the file whose topic fits best, keeping every exception either source had. When one copy is a Coding standards rule, the Steering file copy goes, because the Planner copies Coding standards rules into every Step file ([ADR-0080](../../docs/adr/0080-the-planner-copies-each-steps-rules-into-its-step-file.md)) and that copy reaches the Implementer. An exception only the Steering file copy had stays in that Steering file as a rule of its own.
- **Dead paths.** Check every relative Markdown link and every bare repo path in a rule. Target exists: nothing changes. Git history shows a rename: rewrite to the new path. Git history shows deletion with no successor: drop the pointer and any words that only make sense beside it. Neither can be told: leave the path and list it in the report. URLs and paths outside the checkout are not checked.
- **Contradictions.** Two rules contradict when following one breaks the other for the same kind of change. Settle one only with evidence, by the intent test the ADRs pass uses: an ADR in force that decides it, the code doing what one rule says, or a later commit whose message states the change. The rule the evidence backs stays; the other is removed, or rewritten to keep any part the evidence does not touch. With no evidence, both stay as written and the report lists the pair. A Steering file rule against a Coding standards rule counts too: when the evidence backs the Coding standards rule, the Steering file rule goes; otherwise both stay and the report lists the pair.

Judge each case by reading, with no script: a script or link checker cannot tell a real pointer from an example, or a real conflict from two rules that differ in scope.

Done when no rule in the repo's own Steering files repeats another, every path in them resolves or is in the report, and every contradiction between them is settled by evidence or numbered in the report.

## Update every link

Grep the whole repo for every path the Layout pass moved or deleted, every ADR you Folded, renumbered, renamed, or deleted, and every Coding standards document the Standards health pass merged into another file or deleted — search both the old path and the bare filename, and include `CLAUDE.md` and `AGENTS.md`. Also search every heading anchor (`#...`) of a rule or section the Standards health or Steering health pass moved or merged. Fix every link you find, in skills, READMEs, code comments, anywhere a path, a bare filename, an anchor, or an `ADR-NNNN` reference appears. A link to a deleted ADR with no Folded successor goes, along with any words that only make sense beside it. A bare `ADR-NNNN` naming a duplicate's number, where the words around it don't settle which ADR it means, stays as written and goes in the report.

Done when every old path, bare filename, and anchor of moved or merged text greps clean across the repo, and every bare `ADR-NNNN` naming a duplicate's number is fixed or in the report.

## Report

Close with what moved and where, what stayed and why (unclassified, collision, no effort folder, a status the local Tracker lacks, the repo's Tracker ref), which Issues you closed as done, and what you renumbered, Folded, rewrote, and deleted among the ADRs, with the evidence for each ADR changed because of the code — the reader's way of knowing what to look at in the diff. List each `ADR-NNNN` you could not attribute to one of a duplicate's ADRs, with where it appears. When the Tracker ref kept documents in place, suggest `/setup`, which offers to move local work into the Tracker. List every bug the code check found, with its evidence and a suggestion to take it to `/triage`. For Standards health, give a table of words per file before and after with a total row. List every rule merged, deleted as enforced (naming the check), dropped as stale, moved, or split, each with its reason. List every rule left over 40 words, every rule left in place because coverage or staleness could not be confirmed, and the `[judgement]` candidates. A repo with no Coding standards gets one line saying the pass was skipped. For Steering health, list every merge, path fix, drop, and settled contradiction, each with its reason and evidence (a settled contradiction names the ADR, code, or commit that decided it). Give a numbered list of the contradictions left for a person, each quoting both rules with file and line, and list every path left because its history could not be judged. A path inside an example block is not in the report, not even as ignored. A checkout with no Steering files gets one line saying so. For the report, read [`technical-writing/SKILL.md`](../technical-writing/SKILL.md) and follow it — `/technical-writing` does not load as a skill.

Done when every move, every document left where it was, every Issue you closed, every ADR you renumbered, Folded, rewrote, or deleted, every `ADR-NNNN` you could not attribute, and every bug appears in the report, the Standards health part is in it: the skip line, or the word counts and every rule changed, left over the cap, left unconfirmed, or named a `[judgement]` candidate, and the Steering health part is in it: the no-Steering-files line, or every change with its evidence, every numbered contradiction, and every path left unjudged.
