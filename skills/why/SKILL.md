---
name: why
description: Trace why code is the way it is, with every claim cited. Use for "why does X work this way", why a choice was made, a regression's origin, or before changing code that looks deliberate.
---

# Why

Code shows what it does. Why it exists lives in commits, pull requests, Issues, docs, chat, and incident tools, and every one of them is incomplete. The answer is a cited read of that record, with each claim marked by how well it is supported.

## 1. Pin the target and the question

The **target** is the code, pattern, feature, or decision being asked about. The **question** is what about it: a design choice, a trade-off, an edge case it guards, an outside constraint, dead code, a number, or its whole history. With a vague target, take your best reading from the conversation, say it in one line, and go on.

A guess inside the question ("I assume it's for performance?") is one candidate among others, checked like the rest.

Done: one file and line range or symbol set, and the question in one sentence.

## 2. Anchor in the code

Build the anchor yourself, before any investigator starts:

- The files and line ranges, and the key symbols.
- `git blame -L <start>,<end> <file>` for the last commit on each line, and `git log --follow --oneline -- <file>` for the history through renames.
- Pull request numbers from those commits' messages, and on GitHub `gh pr view <number> --json title,body,comments,reviews,closingIssuesReferences` for each one that changed the target.
- Issue keys and links named in commits and pull requests.

Done: the anchor lists the files, symbols, commits, pull requests, and Issue keys.

## 3. Investigate, one source per agent

Investigators do all the searching, even when source control is the only category, so this session keeps its context for weighing what they bring back. List the evidence sources this session can reach. Source control is always one. Each connected tool counts toward one category, judged by its name and tools:

1. Source control: git, the host's pull requests, comments, tests, ADRs, the changelog.
2. Tracker: the Issues the repo's `.agents/refs/tracker.md` names, such as GitHub Issues or Jira.
3. Long-form documents: Confluence, Notion, Google Docs.
4. Team chat: Slack, Teams.
5. Observability: Datadog, Grafana, New Relic.
6. Error tracking: Sentry, Rollbar.
7. Product analytics: a data warehouse such as Databricks or Snowflake.

Dispatch one `skills:explorer` per category this session can reach, all in one message, each briefed as [INVESTIGATE.md](INVESTIGATE.md) says, with that category's part of [SOURCES.md](SOURCES.md). When the target is defensive code, such as a null check, a retry, a timeout, a rate limit, a feature flag, or a size cap, add the incident part of `SOURCES.md` to every brief.

Skip a reachable category only when it provably cannot bear on the target, such as error tracking for a build script, and write the reason down. A category with no connected tool is a gap.

Done: every investigator has reported, and every category is searched, skipped with a reason, or a gap.

## 4. Write the answer

Read [EVIDENCE.md](EVIDENCE.md), then read [`technical-writing/SKILL.md`](../technical-writing/SKILL.md) and follow it — `/technical-writing` does not load as a skill. Merge the reports: one citation for an item several of them found, both sides of any contradiction. Spot-check each citation you lean on by opening it. Then write under exactly these headings, in this order, dropping only the optional ones that are empty:

- **The question**, restated in one or two sentences.
- **The code**: paths, line ranges, and symbols.
- **What we found**: each claim tagged `[Direct]` or `[Supported]`, with its citation.
- **What we can reasonably infer** (optional): each claim tagged `[Inferred]`, hedged, with the chain from evidence to claim.
- **Competing hypotheses** (optional): each with the evidence for it and what is missing.
- **What we don't know**: each gap, with the sources and searches that came up empty.
- **Sources consulted**: one line per category, including those skipped or not connected, and why.
- **Confidence**: one or two sentences on how far the answer can be trusted.

When the question comes before a change to the target, end with four lists for planning it, under these four names: **Preserve** (what the history says must keep working), **Change** (what the history no longer justifies), **Avoid** (approaches already tried and dropped), and **Risk** (what could break, and who would notice).

Done: `EVIDENCE.md` is read, every heading above is present or optional and empty, and every claim carries its tier and its citation, or sits under What we don't know.
