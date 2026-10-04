# A prototype is kept under `.agents/prototypes/`

`/prototype` writes the artifact to `.agents/prototypes/<slug>/`, and the Spec names that path. A session that starts on the original checkout writes the folder there, outside the worktree. A session already inside a worktree writes the folder in that tree and leaves the worktree to the effort that opened it, so the playable record stays with that effort. A Spec that names the question and the verdict still cannot show the thing that was clicked. The worktree and `prototype/<slug>` branch still go ([ADR-0016](0016-a-prototype-session-runs-in-a-worktree.md)): keeping those branches was rejected, and a folder under `.agents/` is the same shape as an architecture review.

Keeping the playable files on the `prototype/<slug>` branch was rejected: the housekeeping is the same as deleting the branch. Inlining the demo into the Spec was rejected because a Spec is not a place to click. Building the UI prototype only under `.agents/prototypes/` was rejected because a UI prototype has to sit on a real route to be judged.

## Consequences

- A later reader can open the folder a Spec points at and click through again.
- `/to-spec` names `.agents/prototypes/<slug>/`. Decision-rich snippets (a reducer, a machine) may still be inlined; the folder is the playable record. `/refine` names the same path ([ADR-0039](0039-refine-ends-in-a-spec.md)).
- A `/prototype` that serves a larger effort writes the folder and writes no Spec of its own.
- A verdict that kills the idea writes no folder and no Spec.
