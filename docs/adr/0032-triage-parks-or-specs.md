# Triage parks unclear work; it does not grill

`/triage` used to run `/grill-with-docs` in-session and treat a Spec as the only successful ending ([ADR-0014](0014-triage-ends-in-a-spec.md)). A run now starts from a seed the maintainer hands it and records one result per distinct problem: a Spec when the solution is clear, or an Issue in `needs-info`, `needs-human`, or `needs-grilling`. Unclear work waits for a later `/grill-with-docs` session. Rejected or already-implemented work is not kept as a local document.

Grilling in-session was rejected so `/triage` can sort a pile of reports without holding a design interview for each unclear one. Recording rejections as `wontfix` files and `.out-of-scope/` notes was rejected because those documents were not used. Scanning `.agents/issues/` when given nothing was rejected: the maintainer always brings the seed.

Leaving a second live card next to a Spec was already rejected in ADR-0014 and still is. On a GitHub-issue seed the issue is the Spec: its body is replaced with the Spec, it is labeled `ready-for-agent`, and it stays open.

## Consequences

- ADR-0014 is superseded. Specs remain the only agent-ready documents (`Status: ready-for-agent`).
- `needs-human` replaces `ready-for-human`. There is no `needs-triage` or `wontfix` status.
- On a GitHub-issue seed the parked Issue is that GitHub issue: a comment and one of those three labels, not a file under `.agents/issues/`. A not-filed ending is a comment that says why, with no parked label, and then the issue is closed. A Buildable ending leaves the issue open: the body is the Spec and the label is `ready-for-agent`. Every other seed still writes the local Issue file. [ADR-0001](0001-fixed-local-issue-tracker.md).
- A leftover `.out-of-scope/` directory in a consuming repo is inert.
