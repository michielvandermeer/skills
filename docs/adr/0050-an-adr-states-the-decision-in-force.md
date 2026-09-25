# An ADR states the decision in force

An ADR records a decision that holds today and the reason it holds. It carries no history, because git already keeps how a decision got to where it is. When a decision changes, the session that changes it rewrites the ADR in place at Spec time, keeping its number. When a decision is reversed with nothing in its place, its ADR is deleted. `/doctor` brings older ADRs to the same shape: it folds each chain of ADRs about one decision into a single ADR under the newest number, and it rewrites ADRs that tell history.

## Considered Options

- ADRs that are never edited, where a newer ADR marks the older one superseded. This is the usual practice, and it is rejected. A reader has to walk the whole chain to learn what holds now, and partial replacements are easy to miss when a newer ADR states them only in its body. Every session that reads the ADRs pays for the chain in context.
- Rewriting an ADR when its Spec lands instead of at Spec time. Rejected: three implement skills would each take on a new duty. The sessions that read ADRs while a Spec waits are usually planning the next change, so the planned decision is the one they need. `/doctor` reports an ADR whose Spec was dropped.

## Consequences

- `ADR-FORMAT.md` has no Status section. Any ADR in `docs/adr/` is in force.
- Numbers are never reused. A deleted or folded ADR leaves a gap.
- An option once chosen and later dropped stays only as a rejected option with its reason, and only when someone might propose it again.
