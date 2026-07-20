# Canonical `.agents/` layout for specs, ideas, references, and architecture reviews

These skills previously had no single fixed location for the documents they read and write: `validate-spec` looked for specs under `.agents/plans/`, `improve-codebase-architecture` wrote reviews to a singular `.agents/architecture-review/`, and `code-review`'s coding-standards discovery had no preferred spot at all. We fixed a canonical layout — specs at `.agents/specs/<slug>.md`, ideas at `.agents/ideas/<slug>.md`, ADRs at `docs/adr/` (unchanged), skill-supporting reference docs at `.agents/refs/`, architecture reviews at `.agents/architecture-reviews/` — and updated every skill that reads or writes these to agree on it.

As part of this, `to-spec` was decoupled from the `.scratch/` issue tracker (see [ADR-0001](0001-fixed-local-issue-tracker.md)): a spec is no longer published as a tracker ticket, just written to `.agents/specs/` carrying its own `Status:` line for the triage role. A new `migrate-doc-layout` skill was added to relocate documents in consuming repos that predate this convention — e.g. existing `.agents/plans/` directories — since it classifies by content shape rather than assuming a fixed prior location.

## Consequences

- Consuming repos with docs in the old locations (`.agents/plans/`, ad hoc reference docs, a singular `.agents/architecture-review/`) need to run `/migrate-doc-layout` once to conform.
- `code-review`'s standards-source discovery checks `.agents/refs/` first but still falls back to root-level `CODING_STANDARDS.md`/`CONTRIBUTING.md` if that's what a repo already has — `.agents/refs/` is the canonical spot for new docs, not an exclusive one.
