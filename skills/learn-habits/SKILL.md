---
name: learn-habits
description: Learn a person's grilling Habits into their Grilling profile. Use when a grilling session ends, or when the user wants their profile rebuilt from past sessions.
argument-hint: "[window, such as past month or last 50]"
---

A **Grilling profile** holds one person's **Habits** in this repo, at `.agents/refs/profiles/<name>.md`, so grilling can predict which option each person would pick. It learns only from that person's grilling sessions in this repo; the same person may choose differently elsewhere. See [ADR-0063](../../docs/adr/0063-grilling-profiles-live-in-the-repo-per-person.md).

## Whose profile

The person is whoever runs this session: `git config user.email`. When that is empty, stop and say that no profile can be found or written without it.

Their profile is the file in `.agents/refs/profiles/` whose `Email:` line matches. None matches → create it, named after `git config user.name` in kebab case (`ana-silva.md`). Write only this person's profile; a teammate's file is theirs to write from their own sessions.

## Two uses

**After a session** — another skill loaded this one. Read the Rounds and answers in this conversation. No answered Round → change nothing, commit nothing, and say so in one line. Otherwise fold this one session into the profile under [Habit rules](#habit-rules): record each Habit that applied, note new patterns, promote a pattern its third session shows, and update the counts.

**Typed, to rebuild** — the user typed `/learn-habits`. Rebuild the profile from scratch over a window: the last 100 grilling sessions in this repo, or the window the argument names. A rebuild replaces the whole file.

1. **Find the sessions.** Read the session logs of every host on this machine, not only this one. Look up where each keeps them; today Claude Code keeps `~/.claude/projects/<cwd with / as ->/<session>.jsonl` (skip `/subagents/`), and Grok keeps `~/.grok/sessions/<url-encoded cwd>/<session>/`, where only a session whose `prompt_context.json` says `"audience": "primary"` is top-level. A worktree's sessions belong to its repo. A grilling session is one where an assistant message holds a `## Round N` heading and an option marked `← recommended`, whichever skill ran it; that text inside a file the session merely read is not a Round.
2. **Read them in batches.** Dispatch `skills:explorer` sub-agents, about 15 sessions each, in parallel. Each returns one record per answered Question: session date, the kind of question in a few plain words, the options, which one was recommended, what the person picked or wrote, any `*Your habit:*` line and the Habit it named, and the person's stated reason, paraphrased. Carry their records, never the logs.
3. **Build** the profile from the records under [Habit rules](#habit-rules).

## Habit rules

An **override** is an answer other than the recommended option, the person's own words included. An answer that corrects a fact about the domain, or what the person meant, is a missing fact rather than a Habit — leave it to the glossary and the ADRs.

- **A pattern** is overrides that go the same way on the same kind of question. State it as a rule that names that kind of question: "include every related area when asked where a change should stop", never a bare direction such as "prefers wider scope" — two Habits going opposite ways on different kinds of question are both true.
- **A Habit** is a pattern seen in at least 3 sessions. A pattern seen in 1 or 2 stays under `## Patterns` until a third session shows it.
- **Its record** is every question it applied to, last 10 kept, oldest first: `✓` when the person picked what the Habit points to, `✗` when they went the other way. A question where a `*Your habit:*` line moved the recommendation counts, accepted or not.
- **Drop** a Habit when its last 10 hold more `✗` than `✓`.
- Merge Habits that overlap. Every grilling session reads every profile, so keep the file short. Paraphrase; quote nothing.

Run `/plain-language` before writing: teammates read the profile too.

## Profile shape

```md
# Grilling profile: Ana Silva

Email: ana@example.com
Sessions: 27, from 2026-08-28 to 2026-10-09
Picked the recommendation: 131 of 180 answers (73%)

## Habits

- **Include every related area when asked where a change should stop.** 9 sessions, last 2026-10-09. Last 10: ✓✓✗✓✓✓✓✓✗✓
- **Leave out a safeguard for a case that has no users or data yet.** 6 sessions, last 2026-10-07. Last 10: ✓✓✓✓✓✓

## Patterns

- Name a new setting the way the nearest existing one is named. 2 sessions, last 2026-10-02.
```

## Commit

Stage the profile by name and commit it on its own — `learn-habits: <first name>'s Grilling profile`, saying whether it added one session or rebuilt from a window — with no Changelog entry.

**Done** when that commit is made, or the one line saying why nothing changed is in the chat.
