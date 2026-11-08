# A Cold reader explains a new Spec back before the Validator checks it

`/to-spec` hands every Spec draft to a **Cold reader** (`skills:cold-reader`) before the Validator sees it. The Cold reader gets only the draft's path. It retells what the Spec says will change and be built, and it lists each place where it had to guess between two readings. The Driving session compares that retelling with what the session decided and rewrites every part that was misread or guessed at. It does this once, then dispatches the Validator on the rewritten draft.

A Spec is read cold by the Planner and the Implementer, who have no one to ask. A sentence that reads two ways gets built the first way that compiles. The Validator cannot catch this. It reads the Spec next to the code but never learns what was decided, so it settles an ambiguous sentence on the plausible reading without noticing that two readings exist. Only the session that made the decisions can tell a misreading from a correct reading, and only a reader without those decisions shows where the text depends on them.

## Considered Options

Adding the explain-back to `/validate-spec`, so the Validator runs it, was rejected. The Validator has no record of what was decided, so it cannot judge whether a retelling is right.

Giving the Cold reader the repo as well was rejected. The code would fill the gaps the Spec leaves, and those gaps are exactly what the Cold reader is there to find. The Validator already walks the repo.

Running the Cold reader alongside the Validator was rejected. Both would leave the draft changed, and the rewrite would land after the Validator's check, so nothing would check it.

Rereading after the rewrite, until the retelling matches, was rejected. Each pass costs a Sonnet run, and a rewrite made against a list of named misreadings rarely needs a second pass.

Stopping the run when the Cold reader fails was rejected. Its retelling only advises. A failure is reported, and the Validator still runs.

## Consequences

- Every skill that calls `/to-spec` gets the step: `/grill-with-docs`, `/triage`, `/wayfinder`, and `/prototype`.
- The user sees a short list of what was rewritten next to the Validator's report.
- The Cold reader is pinned to Sonnet at `effort: medium`, the model the Planner and Implementer read Specs on ([ADR-0049](0049-agents-are-pinned-in-their-agent-files.md)). A host without `skills:cold-reader` dispatches `general-purpose` with the same prompt, and that dispatch has no pin.
