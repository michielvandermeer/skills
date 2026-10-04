# Tracker: local Markdown

Issues live as Markdown files in this repo, under `.agents/issues/`. Git is their history.

## Settings

None.

## Issues

An Issue is one file, `.agents/issues/<slug>.md`, its slug kebab-case from its title. In a repo with a `CONTEXT-MAP.md` it sits one folder deeper, `.agents/issues/<context>/<slug>.md`, with the context named and picked as the plugin's `skills/domain-modeling/CONTEXT-PATHS.md` says, and a new slug must not already exist in another context folder. Under the H1 sit a `Status:` line, a `Category:` line when triage set one, and a `Blocked by:` line when another Issue must land first. The body follows; `## Comments` ends the file.

- **Reference**: the path, or the slug alone. A run's slug is the Issue's slug.
- **File**: write the file. The session commits it with its other files.
- **Read**: read the file.
- **List by status**: the Issue files whose `Status:` line holds that status. Files inside a Map's folder are Decision tickets, not Issues.
- **Rewrite the body**: replace everything between the header lines and `## Comments`.
- **Set status**: edit the `Status:` line.
- **Set category**: write or edit the `Category:` line.
- **Comment**: append under `## Comments`, starting with the date.
- **Link as blocked by**: add the blocker's slug to `Blocked by: <slug>, <slug>`. A blocker is open while its file exists on the branch being checked.
- **Close as done**: delete the file, and a Map's folder with it, in the commit that finishes the work. Remove its slug from every other Issue's `Blocked by:` line.
- **Close as not planned**: delete the file in the session's commit. The session's summary says why.
- **Closing reference**: the landing commit closes the Issue as done above. The message carries nothing.

## Statuses

The `Status:` line holds the status as written: `needs-triage`, `needs-info`, `needs-grilling`, `needs-human`, `wayfinding`, `ready-for-agent`, or `ready-for-human`. An Issue file with no `Status:` line is `needs-triage`. `Category:` holds `bug` or `enhancement`.

## Maps and Decision tickets

A Map is an Issue in `wayfinding`. Its Decision tickets are files in a folder beside it named for its slug, `.agents/issues/<map-slug>/<NN>-<slug>.md`, numbered from `01`. The file name is the ticket's identity.

- **File a ticket**: write the file with a `Type:` line under the H1: `research`, `prototype`, `grilling`, or `task`.
- **Claim**: set `Status: claimed` and save it in the working copy the user invoked, before any other work. A ticket with no `Status:` line is unclaimed.
- **Blocked by**: a `Blocked by: NN, NN` line naming sibling tickets. A ticket is unblocked when every ticket it names is `resolved`.
- **List the tickets**: every file in the folder, with its `Status:` and `Blocked by:` lines.
- **List the frontier**: the tickets in the folder with no `Status:` line whose blockers are all resolved, lowest number first.
- **Resolve**: append the answer under `## Answer`, set `Status: resolved`, and add a line linking the ticket to the Map's Decisions so far.
- **Rule out of scope**: set `Status: out-of-scope`.

The commit that turns the Map into its first Spec deletes the Map's folder.
