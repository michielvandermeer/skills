# Grill-with-docs writes no Spec when nothing will be built

Status: ready-for-agent

## Problem Statement

You ran `/grill-with-docs` and the session settled on not building anything. The session then wrote a Spec. A Spec is the brief `/implement` reads. A Spec that says "do nothing" is not a brief. It is a file that records a no.

You already decided those files are not useful. `/triage` does not keep a document for work you will not do. `/grill-with-docs` still always runs `/to-spec` after a confirmed Read-back, so a no still becomes a Spec.

## Solution

When the confirmed Read-back is that nothing will be built, `/grill-with-docs` does not run `/to-spec`. It writes no Spec. If the session started from an Issue or an Idea, it deletes that file. It still runs the Retrospective.

When the confirmed Read-back is a change to implement, `/grill-with-docs` still runs `/to-spec` as it does today.

## User Stories

1. As a developer, I want a grilling session that settled on not building anything to leave no Spec, so `/implement` has nothing fake to pick up.

2. As a developer, I want that session to say it wrote no Spec because nothing will be built, so I can tell it finished on purpose.

3. As a developer, I want that session to still run the Retrospective, so the wrap-up does not depend on a Spec existing.

4. As a developer, I want a grilling session that settled on a change to still write a Spec, so a yes still becomes work `/implement` can start.

5. As a developer who started `/grill-with-docs` from an Issue, I want that Issue deleted when we settle on not building the thing, so the tracker does not keep a card for a no.

6. As a developer who started `/grill-with-docs` from an Idea, I want that Idea deleted when we settle on not building the thing, so a thought we rejected does not stay in the ideas folder.

7. As a developer who started `/grill-with-docs` from a paste with no Issue or Idea, I want the session to write no file at all when we settle on not building anything, so a no does not create a document that did not exist before.

8. As a developer, I want Ideas filed during the session for branches we still want kept, so cutting a branch as out of scope is not the same as rejecting the whole subject.

9. As a developer, I want the originating Issue or Idea left in place when the Read-back is a change, so `/to-spec` can still point that file at the new Spec.

10. As a Driving session, I want the confirmed Read-back to be the test of which ending to take, so I do not invent a third Status to mean "we will not do this".

11. As a Driving session, I want a Read-back that mixes "do not build X" with "do build Y" to write a Spec for Y, so a partial no is Out of Scope on a real Spec rather than the no-change ending.

12. As a Driving session, I want to skip `/to-spec` only after the user confirms the Read-back, so a forecast in an earlier Round still does not write files.

13. As a Driving session, I want glossary entries written while terms settled to stay, so the no-change ending does not walk back definitions the user already accepted.

14. As a Driving session, I want ADRs that wait for Spec time left unwritten when there is no Spec, so a no does not get an ADR that exists only to explain the no.

15. As a Driving session, I want a Prototype that ran during the session named only if a Spec is written, so a discarded demo does not force a Spec into existence.

16. As a developer, I want leftover `wontfix` Specs in other repos left alone by this change, so `/grill-with-docs` does not hunt old files.

17. As a developer who types `/to-spec` myself after a no-change grilling, I want that command to still write a Spec, so asking for a Spec on purpose still works.

18. As a later reader of the Specs folder, I want that folder to hold only work we intend to build, so I do not have to guess which Specs are real.

19. As `/implement`, I want every Spec I am handed to describe a change, so I never start a run whose Solution is "do nothing".

20. As a developer, I want `/refine`, `/wayfinder`, and `/prototype` left on their current endings, so this change does not rewrite sessions whose job is to produce a Spec.

21. As a developer, I want the Spec glossary to say a Spec is written only when there is a change to implement, so other skills can use that rule without copying it.

22. As a developer, I want an ADR that records why a no-change grilling writes no Spec, so a later reader does not "fix" the skip by chaining `/to-spec` again.

23. As a Driving session on this skills repo, I want "nothing will be built" to mean no Spec and no skill edits, so the repo rule that skips `/to-spec` to edit skills still has a no-change ending.

24. As a developer, I want `/grilling`'s done-condition to name both endings in the positive, so the inherited interview does not read as "always write a Spec, ADR, or code".

## Implementation Decisions

- `/grill-with-docs` takes one of two endings after the Read-back is confirmed. A change to implement runs `/to-spec` and then the Retrospective, as today. A settled design that nothing will be built skips `/to-spec`, writes no Spec, deletes an Issue or Idea the session started from when one exists, and then runs the Retrospective.

- The confirmed Read-back is the only test. "Nothing will be built" means the whole settled design is that the product and the skills stay as they are. A Read-back that still names a change is the `/to-spec` ending, even when parts of the original request are out of scope.

- Ideas filed during the session for branches the user still wants are not the originating Idea. They stay.

- `/to-spec` itself does not grow a no-change guard. The caller decides whether to invoke it. A user who types `/to-spec` asked for a Spec.

- `/refine`, `/wayfinder`, and `/prototype` keep their current "ends in a Spec" endings. Those sessions exist to produce one.

- Glossary entries already written during the session stay. ADRs that `/grill-with-docs` currently writes in the same turn as the Spec are not written when there is no Spec.

- `/grilling`'s done-condition states the two endings in the positive: a change to implement becomes a Spec; a settled design that nothing will be built writes no Spec. It does not add a Status named for the no.

- The Spec glossary entry states that a Spec is written only when there is a change to implement, and that work we will not do is not a Spec.

- A new ADR records the trade-off: always chaining `/to-spec` after grilling was rejected so a no does not become a file `/implement` could pick up. It points at the existing triage rule that rejected work is not kept as a document.

- This repo's steering that skips `/to-spec` to edit skills in place still skips both when the settled design is no change.

## Testing Decisions

A good check is what a finished session leaves on disk, not how the skill files are worded internally.

- After a confirmed Read-back that nothing will be built, no new file exists under the Specs folder, and an originating Issue or Idea for that subject is gone.
- After a confirmed Read-back that names a change, a Spec exists with `Status: ready-for-agent`.
- After either ending, the session still starts the Retrospective.
- A mixed Read-back ("do not build X, do build Y") produces one Spec for Y, not the no-change ending.
- Ideas filed for branches the user still wants remain after the no-change ending.

This repo has no automated suite for skill prose. The check is a read of the two endings in `/grill-with-docs` and the done-condition in `/grilling`, the way `/validate-spec` already reads a Spec against its checklist. Prior art for "rejected work is not a file" is `/triage`'s not-filed ending.

## Out of Scope

- Changing `/to-spec` so it can refuse to write.
- Changing `/refine`, `/wayfinder`, `/prototype`, or `/improve-codebase-architecture`.
- Hunting leftover `wontfix` Specs in consuming repos.
- Rewriting historical Changelog entries or superseded ADRs that mention `wontfix`.
- Walking back glossary entries written during the session.
- Adding a Status whose meaning is "we will not do this".

The companion Spec `spec-status-is-ready-for-agent` drops `wontfix` from `/validate-spec`. This Spec does not edit that checklist.

## Further Notes

`/triage` already ends rejected work as not filed. This Spec extends that ending to `/grill-with-docs`, which is how a no currently becomes a Spec. The two skills should tell the same story: work we will not do is not a document.
