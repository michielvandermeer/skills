# Fixed local-markdown issue tracker, no per-repo configuration

These skills are derived from Matt Pocock's skills, which support GitHub, GitLab, and local-markdown issue trackers, selected per-repo by a `setup-matt-pocock-skills` skill that scaffolds `docs/agents/issue-tracker.md` and `docs/agents/triage-labels.md`. We only ever use the local-markdown tracker (`.scratch/<feature-slug>/`), so we deleted that setup skill and inlined its local-tracker conventions directly into `triage`, `code-review`, and `wayfinder`. Triage labels are now fixed canonical strings written verbatim as `Status:`/`Category:` lines — no per-repo remapping — and the PR/MR-as-request-surface handling that `triage` and `code-review` carried for forge trackers was dropped, since the local tracker has no such concept.

(`to-spec` was inlined the same way at first, but [ADR-0002](0002-agents-doc-layout.md) moved specs out of the issue tracker entirely — see there for the current behavior.)

(The tracker's location later moved from `.scratch/<feature-slug>/` to `.agents/issues/<feature-slug>/`, with the redundant nested `issues/` subfolder dropped — see [ADR-0003](0003-tracker-under-agents.md). The fixed-local, no-per-repo-config decision recorded here is unaffected; only the path changed.)

## Consequences

- These skills can no longer be pointed at a GitHub or GitLab tracker. Restoring that would mean reintroducing the tracker-abstraction layer this decision removed.
- Any `docs/agents/issue-tracker.md`, `docs/agents/triage-labels.md`, or `docs/agents/domain.md` left over from a prior `setup-matt-pocock-skills` run in a consuming repo is now inert and safe to delete — nothing reads it anymore.
