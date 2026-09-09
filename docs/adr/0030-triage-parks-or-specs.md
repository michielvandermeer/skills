# Triage parks unclear work; it does not grill

`/triage` used to run `/grill-with-docs` in-session and treat a Spec as the only successful ending ([ADR-0013](0013-triage-ends-in-a-spec.md)). A run now starts from a seed the maintainer hands it and writes one document per distinct problem: a Spec when the solution is clear, or an Issue in `needs-info`, `needs-human`, or `needs-grilling`. Unclear work waits for a later `/grill-with-docs` session. Rejected or already-implemented work is not kept as a document.

Grilling in-session was rejected so `/triage` can sort a pile of reports without holding a design interview for each unclear one. Recording rejections as `wontfix` files and `.out-of-scope/` notes was rejected because those documents were not used. Scanning `.agents/issues/` when given nothing was rejected: the maintainer always brings the seed.

Leaving a second live card next to a Spec was already rejected in ADR-0013 and still is.

## Consequences

- ADR-0013 is superseded. Specs remain the only agent-ready documents (`Status: ready-for-agent`).
- `needs-human` replaces `ready-for-human`. There is no `needs-triage` or `wontfix` status.
- A leftover `.out-of-scope/` directory in a consuming repo is inert.
