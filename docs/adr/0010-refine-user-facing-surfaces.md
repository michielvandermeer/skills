---
status: superseded by ADR-0036
---

# Refine keeps a dense session document and thin user-facing surfaces

A `/refine` session needs a full read-from-code account of today so a resume can reopen the change without re-deriving it, and a mixed Product/QA/Development room needs every spoken and shipped sentence to stay at functional altitude. We split those jobs: `session.md` is resume infrastructure and may keep code anchors; the live rounds, `complete.md`, and write-back to the Jira ticket or source markdown file are the only user-facing surfaces and restate today as behaviour. The Prototype is the picture during the session. There is no HTML report.

## Consequences

- Opening `session.md` can still expose technical prose; that is acceptable because it is not a product deliverable.
- Domain modeling in `/refine` still updates `CONTEXT.md` as terms settle, and never offers or writes ADRs — altitude stays functional, glossary still grows.
