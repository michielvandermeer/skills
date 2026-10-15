---
name: setup
description: Set up or update the repo's Tracker ref and the models pstack's roles run on.
disable-model-invocation: true
model: sonnet
effort: high
argument-hint: "[models | local | github | jira | other]"
---

# Setup

Two parts, each finished before the next starts:

- **Tracker** — the repo's `.agents/refs/tracker.md`.
- **Models** — the user's `pstack-models.md`, the sheet that picks each pstack role's model and effort and turns the SessionStart hook on or off.

The argument picks one part: `models` runs Models; `local`, `github`, `jira`, or `other` runs Tracker with that tracker picked. With no argument, run Tracker, then Models. Then offer a verification skill. While Tracker runs, the user hears only about Tracker.

Everything the user reads runs at the `/technical-writing` bar.

## Tracker

Write or update `.agents/refs/tracker.md`, the **Tracker ref**: the repo's own description of its **Tracker** and of how each operation the skills name is carried out there. The plugin ships one **Tracker template** per system — [LOCAL.md](LOCAL.md), [GITHUB.md](GITHUB.md), [JIRA.md](JIRA.md). The copy this part writes is the repo's own to edit; the skills follow it as written, and later changes to a template do not reach it.

### 1. Read what is there

- `.agents/refs/tracker.md`. When it exists, this run is an update: show its settings, ask what should change, and take the existing ref as the draft at step 3. An answer of no change ends the Tracker part.
- `git remote -v`, and `gh auth status` when the remote is on GitHub.
- Old tracker docs: `issue-tracker.md` and `triage-labels.md` under `.agents/refs/`, `.agents/ref/`, or `docs/agents/`. Read them only for what they say about the repo's tracker.
- Each line in `AGENTS.md` or `CLAUDE.md` that says where work is tracked.
- `CONTEXT-MAP.md`. Its contexts become labels on GitHub and Jira.
- Local work under `.agents/issues/`, `.agents/ideas/`, and `.agents/specs/`, in [LOCAL.md](LOCAL.md)'s shape or an older one.

Done: you can name the tracker the repo appears to use and list every local work document it holds.

### 2. Choose the tracker

Suggest one: GitHub Issues when the remote is on GitHub and `gh` is signed in; Jira when the old docs or the user name it; local Markdown otherwise. The invocation's argument counts as the user's pick. Otherwise ask the user to confirm the suggestion or pick another.

Then ask, in one round, for every setting the chosen template's `## Settings` section lists. For a tracker with no template, ask the user to describe how it does each operation the templates name.

Done: the tracker and every setting are known.

### 3. Draft and show

Copy the chosen template and fill in its settings. For a tracker with no template, write the user's description under the headings every template uses — Settings, Issues, Statuses, Maps and Decision tickets — with one entry for each operation the templates list. Show the draft and wait for a yes. An answer that changes the draft gets the changed draft shown again.

Done: the user said yes to the draft.

### 4. Apply

1. Write `.agents/refs/tracker.md`.
2. On GitHub, create each label the ref names that `gh label list` lacks: the statuses, the Decision ticket types, the categories, and the contexts.
3. Offer to move the local work from step 1. On yes, file each open document in the new Tracker — an old Idea as an Issue in `needs-grilling`, an old Spec as one in `ready-for-agent`, an Issue in its own status, a Map in `wayfinding` with its open Decision tickets as children — and skip any whose title the Tracker already holds. Delete each local file once its Issue exists. When the new Tracker is local Markdown, moving rewrites each document into LOCAL.md's shape at the path LOCAL.md gives it.
4. Offer to delete the old tracker docs, and to fix each `AGENTS.md` or `CLAUDE.md` line that contradicts the new ref. Apply what the user accepts.
5. Commit everything this run changed, staged by name, in one commit.

Done: the commit exists, and every move is done, declined, or reported as failed.

### 5. Report

Name the Tracker and the ref's path. List the labels created, each document moved with its new reference, each skipped because its title was already there, each move that failed, and each offer the user declined.

Done: every label, move, skip, failure, and declined offer from step 4 appears in the report.

## Models

Once Tracker is done, or when the argument is `models`, read [MODELS.md](MODELS.md) and follow its steps.

Done: its step 8 has told the user where the sheet is and whether the hook is on.

## Offer a verification skill

Check whether the project has a way to drive the real app for proof (a project `verify` or `verify-*` skill, or an existing harness). If not, offer once: "want a project-local verification skill, so agents can drive the app the way a user does and prove changes work? I can generate one with /create-verification-skill." On yes, invoke [`/create-verification-skill`](../create-verification-skill/SKILL.md). On no, move on without pushing.
