---
status: partially superseded by ADR-0008
---

# Canonical `.agents/` layout for references and architecture reviews

Each document the skills keep in the repo has one fixed location, and every skill that reads or writes it agrees on that location. This layout fixes three: ADRs at `docs/adr/`, skill-supporting reference docs at `.agents/refs/`, and architecture reviews at `.agents/architecture-reviews/`. Issues, and the Specs they carry, follow the repo's Tracker ([ADR-0001](0001-each-repo-describes-its-tracker.md)). `/doctor` moves documents in consuming repos that predate this layout into it, classifying each by content shape rather than assuming a fixed prior location.

## Consequences

- Consuming repos with docs in the old locations (ad hoc reference docs, a singular `.agents/architecture-review/`) are brought into line by `/doctor`, which moves them without asking in its single commit.
- Architecture reviews since moved to a folder per review, and Refinements were added on the same rule — see [ADR-0008](0008-session-output-gets-a-folder.md). The flat-file-per-document layout still holds for references.
- `code-review`'s standards-source discovery checks `.agents/refs/` first but still falls back to root-level `CODING_STANDARDS.md`/`CONTRIBUTING.md` if that's what a repo already has — `.agents/refs/` is the canonical spot for new docs, not an exclusive one.
