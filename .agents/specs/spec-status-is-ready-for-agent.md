# Spec Status is only ready-for-agent

Status: ready-for-agent

## Problem Statement

`/validate-spec` still treats `wontfix` as a valid Status on a Spec. It also lists `needs-triage`, `needs-info`, and `ready-for-human`. Those were Issue statuses from an older tracker, or they are Issue statuses now.

A Spec is the input to `/implement`. The only Status a Spec carries is `ready-for-agent`. There is no `wontfix` Status anywhere: `/triage` does not keep a document for work you will not do, and you do not want a slot that records a no.

An agent that is told to write a Spec, and that is told the work will not be built, reads that stale list and stamps `wontfix` on the file. The list is what makes that stamp look legal.

## Solution

`/validate-spec`'s Shape check names `ready-for-agent` as the only valid Status on a Spec. The Spec glossary says the same. Issue statuses stay on Issues. A Spec does not grow a Status for work we will not do.

## User Stories

1. As a developer, I want `/validate-spec` to accept only `ready-for-agent` on a Spec, so a `wontfix` Spec is not treated as well-formed.

2. As a Driving session writing a Spec, I want the valid Status list I read to match `/to-spec`, so I do not pick a retired value from a second list.

3. As a Driving session, I want `needs-triage` gone from that list, so I do not park a Spec in a Status Issues no longer use.

4. As a Driving session, I want `needs-info` gone from that list, so I do not copy an Issue Status onto a Spec.

5. As a Driving session, I want `ready-for-human` gone from that list, so I do not revive a Status `/triage` already replaced with `needs-human`.

6. As a developer, I want Issue files to keep `needs-info`, `needs-human`, and `needs-grilling`, so this change does not shrink the triage state machine.

7. As a developer, I want Idea docs to keep carrying no Status line, so the Shape check still differs by type.

8. As `/implement`, I want every Spec I am handed to read `ready-for-agent`, so I never have to interpret a second Status.

9. As a later reader of a Spec, I want the Status line to mean only "this is ready for `/implement`", so I do not have to remember retired labels.

10. As a Driving session that finds a Spec whose Status is an old Issue label (`needs-triage`, `needs-info`, or `ready-for-human`), I want `/validate-spec` to treat that line as a fact and set it to `ready-for-agent`, so a real Spec is not left parked.

11. As a Driving session that finds a Spec whose Status is `wontfix`, I want `/validate-spec` to flag that as a question rather than rewrite it to `ready-for-agent`, so a recorded no is not promoted into work.

12. As a developer, I want leftover `wontfix` files in other repos left unhunted, so `/validate-spec` does not become a cleaner for old trackers.

13. As a developer, I want historical Changelog entries and superseded ADRs that mention `wontfix` left as history, so this change does not rewrite the past.

14. As a developer, I want `/to-spec` left writing `Status: ready-for-agent`, so the writer and the checker agree.

15. As a developer, I want the Spec glossary to say a Spec carries `Status: ready-for-agent`, so the definition site and the checker agree.

16. As a Driving session running `/migrate-doc-layout`, I want classifying old files by the shape they already have left alone, so a legacy Status on disk can still tell the migrator what the file was.

17. As a developer, I do not want a new Status whose meaning is "we will not do this", so the checker cannot grow the slot we just closed.

## Implementation Decisions

- `/validate-spec`'s Shape check for a plan or Spec lists one valid Status: `ready-for-agent`. The other values leave that list.

- A Status that is an old Issue label (`needs-triage`, `needs-info`, `ready-for-human`) is a fact. `/validate-spec` corrects the line to `ready-for-agent` in place. A Status of `wontfix` is not a fact to rewrite into work: flag it as a question that the file should not be a Spec.

- The Spec glossary entry states that a Spec carries `Status: ready-for-agent`. It does not list Issue statuses.

- `/to-spec` already writes `ready-for-agent`. It does not change.

- `/triage`'s Issue statuses do not change. Surviving Issue states stay `needs-info`, `needs-human`, and `needs-grilling`. Rejected work is still not a document.

- No new ADR. The existing triage ADR already says there is no `wontfix` Status and that Specs carry `ready-for-agent`. This Spec deletes the stale cache of that decision.

## Testing Decisions

A good check is what `/validate-spec` accepts and what it rewrites, not the wording of the checklist item in isolation.

- A Spec whose Status is `ready-for-agent` passes the Shape check on that line.
- A Spec whose Status is `needs-triage`, `needs-info`, or `ready-for-human` has that line corrected to `ready-for-agent`.
- A Spec whose Status is `wontfix` is flagged as a question, not rewritten to `ready-for-agent`.
- An Issue with `needs-info`, `needs-human`, or `needs-grilling` is out of `/validate-spec`'s Spec Shape check.
- An Idea still has no Status line required.

This repo has no automated suite for skill prose. The check is a read of the Shape item against `/to-spec` and the Spec glossary, the way `/validate-spec` already reads a Spec against the current codebase. Prior art for dropping `wontfix` is the triage ADR that removed it from Issues.

## Out of Scope

- Stopping `/grill-with-docs` from writing a Spec when nothing will be built. That is the companion Spec `grill-with-docs-no-change-writes-no-spec`.
- Changing `/to-spec`, `/triage`, or Issue statuses.
- Hunting leftover `wontfix` files in consuming repos.
- Rewriting historical Changelog entries or superseded ADRs.
- Changing how `/migrate-doc-layout` classifies legacy files.

## Further Notes

The stale list is leftover from when a Spec carried a Status "for the triage role". Specs left the tracker. The list did not. `/to-spec` and the triage ADR already agree on `ready-for-agent` only. `/validate-spec` is the file that still contradicts them, and it is the file an agent reads when it chooses a Status.

If a consuming repo still has a Spec stamped `wontfix`, delete that file. `/validate-spec` will ask about it rather than promote it. Do not hand it to `/implement`.
