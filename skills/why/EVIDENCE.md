# Evidence

The record is historical, partial, and sometimes contradicts itself. Each claim in the answer sits in one tier, and the tier sets where it goes and how it is worded.

## Tiers

- **Direct**: someone wrote down the reason. A pull request says "fixes pagination for users with more than 1000 items", an Issue says "customer Acme asked for this in their security review", a comment says "clamp to 100 because the upstream API rejects more". State it plainly, with the citation: "This exists because X."
- **Supported**: several indirect items point to one conclusion and none states it. The pull request title says "improve performance", the Issue is labelled `perf`, and the commits around it all touch the same hot path. State it with each item cited: "The evidence points to X: A, B, and C."
- **Inferred**: a reasonable reading that nothing states. It goes under What we can reasonably infer, hedged, with the chain shown: "Given A and B, C seems likely, because D."
- **Speculative**: a possibility the evidence barely touches, with others fitting as well. It goes under Competing hypotheses: "One possibility is X, but we found no evidence for it."
- **Unknown**: searched for and not found. It goes under What we don't know, naming the sources and the searches: "We searched the Tracker for A and B and read the six pull requests that touched this file since 2023. None gives a reason for the limit."

## Wording

- "because", "the reason is", "was designed to", "fixes", and "the team decided" claim a recorded fact. Use them only with a Direct or Supported citation beside them.
- An inference uses "appears to", "likely", "suggests", or "is consistent with".
- "Obviously", "clearly", "of course", and "just" hide uncertainty. Say what the evidence shows instead.

## Traps

- **Code as its own reason.** The code shows what it does, never why. A claim whose only evidence is the code it explains moves to Inferred or out.
- **A tidy story.** Code that makes sense today may exist for reasons that no longer hold, or were wrong then. A consistent pattern may be copy and paste. No one mentioning a concern does not mean there was none.
- **The asker's guess.** A guess in the question gets the same check as any other hypothesis. Confirm it only with evidence, and say what the evidence supports when it is not the guess.
- **The latest commit.** The current shape is usually many decisions deep. Trace back past the last change.
- **A ruling's scope.** "Avoid that endpoint during this migration" and a later note saying "the endpoint is forbidden" are different claims. Quote the person's own words, mark a summary as a summary, and count copies of one summary as one source.
- **Contradictions.** When two sources disagree, show both with their citations, and leave the call to the reader.

An honest gap is worth more than a confident guess, because the reader acts on what the answer says. An answer with no gaps at all is suspect.
