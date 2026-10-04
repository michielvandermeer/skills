# Each repo describes its own Tracker, and every piece of work is one Issue

A repo keeps its Issues in whatever Tracker it already uses: local Markdown, GitHub Issues, Jira, or another system. It describes that Tracker in a Tracker ref at `.agents/refs/tracker.md`. `/setup` writes the ref from one of the Tracker templates the plugin ships, and the repo may then edit it freely. The skills name operations — file, read, list by status, rewrite the body, set status, comment, link, close, and the closing reference a landing commit carries — and the ref says how each one works there. A repo with no ref uses the local template as shipped, so a repo that does nothing keeps working.

Most people using these skills work in Jira, some in GitHub Issues, and the owner has moved repos such as mvdmio-suite to GitHub Issues. A tracker fixed to local files split their work across two places.

Ideas, triaged Issues, and Specs are now one kind, the Issue. Only its status tells them apart: `needs-triage`, `needs-info`, `needs-grilling`, `needs-human`, `wayfinding` for a Map, and `ready-for-agent` or `ready-for-human` once it carries a Spec. Turning a rough thought into a Spec rewrites the same Issue, so no skill deletes one document and writes another in its place.

## Considered Options

- One fixed local tracker, with no setup per repo. Rejected: it cannot follow work into the tracker a team already uses.
- The plugin owns the workflow for each tracker, and the ref only names one, with its settings and notes. Rejected: the owner wants the ref to belong to the repo outright. A team's own workflow fits without a plugin change, and a copy going stale when a template changes is the accepted cost.
- Specs stay local files while the rest moves. Rejected: a piece of work would live in two places, and "delete one, write another" would survive at the step where it costs most.

## Consequences

- An implement run reads its Issue and never writes to the Tracker ([ADR-0028](0028-implement-never-leaves-the-repository.md)). Its landing commit carries the ref's closing reference, such as `Closes #42`. On a Tracker with none, the run's final report names the Issue for the user to close.
- The run copies the Spec into its Step folder when it starts, so an edit in the Tracker during the run cannot change it.
- A Map is an Issue in `wayfinding`, and its Decision tickets are its children. The Map's own Issue becomes the first Spec it ends in.
- `/to-spec` drafts a Spec in a temporary file for the Validator and then writes it to the Issue in one update, so watchers get one notification.
- An old `issue-tracker.md` or `triage-labels.md` is inert. `/setup` reads it for its suggestion and offers to delete it.
- `/doctor` converts old local Ideas, Specs, and Issues into the local template's shape only in a repo with no Tracker ref. In a repo with a ref, it leaves tracker documents alone.
