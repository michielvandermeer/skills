---
name: retro
description: Look at a finished session and suggest environment changes so later runs go better.
argument-hint: "[session]"
disable-model-invocation: true
---

Suggest improvements to the agent's **environment** so later runs are cheaper or more reliable. The environment only — `/code-review` and `/improve-data-structures` own the product diff.

You are the **driving session**. Run `/writing-for-agents` for where each kind of change belongs, and `/plain-language` before you present.

The argument names a session, or is empty for the current one. If this session already presented a retrospective, say so and stop.

## Sources

The host's session logs for the current or named session, plus the steering files that session used. Look up log paths for this host. If the named session cannot be found, stop and say so. If logs for the current session are not on disk, work from what this conversation holds.

**Steering files** always include the repo's `AGENTS.md` / `CLAUDE.md` and the host's global always-loaded agent files, plus any file this session actually reached. Skills in this plugin are in scope when those skill files live in the current workspace.

## Categories

Check every item. *Use when* is the evidence bar. Every suggestion is something this session demonstrated.

- **Navigation** — would a **context pointer** have shortened the hunt? *Use when* the session took a long time to find a piece of information.
- **Automated checks** — lint, types, tests, filesystem linters that would have caught a mistake this session made. *Use when* the agent made a mistake a check could have caught.
- **Coding standards** — a new, removed, or clarified rule for the reviewer (`/code-review`, `.agents/refs/`, or the repo's standards file). *Use when* the reviewer missed a mistake.
- **AGENTS.md load** — steering in `AGENTS.md` / `CLAUDE.md` (repo or global) that belongs in coding standards or a check instead. *Use when* that file is carrying more than **context pointers**.
- **Tool economy** — expensive calls that could be cheaper, or a custom tool that wastes tokens. *Use when* the session made an expensive call.
- **No-ops** — instructions in steering files that do not change behaviour. *Use when* those files are large.
- **Information access** — logs, readonly third-party access, or other information the agent lacked. *Use when* a piece of information the session needed was unavailable.

Prefer a pointer or an automated check over a new skill.

## Present

Rank by how often the pain will recur and how much it costs. An every-turn context-load problem outranks a one-off expensive call. Number them. Each item states `repo` or `global` and the path, and is concrete enough to apply in one turn.

Nothing to suggest → one line that the retrospective found nothing, so it is clear it ran.

**Done** when the numbered list is in the chat, or that one line is. Then stop. Applying is a new request.
