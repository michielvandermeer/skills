# Report schema

Write one file: `.agents/codebase-audits/<timestamp>/report.md`.

Every section below is always present. Human-facing sentences hold the `/plain-language` bar. Paths stay paths. IDs stay IDs.

## What we checked

One row per subsystem:

| ID | Name | Ownership boundary | Key files | Interfaces, call sites, tests | Status |

Status is `queued`, `in review`, `recommend`, or `skip`. Every row names an exact boundary.

## Recommendations

Each accepted recommendation, assigned to one subsystem ID, carrying every field from [WORKER.md](WORKER.md) plus:

- **Coordinator verdict:** accepted, narrowed, or demoted — and why
- **Authoritative subsystem:** the one ID that owns it

## Parts we left as they are

Every `skip`, with the reason.

## Patterns that span subsystems

Cross-cutting concerns workers named. Recorded here, not solved here.

## Duplicates we dropped

Which finding superseded which, and why.

## What to do first

Ranked recommendations: impact, confidence, effort, blast radius, prerequisites. The best first implementation slices, named.

## How this audit ran

Append-only log: each dispatch, harvest, accept, reject, demote, and omission, with the reason.
