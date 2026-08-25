# A prototype is kept under `.agents/prototypes/`

[ADR-0015](0015-a-prototype-is-deleted-and-its-spec-is-the-record.md) deleted the prototype with its worktree so the Spec was the only record. A Spec that names the question and the verdict still cannot show the thing that was clicked. `/prototype` now writes the artifact to `.agents/prototypes/<slug>/` on the checkout that will hold the Spec, and the Spec names that path. The worktree and `prototype/<slug>` branch still go: keeping those branches was already rejected, and a folder under `.agents/` is the same shape as a Refinement or an architecture review.

Keeping the playable files on the `prototype/<slug>` branch was rejected again: the housekeeping is the same as in ADR-0015. Inlining the demo into the Spec was rejected because a Spec is not a place to click. Building the UI prototype only under `.agents/prototypes/` was rejected because a UI prototype has to sit on a real route to be judged.

## Consequences

- A later reader can open the folder a Spec points at and click through again.
- `/to-spec` names `.agents/prototypes/<slug>/`. Decision-rich snippets (a reducer, a machine) may still be inlined; the folder is the playable record. A Refinement used to name the same path; that line is superseded by [ADR-0023](0023-refine-prototype-lives-in-the-refinement-folder.md).
- A `/prototype` that serves a larger effort writes the folder and writes no Spec of its own.
- A verdict that kills the idea writes no folder and no Spec.
- ADR-0015 is superseded for the "nothing survives" rule. The worktree, the host-shaped levers, the no-fold-into-real-code rule, and the Spec-as-handover rule stand.
