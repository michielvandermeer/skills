---
name: retro
description: Look at a finished session, apply high-priority changes this repository owns, and summarise the rest.
argument-hint: "[session]"
---

A **Retrospective** applies **High-priority** environment changes to **Owned files** without asking, then summarises. `/code-review` and `/improve-data-structures` still review the product diff; `/retro` reads it only to find **Corrections**.

Apply and present only when the skill the user typed is this `/retro`, or that skill has reached its own done condition.

Run `/writing-for-agents` for where each kind of change belongs, and `/plain-language` before the summary.

The argument names a session, or is empty for the current one.

## Sources

The host's session logs for the current or named session, plus the steering files that session used, plus the session's code changes. Look up log paths for this host. If the named session cannot be found, stop and say so. If logs for the current session are not on disk, work from what this conversation holds.

**Steering files** always include the repo's `AGENTS.md` / `CLAUDE.md` and the host's global always-loaded agent files, plus any file this session actually reached.

The session's code changes are the commits the session log records for the current or named session, plus any uncommitted changes still in the working tree. Take the commits from the session log: `/implement` deletes its run branch before `/retro` runs, so no branch or start commit survives to diff against.

## Corrections

A **Correction** is a change to old code where the session also shows the old code was wrong: the user said so, a bug was being fixed, a test failed, or a review flagged it. Who wrote the old code, a person or an agent, does not matter.

Old code is a line the session's diff removed or changed that was committed before the session's first commit, or was already in `HEAD` when the session made no commits. `git blame` on the pre-change version names that commit. A change that follows a changed requirement is new work.

Code the session itself wrote stays with the session's own review loop, however soon it was fixed. Only a mistake in it that the reviewer let through reaches a rule, through the reviewer-missed-a-mistake bar under **Coding standards**.

A *lesson* is a Correction whose fix points to a pattern future code could repeat. Route each Correction to the first outcome that fits:

- a mistake a check could catch → **Automated checks**;
- the old code broke a rule the Coding standards already hold → the reviewer-missed-a-mistake bar;
- a one-off fact, such as a wrong constant → record nothing;
- any other lesson → a new Coding standards rule.

A lesson that contradicts a rule already written changes or removes that rule, so the Coding standards keep one rule on the point.

Write the rule into the repo's existing Coding standards: the file in `.agents/refs/` that holds them, else a root `CODING_STANDARDS.md` or `CONTRIBUTING.md`, else create `.agents/refs/coding-standards.md`. A Correction in a file this repo does not own still writes its rule here.

## Categories

Check every item. *Use when* is the evidence bar. Every suggestion is something this session demonstrated.

- **Navigation** — would a **context pointer** have shortened the hunt? *Use when* the session took a long time to find a piece of information.
- **Automated checks** — lint, types, tests, filesystem linters that would have caught a mistake this session made. *Use when* the agent made a mistake a check could have caught.
- **Coding standards** — a new, removed, or clarified rule for the reviewer (`/code-review`, `.agents/refs/`, or the repo's standards file). *Use when* the reviewer missed a mistake, or a **Correction** is a *lesson*.
- **AGENTS.md load** — steering in `AGENTS.md` / `CLAUDE.md` (repo or global) that belongs in coding standards or a check instead. *Use when* that file is carrying more than **context pointers**.
- **Tool economy** — expensive calls that could be cheaper, or a custom tool that wastes tokens. *Use when* the session made an expensive call.
- **No-ops** — instructions in steering files that do not change behaviour. *Use when* those files are large.
- **Information access** — logs, readonly third-party access, or other information the agent lacked. *Use when* a piece of information the session needed was unavailable.

## Apply

Rank by how often the pain will recur and how much it costs. An every-turn context-load problem outranks a one-off expensive call.

**High-priority** is pain that will recur every turn or every session. It includes a judgement-call coding standard, a new check this session demonstrated, and a *lesson*'s rule (see **Corrections**). Apply those without asking to **Owned files**. Each edit is the smallest change that encodes what this session demonstrated. A new check that would fail on current master still applies.

Owned-file high-priority edits: one commit, no Changelog entry.

A file that is not an **Owned file**, or a write or commit that cannot complete: that item is not applied; continue the rest.

Do not start `/code-review` on these edits.

## Present

Two lists in chat: applied, then not applied. Omit an empty list.

Applied items: the path in this tree, concrete enough to undo.

Not-applied items: **High-priority** first, labelled, then the rest. Each names the file to edit, concrete enough to apply by hand, and what this session did that shows the need — the reader applies it in another session that did not see this one. An **Owned file** is the path in this tree. A plugin skill is `skills/<name>/...` in this plugin. A user-global file is the host path, looked up.

Nothing to apply and nothing to list → one line that the retrospective found nothing, so it is clear it ran.

No retrospective file.

**Done** when those lists are in the chat, or that one line is.
