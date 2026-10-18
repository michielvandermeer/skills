---
name: retro
description: Look at a finished session, apply high-priority changes this repository owns, file the structural ones as Issues, and summarise the rest.
argument-hint: "[session]"
disable-model-invocation: true
model: sonnet
effort: high
---

A **Retrospective** applies **High-priority** environment changes to **Owned files** without asking, files each **Structural fix** as an Issue, then summarises. `/code-review` still reviews the product diff; `/retro` reads it only to find **Corrections**.

Apply and present only when the skill the user typed — or, when they typed none, the outermost skill the agent loaded — is this `/retro` or has reached its own done condition.

Run `/writing-for-agents` for how a steering edit is written, and `/technical-writing` before an Issue or the summary. Which mechanism a lesson gets follows "Encode lessons in structure" in [code-review/PRINCIPLES.md](../code-review/PRINCIPLES.md): agents copy what exists and take the shortest path, so code that makes the wrong thing impossible beats a check, and a check beats prose.

Issues live in the repo's **Tracker**: carry out each operation on one — file, list, comment — as `.agents/refs/tracker.md` says, or as [setup/LOCAL.md](../setup/LOCAL.md) says when the repo has no ref.

The argument names a session, or is empty for the current one.

## Sources

The host's session logs for the current or named session, plus the steering files that session used, plus the session's code changes. Look up log paths for this host. If the named session cannot be found, stop and say so. If logs for the current session are not on disk, work from what this conversation holds.

**Steering files** always include the repo's `AGENTS.md` / `CLAUDE.md` and the host's global always-loaded agent files, plus any file this session actually reached.

The session's code changes are the commits the session log records for the current or named session, plus any uncommitted changes still in the working tree. Take the commits from the session log. An implement run's change is its landing commit: once the run lands, its other commits are on no branch.

## Corrections

A **Correction** is a change to old code where the session also shows the old code was wrong: the user said so, a bug was being fixed, a test failed, or a review flagged it. An edit to an existing **Verify skill** is a Correction too: an agent edits one only when it steered the agent wrong. Who wrote the old code, a person or an agent, does not matter.

Old code is a line the session's diff removed or changed that was committed before the session's first commit, or was already in `HEAD` when the session made no commits. `git blame` on the pre-change version names that commit. A change that follows a changed requirement is new work.

Code the session itself wrote stays with the session's own review loop, however soon it was fixed. Only a mistake in it that the reviewer let through reaches a rule, through the reviewer-missed-a-mistake bar under **Coding standards**.

A *lesson* is a Correction whose fix points to a pattern future code could repeat. Route each Correction to the first outcome that fits:

- a Verify skill edit → a check in that skill's Doctor section when a check could have caught what steered the agent wrong, else record nothing — the edit already holds the lesson;
- a mistake a change to the code's shape could rule out → a **Structural fix** (see **File**);
- a mistake a check could catch → **Automated checks**;
- the old code broke a rule the Coding standards already hold → the reviewer-missed-a-mistake bar;
- a one-off fact, such as a wrong constant → record nothing;
- any other lesson → a new Coding standards rule.

For each lesson, search the codebase for other copies of the corrected pattern: the next agent copies what it finds. The copies go into the lesson's Issue, else onto the not-applied list as **High-priority**.

A lesson that contradicts a rule already written changes or removes that rule, so the Coding standards keep one rule on the point.

Write the rule into the repo's existing Coding standards: the file in `.agents/refs/` that holds them, else a root `CODING_STANDARDS.md` or `CONTRIBUTING.md`, else create `.agents/refs/coding-standards.md`. A Correction in a file this repo does not own still writes its rule here.

## Categories

Check every item. *Use when* is the evidence bar. Every suggestion is something this session demonstrated.

- **Navigation** — would a **context pointer** have shortened the hunt? An analyzer or lint project that no steering file points to is one. *Use when* the session took a long time to find a piece of information.
- **Automated checks** — the strongest mechanism the repo can carry that would have caught a mistake this session made: a type that cannot hold the bad state, then a static analysis rule, test, or CI rule, then a shared helper, then a runtime check. Static analysis is a rule in the repo's own analyzer or lint project, such as a Roslyn analyzer or an ESLint plugin, or a setting in its lint config. Read the repo's own check commands first (its build tool's lint or check scripts, its CI workflow), and find where it keeps its checks through the steering files and build config: a check that already exists but is not wired in, or is silently broken, is the finding, not a new check. A check that only configures a tool the repo already runs is applied; a check that needs new code — a type, an analyzer rule, a test, a helper — is filed with the lesson (see **File**). Applying a check deletes the rule it now enforces from the Coding standards and `AGENTS.md` / `CLAUDE.md`. *Use when* the agent made a mistake a check could have caught.
- **Coding standards** — a new, removed, or clarified rule for the reviewer (`/code-review`, `.agents/refs/`, or the repo's standards file). *Use when* the reviewer missed a mistake, or a **Correction** is a *lesson*.
- **AGENTS.md load** — steering in `AGENTS.md` / `CLAUDE.md` (repo or global) that belongs in coding standards or a check instead. *Use when* that file is carrying more than **context pointers**.
- **Tool economy** — expensive calls that could be cheaper, or a custom tool that wastes tokens. *Use when* the session made an expensive call.
- **No-ops** — instructions in steering files that do not change behaviour. *Use when* those files are large.
- **Information access** — logs, readonly third-party access, or other information the agent lacked. A running app checked by hand in a repo with no **Verify skill** is **High-priority**: run `/setup verify`. *Use when* a piece of information the session needed was unavailable.

## Apply

Rank by how often the pain will recur and how much it costs. An every-turn context-load problem outranks a one-off expensive call.

**High-priority** is pain that will recur every turn or every session. It includes a judgement-call coding standard, a new configuration check this session demonstrated, and a *lesson*'s rule (see **Corrections**). Apply those without asking to **Owned files**. Each edit is the smallest change that encodes what this session demonstrated. A new check that would fail on the current branch still applies.

Owned-file high-priority edits: one commit.

A file that is not an **Owned file**, or a write or commit that cannot complete: that item is not applied; continue the rest.

Do not start `/code-review` on these edits.

## File

A **Structural fix** changes the shape of the code, wider than one type, so the mistake cannot recur: a boundary, one shared path in place of copies, a module split. It and a check that needs new code are product changes that need review, so `/retro` files them instead of applying them.

1. List the open Issues. One that already covers the fix gets this session's evidence as a comment, and filing stops there.
2. Otherwise file one Issue per lesson in `needs-triage`, category `enhancement`. Its body names the mistake the session corrected, the Structural fix, the check and where it goes with a link to the repo's own steps for adding one, and every copy of the pattern.
3. Apply the lesson's interim guard now: the first outcome that applies without new code — a configuration check, else a Coding standards rule. The Issue names it, to delete when the fix lands.

A fix for a file this repo does not own is not filed; it stays in the summary. A filing that cannot complete moves the item to the not-applied list as **High-priority**, saying why.

## Present

Two lists in chat: applied, then not applied. Omit an empty list.

Applied items: the path in this tree, concrete enough to undo, and each Issue filed or commented on, by its reference.

Not-applied items: **High-priority** first, labelled, then the rest. Each names the file to edit, concrete enough to apply by hand, and what this session did that shows the need — the reader applies it in another session that did not see this one. An **Owned file** is the path in this tree. A plugin skill is `skills/<name>/...` in this plugin. A user-global file is the host path, looked up.

Nothing to apply and nothing to list → one line that the retrospective found nothing, so it is clear it ran.

No retrospective file.

**Done** when those lists are in the chat, or that one line is.
