# Tracker: Jira

Issues live as Jira issues in one Jira project. Use the Jira MCP tools this session has, writing text in the format each tool takes. When the session has none, stop and say so.

## Settings

- Site: `<site>.atlassian.net`
- Project key: `<KEY>`
- Issue type for Issues: `<type>`
- Issue type for Decision tickets: `<child type>`
- Done transition: `<done>`
- Not-planned transition: `<not planned>`
- Smart commits: `<yes or no>` — whether Jira acts on commit messages pushed to this repo

## Issues

- **Reference**: the issue key, such as `<KEY>-123`, or its URL. A run's slug is the key plus the summary, in kebab case, such as `<key>-123-show-taken-opnemen`; the leading key finds the Issue a slug names.
- **File**: create an issue of the Issues type in the project, with the summary, the description, and the status, category, and context labels.
- **Read**: fetch the issue with its description, labels, workflow status, comments, issue links, and parent.
- **Claim**: read the assignee and the current user. When another user is assigned, stop and name them. When the current user is, the Issue is claimed. With no assignee, assign the issue to the current user and read it again; when another user is now assigned, stop; otherwise the Issue is claimed. The claim stands until the issue's status category is Done or the user clears it.
- **List by status**: search with JQL `project = <KEY> AND labels = <status> AND statusCategory != Done`. `needs-triage` is every open issue that carries no status label.
- **Rewrite the body**: replace the description.
- **Set status**: swap the status label. An issue carries one status label at a time; its workflow status stays where the team put it.
- **Set category**: swap the category label.
- **Comment**: add a comment.
- **Link as blocked by**: an issue link of type Blocks, from the blocker to this issue. After creating it, check the direction: the blocker reads "blocks" and this issue "is blocked by". A blocker is open until its status category is Done.
- **Close as done**: comment, then run the Done transition.
- **Close as not planned**: comment why, then run the not-planned transition.
- **Closing reference**: with smart commits on, a `<KEY>-123 #<done>` line in the landing commit's message, the Done transition's name in lower case with hyphens for spaces. Jira runs the transition when that commit is pushed. A blocker has landed on a branch when `git log <branch> --grep "<KEY>-123 #"` finds a commit. With smart commits off, there is no closing reference.

## Statuses

Each status is a label of the same name: `needs-triage`, `needs-info`, `needs-grilling`, `needs-human`, `wayfinding`, `ready-for-agent`, `ready-for-human`. The category is the `bug` or `enhancement` label. In a repo with a `CONTEXT-MAP.md`, the context is a label named and picked as the plugin's `skills/domain-modeling/CONTEXT-PATHS.md` names and picks a context subfolder, `common` included. Jira creates a label the first time it is used.

## Maps and Decision tickets

A Map is an Issue labelled `wayfinding`. Its Decision tickets are child issues of the Decision ticket type, with the Map as parent.

- **File a ticket**: create a child issue under the Map, labelled `wayfinder-<type>` — `research`, `prototype`, `grilling`, or `task`.
- **Claim**: assign the ticket to the current user, before any other work. A ticket with no assignee is unclaimed.
- **Blocked by**: as for Issues.
- **List the tickets**: JQL `parent = <map key> ORDER BY created`, with each ticket's status category, assignee, and blockers.
- **List the frontier**: JQL `parent = <map key> AND statusCategory != Done AND assignee is EMPTY ORDER BY created`, dropping any ticket with an open blocker.
- **Resolve**: comment the answer under an Answer heading, run the Done transition, and add a line linking the ticket to the Map's Decisions so far.
- **Rule out of scope**: comment why, then run the not-planned transition.
