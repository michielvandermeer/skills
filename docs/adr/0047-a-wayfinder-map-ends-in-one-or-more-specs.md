---
status: partially superseded by ADR-0048
---

# A wayfinder map ends in one or more Specs

[ADR-0011](0011-every-wayfinder-map-ends-in-a-spec.md) fixed what a `/wayfinder` effort produces: a Spec, not a decision or a change made in place. It also fixed how many: exactly one. A goal big enough to need a map is often too big to ship as one change, so the count now follows the work. A Map ends in one or more Specs.

The last session decides the split, once no tickets remain. It cuts where each Spec is a change that lands green and is worth shipping on its own. Size is the reason to look for a cut, and landing on its own is where the cut goes. A Spec may wait on another Spec landing first. The session proposes the split to the user and writes nothing until they confirm it.

## Considered Options

- Split at charting, with the Destination listing the Specs up front — rejected. Charting knows the least about the work, so the split would be a guess that the resolved tickets then force it to redraw.
- Split by size alone — rejected. `/implement` already runs a Spec of any size. A cut made only to shrink a Spec can fall in the middle of a feature and land half of it.
- Split only into Specs that are independent, as `/triage` does — rejected. The stages of a big goal usually build on each other, so a big goal would almost never split.

## Consequences

- ADR-0011 stands for what a Map ends in. Only the count changes.
- The Destination names the whole change the effort's Specs will cover.
- A Spec that must wait for another carries a `Blocked by: <spec-slug>` line. A Spec still in `.agents/specs/` has not landed. `/implement`, `/implement-oneshot`, and `/implement-yolo` stop before they start anything when a Spec is blocked by one that is still there.
- The session that writes the Specs deletes the Map folder in the same commit. The Specs are the record. A Map whose tickets are all resolved would otherwise look like a destination still to write, and a later session would write the Specs again.
