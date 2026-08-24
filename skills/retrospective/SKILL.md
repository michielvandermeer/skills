---
name: retrospective
description: Look at a finished session and suggest environment changes so later runs go better.
argument-hint: "[session]"
disable-model-invocation: true
---

You are suggesting improvements to the agent's **environment** so later runs are cheaper or more reliable. The environment only — `/code-review` and `/improve-data-structures` own the product diff.

You are the **driving session**. A `general-purpose` sub-agent at your own model and effort **gathers**. You **present**. See [ADR-0007](../../docs/adr/0007-pinned-subagent-model-tiers.md).

If this session already presented a retrospective, say so and stop.

## Callers

**Typed.** Argument names a session, or empty for the current one. Gather, then present.

**`/implement`.** Calls Gather, then Present, around land. Timing lives in that skill. See [ADR-0019](../../docs/adr/0019-implement-ends-with-a-non-blocking-retrospective.md).

## Gather

Dispatch one `general-purpose` sub-agent. Hand it this file, `/writing-for-agents`, and the sources below. It returns the ranked list or `none`. Retry once on failure; a second failure returns `none` plus the failure line.

**Done** when every category has been applied to the evidence, and every suggestion is something this session demonstrated.

### Sources

`/implement`: Spec, Step files (Outcomes, Footprints), deviations, the review findings, branch log vs the fixed point, plus the steering files the run used.

Typed: the host's session logs for the current or named session, plus the steering files that session used. Look up log paths for this host. If the named session cannot be found, stop; the driving session presents that line. If logs for the current session are not on disk, brief the gatherer from what this conversation holds.

**Steering files** always include the repo's `AGENTS.md` / `CLAUDE.md` and the host's global always-loaded agent files, plus any file this session actually reached. See [ADR-0020](../../docs/adr/0020-retrospective-includes-global-agent-files.md).

Skills in this plugin are in scope when those skill files live in the current workspace.

### Categories

Check every item. *Use when* is the evidence bar.

- **Navigation** — would a **context pointer** have shortened the hunt? *Use when* the session took a long time to find a piece of information.
- **Automated checks** — lint, types, tests, filesystem linters that would have caught a mistake this session made. *Use when* the agent made a mistake a check could have caught.
- **Coding standards** — a new, removed, or clarified rule for the reviewer (`/code-review`, `.agents/refs/`, or the repo's standards file). *Use when* the reviewer missed a mistake.
- **AGENTS.md load** — steering in `AGENTS.md` / `CLAUDE.md` (repo or global) that belongs in coding standards or a check instead. *Use when* that file is carrying more than **context pointers**.
- **Tool economy** — expensive calls that could be cheaper, or a custom tool that wastes tokens. *Use when* the session made an expensive call.
- **No-ops** — instructions in steering files that do not change behaviour. *Use when* those files are large.
- **Information access** — logs, readonly third-party access, or other information the agent lacked. *Use when* a piece of information the session needed was unavailable.

Prefer a pointer or an automated check over a new skill. Place each suggestion where `/writing-for-agents` already puts that kind of change.

### List shape

Each suggestion is one line the driving session can hold:

```
N. repo|global  <path>  — <the change>  (<category>; <why this session demonstrated it>)
```

Rank by how often the pain will recur and how much it costs. An every-turn context-load problem outranks a one-off expensive call.

## Present

Run `/plain-language`. Present the list in that order. Number them. Each item states repo or global and the path, and is concrete enough to apply in one turn.

Nothing to suggest → one line that the retrospective found nothing, so the caller knows it ran.

**Done** when the numbered list is in the chat, or that one line is. Then stop. Applying is a new request.
