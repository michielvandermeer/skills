---
name: what-did-i-get-done
description: Summarise what you got done over a period, from your commits, pull requests, and Issues in this repo.
argument-hint: "[period, such as yesterday or last week]"
disable-model-invocation: true
model: sonnet
effort: high
---

# What did I get done

A short status update of the work you finished in one repo over one period: what shipped, what is in review, and what moved in the Tracker.

## 1. Pin the window and the person

Turn the period into a start and an end date in local time. "Yesterday" is that one day. "Last week" is the seven days before today. With no period, take the last seven days and say so in the update.

The person is `git config user.email` for commits, and the signed-in account for the host and the Tracker: `gh api user --jq .login` on GitHub.

Done: a start date, an end date, and the person's email and account.

## 2. Gather

Run each source the repo has. A source that fails is a gap, kept with its error.

- **Commits**: `git log --all --no-merges --author=<email> --since=<start> --until=<end + 1 day> --format='%h %ad %s' --date=short`. A commit that sits on several branches under one subject, as after a rebase, counts once.
- **Pull requests**, on GitHub: `gh pr list --state all --author @me --search "updated:>=<start>" --limit 100 --json number,title,state,createdAt,mergedAt,closedAt,url`. Keep those opened, merged, or closed in the window. Add the ones you reviewed: the same command with `--search "reviewed-by:@me updated:>=<start>"` in place of `--author @me`. Another host uses its own CLI for the same three lists.
- **Issues**, in the Tracker `.agents/refs/tracker.md` names, or local Markdown when the repo has none. Keep those you filed, closed, or moved to a new status in the window.
  - GitHub: `gh issue list --state all --search "involves:@me updated:>=<start>" --limit 100 --json number,title,state,author,createdAt,closedAt,labels,url`, then the timeline of each to see what you changed.
  - Jira: JQL `project = <KEY> AND (reporter = currentUser() OR assignee = currentUser() OR status CHANGED BY currentUser()) AND updated >= <start>`.
  - Local Markdown: `git log --author=<email> --since=<start> --until=<end + 1 day> --name-status -- .agents/issues/` and the `Status:` line each commit left.

Done: every source has its list for the window, or is a gap with its error.

## 3. Write the update

Read [`technical-writing/SKILL.md`](../technical-writing/SKILL.md) and follow it — `/technical-writing` does not load as a skill. Group commits under the pull request that carried them, and an Issue under the pull request that closed it. Lead with what changes behaviour or structure for a user or a developer. Leave out formatting, import, and rename-only work. Describe what each change does, from its title, body, and diff, and leave its motive to the person.

```
<start> to <end>

<one or two sentences: the most important thing that shipped, and what else moved>

- Shipped: <change>, #<PR>
- In review: <change>, #<PR>
- Reviewed: <PR title>, #<PR>
- Tracker: <Issues filed, closed, or moved>
```

Keep only the lines that have something, at most five bullets in all, and name each gap from step 2 with its error.

Done: the update is in the chat, with its real date range.
