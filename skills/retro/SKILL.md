---
name: retro
description: Read a window of past sessions, apply high-priority changes this repository owns for lessons that repeat, file the structural ones as Issues, and summarise the rest.
argument-hint: "[window, such as past month or last 50]"
disable-model-invocation: true
model: sonnet
effort: high
---

A **Retrospective** reads a **Window** of past sessions and acts only on a **Lesson** at least three of them show: it applies **High-priority** environment changes to **Owned files** without asking, files each **Structural fix** as an Issue, then summarises. `/code-review` still reviews the product diff; `/retro` reads it only to find **Corrections**.

Run `/writing-for-agents` for how a steering edit is written, and read [`technical-writing/SKILL.md`](../technical-writing/SKILL.md) and follow it before an Issue or the summary — `/technical-writing` does not load as a skill. Which mechanism a Lesson gets follows "Encode lessons in structure" in [code-review/PRINCIPLES.md](../code-review/PRINCIPLES.md): agents copy what exists and take the shortest path, so code that makes the wrong thing impossible beats a check, and a check beats prose.

Issues live in the repo's **Tracker**: carry out each operation on one — file, list, comment — as `.agents/refs/tracker.md` says, or as [setup/LOCAL.md](../setup/LOCAL.md) says when the repo has no ref.

## Window

The **Window** is the last 100 sessions in this repo, or what the argument names. Find them in the logs [learn-habits/SESSION-LOGS.md](../learn-habits/SESSION-LOGS.md) names. Every top-level session counts, this one included when it did work before `/retro` started. Skip a session that did nothing but run `/retro`.

A Window of fewer than three sessions stops here: say how many it held, and that three is the minimum.

## Sources

Read the Window in batches. Dispatch `skills:explorer` sub-agents, about 5 sessions each, in parallel. Hand each its session paths and the absolute path of this file, built from the folder the host loaded it from and checked with `ls`, so it reads **Corrections** and **Categories** itself. Each judges one session at a time and returns one record per moment a session fits either: the session's date, the Correction or category, what happened and what in the session shows it, and the files and commits involved. Carry their records, never the logs.

**Steering files** always include the repo's `AGENTS.md` / `CLAUDE.md` and the host's global always-loaded agent files, plus any file a record names.

A session's code changes are the commits its log records. An implement run's change is its landing commit: once the run lands, its other commits are on no branch.

## Corrections

A **Correction** is a change to old code where the session also shows the old code was wrong: the user said so, a bug was being fixed, a test failed, or a review flagged it. An edit to an existing **Verify skill** is a Correction too: an agent edits one only when it steered the agent wrong. Who wrote the old code, a person or an agent, does not matter.

Old code is a line the session's diff removed or changed that was committed before the session's first commit, or was already in `HEAD` when the session made no commits. `git blame` on the pre-change version names that commit. A change that follows a changed requirement is new work.

Code the session itself wrote stays with the session's own review loop, however soon it was fixed. Only a mistake in it that the reviewer let through reaches a rule, through the reviewer-missed-a-mistake bar under **Coding standards**. The session is the boundary, never the Window: code an earlier session wrote is old code to the session that fixes it.

A Correction whose fix points to a pattern future code could repeat shows a **Lesson**. Route each Lesson that clears **Lessons** to the first outcome that fits:

- a Verify skill edit → a check in that skill's Doctor section when a check could have caught what steered the agent wrong, else record nothing — the edit already holds the Lesson;
- a mistake a change to the code's shape could rule out → a **Structural fix** (see **File**);
- a mistake a check could catch → **Automated checks**;
- the old code broke a rule the Coding standards already hold → the reviewer-missed-a-mistake bar;
- a one-off fact, such as a wrong constant → record nothing;
- any other Lesson → a new Coding standards rule.

A Lesson whose rule cannot name a kind of change is a one-off fact, unless an earlier outcome, such as a check, took it.

For each Lesson, search the codebase for other copies of the corrected pattern: the next agent copies what it finds. The copies go into the Lesson's Issue, else onto the not-applied list as **High-priority**.

The Coding standards keep one rule on the point:

- A Lesson that contradicts a rule already written changes or removes it.
- A Lesson the rule already covers adds nothing to it, even when the rule is outside the shape below: `/doctor` trims it.
- A Lesson that shows the rule too narrow rewrites it, in the same commit, to name the wider kind of change. A new case is never appended to a rule.
- A rule `/retro` changes that is itself outside the shape below is rewritten to the shape below in the same commit. Rules no Lesson touches stay as they are.

Write the rule into the repo's existing Coding standards: the file in `.agents/refs/` that holds them, else a root `CODING_STANDARDS.md` or `CONTRIBUTING.md`, else create `.agents/refs/coding-standards.md`. A Correction in a file this repo does not own still writes its rule here.

**Rule shape.** Every rule `/retro` writes or changes, the **File** step's interim guard included, names a kind of change, never one file, type, or Issue, and reads true to someone who never saw the incident. Write only what every session behind the Lesson shares. It is one imperative line of at most 40 words, with at most one short example or reason and at most one `(#n)` or commit reference ([ADR-0081](../../docs/adr/0081-a-coding-standards-rule-is-one-short-line.md)).

A rule holds none of: an incident story, a Sentry or log ID, an error message or stack frame, a figure from one run, a path or symbol only the corrected bug had (unless it is the rule's subject), a procedure for probing, reproducing, or bisecting, a note that the rule is interim or to be deleted. Each goes where a reader who wants it looks:

- The evidence goes in the commit message, and in the Issue when one is filed or commented on.
- The note to delete an interim rule goes in the Issue, which **File** makes name the rule.
- An error signature goes in the repo's triage document when the Coding standards' folder holds one, and nowhere when it holds none. `/retro` creates no triage document.

## Categories

Check every item against each session. *Use when* is the evidence bar.

- **Navigation** — would a **context pointer** have shortened the hunt? An analyzer or lint project that no steering file points to is one. *Use when* the session took a long time to find a piece of information.
- **Automated checks** — the strongest mechanism the repo can carry that would have caught a mistake a session made: a type that cannot hold the bad state, then a static analysis rule, test, or CI rule, then a shared helper, then a runtime check. Static analysis is a rule in the repo's own analyzer or lint project, such as a Roslyn analyzer or an ESLint plugin, or a setting in its lint config. Read the repo's own check commands first (its build tool's lint or check scripts, its CI workflow), and find where it keeps its checks through the steering files and build config: a check that already exists but is not wired in, or is silently broken, is the finding, not a new check. A check that only configures a tool the repo already runs is applied; a check that needs new code — a type, an analyzer rule, a test, a helper — is filed with the Lesson (see **File**). Applying a check deletes the rule it now enforces from the Coding standards and `AGENTS.md` / `CLAUDE.md`. *Use when* the agent made a mistake a check could have caught.
- **Coding standards** — a new, removed, or clarified rule for the reviewer (`/code-review`, `.agents/refs/`, or the repo's standards file). *Use when* the reviewer missed a mistake, or a **Correction** shows a **Lesson**.
- **AGENTS.md load** — steering in `AGENTS.md` / `CLAUDE.md` (repo or global) that belongs in coding standards or a check instead. *Use when* that file is carrying more than **context pointers**.
- **Tool economy** — expensive calls that could be cheaper, or a custom tool that wastes tokens. *Use when* the session made an expensive call.
- **No-ops** — instructions in steering files that do not change behaviour. *Use when* those files are large.
- **Information access** — logs, readonly third-party access, or other information the agent lacked. A running app checked by hand in a repo with no **Verify skill** is **High-priority**: run `/setup verify`. *Use when* a piece of information the session needed was unavailable.

## Lessons

Group the records into **Lessons**: two sessions show the same Lesson when one rule or check would have prevented both. Count sessions, not occurrences. Every suggestion is a Lesson.

Read today's files and drop a Lesson they already fix: a Window reaches back past earlier fixes.

Sort what remains by how many sessions show it, whatever its category:

- Three or more: it goes on to **Apply** and **File**.
- Two: it goes on the not-applied list with its count.
- One: it adds to the count **Present** gives.

## Apply

Rank by how often the pain will recur and how much it costs. An every-turn context-load problem outranks a one-off expensive call.

**High-priority** is pain that will recur every turn or every session. It includes a judgement-call coding standard, a new configuration check, and a Correction's rule (see **Corrections**). Apply those without asking to **Owned files**. Each edit is the fewest words that state what the sessions share, not the most detailed record of them. A new check that would fail on the current branch still applies.

Before the commit, count each rule written or changed with `wc -w`, leaving out a leading `[judgement]` or `[hard]` marker, and rewrite any over 40 words.

Owned-file high-priority edits: one commit. Its message lists, for each rule written or changed, the sessions that showed the Lesson and the evidence left out of the rule.

A file that is not an **Owned file**, or a write or commit that cannot complete: that item is not applied; continue the rest.

Do not start `/code-review` on these edits.

## File

A **Structural fix** changes the shape of the code, wider than one type, so the mistake cannot recur: a boundary, one shared path in place of copies, a module split. It and a check that needs new code are product changes that need review, so `/retro` files them instead of applying them.

1. List the open Issues. One that already covers the fix gets the sessions' evidence as a comment, and filing stops there.
2. Otherwise file one Issue per Lesson in `needs-triage`, category `enhancement`. Its body names the mistake the sessions corrected, the Structural fix, the check and where it goes with a link to the repo's own steps for adding one, and every copy of the pattern.
3. Apply the Lesson's interim guard now: the first outcome that applies without new code — a configuration check, else a Coding standards rule, in the shape **Corrections** sets. The Issue names it, to delete when the fix lands.

A fix for a file this repo does not own is not filed; it stays in the summary. A filing that cannot complete moves the item to the not-applied list as **High-priority**, saying why.

## Present

Two lists in chat: applied, then not applied. Omit an empty list. Close with one line: how many sessions the Window held, and how many Lessons only one session showed.

Applied items: the path in this tree, concrete enough to undo, and each Issue filed or commented on, by its reference.

Not-applied items: **High-priority** first, labelled, then the rest. Each names the file to edit, concrete enough to apply by hand, and what the sessions did that shows the need, with how many showed it — the reader applies it in a session that saw none of them. An **Owned file** is the path in this tree. A plugin skill is `skills/<name>/...` in this plugin. A user-global file is the host path, looked up.

Nothing to apply and nothing to list → that closing line alone, saying the retrospective found nothing else, so it is clear it ran.

No retrospective file.

**Done** when the closing line is in the chat, after any lists.
