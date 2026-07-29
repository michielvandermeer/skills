# Refine owns its HTML scaffold rather than sharing the architecture review's

Both `/refine` and `/improve-codebase-architecture` render a self-contained Tailwind + Mermaid HTML report, so sharing one `HTML-REPORT.md` looks like the obvious move. We duplicated the scaffold instead. The overlap is roughly fifteen lines of CDN boilerplate; everything else in that file pulls the wrong way — its diagram patterns are mass diagrams and cross-sections, and its tone section *mandates* the `/codebase-design` vocabulary (module, interface, seam, depth). A Refinement report is read by Product and QA, and the moment a box on it says "repository" the session has changed altitude.

## Consequences

- The CDN scaffold exists twice. A future reader may take it for an oversight and try to DRY it — that consolidation is the thing this ADR exists to prevent.
- The two files diverge freely: `/refine` needs as-is/to-be flow pairs, state diagrams, and decision tables, and needs architecture diagrams to stay out.
