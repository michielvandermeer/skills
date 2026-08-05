# Refine keeps a dense session document and thin user-facing surfaces

A `/refine` session needs a full read-from-code account of today so a resume can reopen the change without re-deriving it, and a mixed Product/QA/Development room needs every spoken and shipped sentence to stay at functional altitude. We split those jobs: `session.md` is resume infrastructure and may keep code anchors; the live rounds, mid-session `session.html`, `complete.md`, `complete.html`, and Jira write-back are the only user-facing surfaces and restate today as behaviour. Mid-session HTML rewrites `How it works today` at render time rather than dual-writing a second today section, so the markdown file stays the single resume source of truth.

## Consequences

- Opening `session.md` can still expose technical prose; that is acceptable because it is not a product deliverable.
- Domain modeling in `/refine` still updates `CONTEXT.md` as terms settle, and never offers or writes ADRs — altitude stays functional, glossary still grows.
