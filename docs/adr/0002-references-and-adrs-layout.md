# Canonical `.agents/` layout for references and ADRs

Each document the skills keep in the repo has one fixed location, and every skill that reads or writes it agrees on that location. ADRs live at `docs/adr/`. Skill-supporting reference docs live at `.agents/refs/`. Issues, and the Specs they carry, follow the repo's Tracker ([ADR-0001](0001-each-repo-describes-its-tracker.md)). A session that produces several files gets a folder ([ADR-0008](0008-session-output-gets-a-folder.md)). `/doctor` moves documents in consuming repos that predate this layout into it. A known old layout moves from its path alone, so those files are not re-read one by one; every other document is classified by content shape.

## Consequences

- Consuming repos with docs in the old locations are brought into line by `/doctor`, which moves them without asking in its single commit.
- References stay one file each. The folder rule does not reach them.
- `code-review`'s standards-source discovery checks `.agents/refs/` first but still falls back to root-level `CODING_STANDARDS.md`/`CONTRIBUTING.md` if that's what a repo already has — `.agents/refs/` is the canonical spot for new docs, not an exclusive one.
