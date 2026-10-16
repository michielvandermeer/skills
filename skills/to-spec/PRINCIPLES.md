# Planning principles

These principles describe what a Spec must give `/implement`. One Implementer builds the whole Spec in one session, with no person to ask, and a Verifier then checks it. Whatever the Spec leaves open, they fill with a guess. `/grilling` recommends options by these principles, `/to-spec` writes the Spec to meet them, and the Validator checks the draft against them. Each one says when it applies. Name the principle when you cite it, as in "misses Explain the number: ...".

## Leave the implementer nothing to ask

Every choice that changes what a person meets is made in the Spec. The run has no one to ask, so an open choice gets settled by the first guess that compiles.

**In a Spec:**
- A choice left as "TBD", "either", or "to be decided", or left out where the Solution needs it.
- Behaviour written for the happy path only, when the person also meets the empty, error, or no-permission case.
- An Implementation Decision that leaves something a person would notice to "the implementer's judgement".

**Fix:** decide each such choice in the Spec. A choice the person would never notice can be left to the Implementer, as long as the Spec says so and gives the bounds. A choice only a person can make goes to a grilling round before the Spec is written.

## Fit one run

A fresh Implementer reads and builds the whole Spec in one session; each later Iteration starts a fresh one to fix findings, up to three in all. The Spec has to fit that first session.

**In a Spec:**
- A Solution made of several features, each of which could ship alone.
- Implementation Decisions that reach into many unrelated areas, or a sweep over more files than one session can read.
- User Stories that fall into groups with no module in common.

**Fix:** a Spec that one session could not read and build is too big. Splitting it is a person's call: they split it into Specs that each land green, or move the change to `/wayfinder`.

## Experience first

The smallest change ([ADR-0065](../../docs/adr/0065-a-spec-takes-the-smallest-change-that-does-the-job.md)) decides how the change is built. The person's experience decides what they get. That person is whoever uses the result: someone on a screen, a developer calling an API, the next maintainer.

**In a Spec:**
- A Solution with no error message, empty state, loading state, or feedback where the person will need one, because the smallest build could skip it.
- A new control, option, or setting that no User Story needs.
- A clumsy call or extra step for the person, there because it was easier to build.

**Fix:** where the smallest build leaves the person worse off, build the wider version, and say why in Implementation Decisions. Remove every control or option no User Story needs.

## Exhaust the design space

An interaction, screen, or architecture that has no precedent in the codebase gets compared in working form before it is chosen. So does any choice whose right answer depends on how it feels to use.

**In a Spec:**
- A new kind of screen, interaction, or structure, with nothing like it in the codebase, chosen by argument alone.

**Fix:** run `/prototype` before the Spec is written. A UI prototype builds its variants; a logic prototype builds two or three competing models. Write the verdict into the Spec and name the prototype's folder there.

## Sequence verifiable units

The Spec names the check that fails today and passes once the change lands. Work that is split ships in an order where every Spec lands green.

**In a Spec:**
- A bug fix whose Testing Decisions name no test that fails on today's code.
- A reproduction that `/triage` recorded but the Spec leaves out.
- A Spec in a split that can't land green alone, or that comes before a Spec it needs.

**Fix:** turn the reproduction into the first test, the one that fails on today's code, and add the Hand check that shows the fix working. Order the Specs of a split so prerequisites come first, and link each Spec as blocked by the ones it waits on.

## Explain the number

A number a Spec promises or relies on is measured before anyone trusts it: a speed-up, a latency, a size, a cost, an eval score.

**In a Spec:**
- A target such as "twice as fast", "under 200 ms", or "half the memory", with no baseline measured on today's code.
- A Hand check that reads a number off a single run.
- A number taken from a report without anyone measuring it.

**Fix:** measure the baseline before the Spec, and record the run count and the spread. Name what limits the number, such as a lock, the disk, or one code path, using a profile. Rule out what else the number could be measuring: errors, cached or skipped work, code that never ran, noise. The Hand check measures the result the same way the baseline was measured.

## Attack the premise

Two or more fixes that failed the same way all shared an assumption. Suspect that assumption before writing a third fix.

**In a Spec:**
- A fix for a problem that earlier fixes already tried (closed Issues, or commits reverted or patched again), where the new fix assumes what the earlier ones assumed.

**Fix:** write the shared assumption down in one sentence. Before the Spec, run a check that would come out differently if the assumption were false. When the problem is unevenly spread across actors, the check is a count of which actors hold how much of it. Write the fix from what the check showed. If the check can't run during planning, park the Issue in `needs-grilling` with the assumption and the check written in it.

## Build the lever

When the same edit repeats across many places, a script makes the edit and a check that can be rerun proves it.

**In a Spec:**
- One edit spelled out as a list of files or call sites.
- A check that only a person can repeat by hand.

**Fix:** in Implementation Decisions, name the codemod, script, or generator that makes the edit. In Testing Decisions, name a check the Verifier can run again.

## Converge on the end state

A Spec builds the end state: every caller moved, the old way deleted.

**In a Spec:**
- An old path kept "for compatibility": a flag, an adapter, or writing to both old and new, in a change that could move every caller now.
- Bridge code that no later Spec removes.

**Fix:** within one Spec, move every caller and delete the old path in the same change. Bridge code is allowed only when the change is split across Specs and one in the middle must land green. Name the bridge code in that Spec's Implementation Decisions. A later Spec, linked as blocked by it, removes it.
