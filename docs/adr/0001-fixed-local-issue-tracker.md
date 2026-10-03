# Fixed local-markdown issue tracker, no per-repo configuration

These skills are derived from Matt Pocock's skills, which support GitHub, GitLab, and local-markdown issue trackers, selected per-repo by a `setup-matt-pocock-skills` skill that scaffolds `docs/agents/issue-tracker.md` and `docs/agents/triage-labels.md`. We only ever use the local-markdown tracker (`.scratch/<feature-slug>/`), so we deleted that setup skill and inlined its local-tracker conventions directly into `triage`, `code-review`, and `wayfinder`. Triage labels are now fixed canonical strings written verbatim as `Status:`/`Category:` lines — no per-repo remapping — and the PR/MR-as-request-surface handling that `triage` and `code-review` carried for forge trackers was dropped, since the local tracker has no such concept.

(`to-spec` was inlined the same way at first, but [ADR-0002](0002-agents-doc-layout.md) moved specs out of the issue tracker entirely — see there for the current behavior.)

(The tracker's location later moved from `.scratch/<feature-slug>/` to `.agents/issues/<feature-slug>/`, with the redundant nested `issues/` subfolder dropped — see [ADR-0003](0003-tracker-under-agents.md). The fixed-local, no-per-repo-config decision recorded here is unaffected; only the path changed.)

(A GitHub-issue seed is a later carve-out for `/triage` only. That run publishes on the GitHub issue, and every other seed still uses the local Issue files. See Consequences.)

## Consequences

- These skills are not pointed at a GitLab tracker, and they still have no per-repo tracker configuration and no label remapping. `/triage` alone publishes on a GitHub issue when the seed is that issue (a GitHub issue URL or `owner/repo#number`): a parked ending is a comment plus `needs-info`, `needs-human`, or `needs-grilling`, a not-filed ending is a comment that says why, with no parked label, and then the issue is closed, and a further distinct problem is a new GitHub issue. That run writes no `.agents/issues/` file, and a parked or not-filed ending opens no pull request. A Buildable ending leaves the issue open, replaces the body with the Spec, and sets `ready-for-agent`. `/to-spec` may still write a repo file; a pull request for that file says in its description that the issue body is the copy people read. Every other seed still uses the local Issue files this ADR fixes. Wayfinder is unchanged. Restoring a configurable GitHub or GitLab tracker would mean reintroducing the tracker-abstraction layer this decision removed.
- Any `docs/agents/issue-tracker.md`, `docs/agents/triage-labels.md`, or `docs/agents/domain.md` left over from a prior `setup-matt-pocock-skills` run in a consuming repo is now inert and safe to delete — nothing reads it anymore.
