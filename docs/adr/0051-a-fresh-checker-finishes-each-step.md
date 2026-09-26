# A fresh Checker finishes each Step

In `/implement`, the Step agent does not review its own work. Once it has committed its Step with its Footprint's tests passing, the Driving session sends a fresh **Checker** (`skills:checker`). The Checker runs the repo's browser pass or smoke run, reviews the Step's commit on both axes, fixes what it finds, and folds the fixes into that commit. The Step agent used to do all of this itself, after its code was green. In 48 hours of transcripts (2026-09-24 to 2026-09-26), that work took 29% of Step agent spend, because by then its context had grown to 300–400k tokens and every turn re-reads the whole context. A Checker starts from the Step file and the Step's changes, at a small fraction of that.

The trade: the Checker does not know the code the way the Step agent does, and it re-reads what it needs to fix. Review findings name the place they are about, so that re-reading is narrow.

## Considered Options

The Step agent starting the Checker itself was rejected. The Step agent would wait at peak context while the Checker worked, and the Checker's reviewers would sit three agents deep. Every other `/implement` sub-agent is sent by the Driving session.

Moving only the browser pass, and keeping the review-and-fix loop in the Step agent, was rejected. Both run at peak context, and the loop is the larger part.

Dropping the per-Step Standards review and leaving it to the final review was rejected. Once the review runs at a small context, the saving left is small, and it would move more work onto the final fixers, which were already the longest agents in a run.

## Consequences

- A Step has two states after `pending`. The Step agent sets `Status: built`, and the Checker sets `done`. A resumed run restarts a `built` Step at its Checker, so a check is never skipped.
- The Step agent's own green covers only its Footprint's tests. A Step is **Green** once the Checker's verification has passed too.
- The Checker is Spec-bound and runs at `effort: medium`, the effort the review-and-fix loop already ran at inside the Step agent ([ADR-0049](0049-spec-bound-agents-keep-the-session-model.md)).
