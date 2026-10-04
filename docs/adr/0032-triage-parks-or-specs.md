# Triage parks unclear work; it does not grill

A `/triage` run starts from a seed the maintainer hands it — an Issue, a report, or a query such as every `needs-triage` Issue — and ends each distinct problem in one of three ways. When the solution is clear, `/to-spec` rewrites the problem's Issue into a Spec, or files one. When it is not, the Issue is parked in `needs-info`, `needs-human`, or `needs-grilling` with a comment saying why, and unclear work waits for a later `/grill-with-docs` session. Rejected or already-implemented work is not filed, and an Issue that holds it is closed as not planned. An explicit status in the seed — `spec this`, `ready-for-agent`, `ready-for-human`, or a park's name — is the maintainer's call on whether the solution is clear, and `/triage` follows it. When one Issue holds several problems, it keeps the first, and each other problem is filed as a new Issue.

Grilling in-session was rejected so `/triage` can sort a pile of reports without holding a design interview for each unclear one. Recording rejections as `wontfix` Issues and `.out-of-scope/` notes was rejected because those documents were not used. Listing the Tracker when given nothing was rejected: the maintainer always brings the seed, and `/triage` asks for one when there is none.

## Consequences

- A Spec is the only agent-ready document, and becoming one rewrites the same Issue, so no second live card sits next to it ([ADR-0001](0001-each-repo-describes-its-tracker.md)).
- `needs-triage` marks an Issue nobody has triaged yet. `needs-human` waits on a secret or a manual test, while `ready-for-human` carries a Spec a person builds. There is no `wontfix` status.
- A leftover `.out-of-scope/` directory in a consuming repo is inert.
