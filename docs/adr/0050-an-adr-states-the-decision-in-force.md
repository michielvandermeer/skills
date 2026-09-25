# An ADR states the decision in force

An ADR records a decision that holds today and the reason it holds. It carries no history, because git already keeps how a decision got to where it is. When a decision changes, the session that changes it rewrites the ADR in place at Spec time, keeping its number. When a decision is reversed with nothing in its place, its ADR is deleted. `/doctor` brings older ADRs to the same shape: it folds each chain of ADRs about one decision into a single ADR under the newest number, and it rewrites ADRs that tell history.

`/doctor` also checks every ADR against the code and brings it in line. When the code has moved on from an ADR and there is evidence someone chose that on purpose — a migration, a commit whose message states the change, or a newer Spec or ADR that covers it — `/doctor` rewrites the ADR to state what the code does, or deletes it when nothing of the decision is left. When there is no such evidence, the ADR stays as written and `/doctor` reports the mismatch as a bug in the code. An ADR whose Spec was dropped is judged the same way: deleted when nothing was built, rewritten to what was built otherwise.

## Considered Options

- ADRs that are never edited, where a newer ADR marks the older one superseded. This is the usual practice, and it is rejected. A reader has to walk the whole chain to learn what holds now, and partial replacements are easy to miss when a newer ADR states them only in its body. Every session that reads the ADRs pays for the chain in context.
- Rewriting an ADR when its Spec lands instead of at Spec time. Rejected: three implement skills would each take on a new duty. The sessions that read ADRs while a Spec waits are usually planning the next change, so the planned decision is the one they need.
- `/doctor` reports every mismatch between an ADR and the code and leaves the ADR as written, treating the code as the thing that is wrong. Rejected: most mismatches are decisions that moved on without anyone rewriting the ADR, so the ADRs stay stale and every later session reads a decision that no longer holds.
- The code always wins, and `/doctor` rewrites every contradicted ADR to match it. Rejected: a real bug, such as an error message leaking to a user against an ADR that forbids it, would be recorded as a decision.
- `/doctor` asks the user about each mismatch. Rejected: `/doctor` runs from start to finish without asking, and its diff and report already show every judgement it made.

## Consequences

- `ADR-FORMAT.md` has no Status section. Any ADR in `docs/adr/` is in force.
- Numbers are never reused. A deleted or folded ADR leaves a gap.
- An option once chosen and later dropped stays only as a rejected option with its reason, and only when someone might propose it again.
- `/doctor` never edits application code. A mismatch it judges to be a bug appears only in its report; it files no Issue or Idea for it.
