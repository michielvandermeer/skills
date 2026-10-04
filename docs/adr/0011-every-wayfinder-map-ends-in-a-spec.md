# Every wayfinder map ends in a Spec

Every `/wayfinder` effort finds its way to a Spec, ready to hand to `/implement`. What an effort names is the change that Spec covers. How many Specs, and where the cut falls, is [ADR-0047](0047-a-wayfinder-map-ends-in-one-or-more-specs.md). Which session writes them is [ADR-0048](0048-a-fresh-session-writes-a-wayfinder-maps-specs.md).

Asking each effort what it is finding its way to — a spec, a decision to lock, a change made in place — so the map fits course content as readily as code, was rejected. That generality was never used. Every map drawn so far has ended in a Spec, and the one that made its ADR and its spec into terminal tickets had to declare a deliberate exception to "plan, don't do" in order to do it. Meanwhile the question was asked at the top of every charting session, at the moment the user has the least patience for it, and its answer shaped every ticket underneath — so an effort that answered it loosely paid for that for the rest of its life.

## Consequences

- Charting drops from two grilling passes to one, and that pass grills scope: what the change covers, and what it leaves alone.
- An effort carries no execution in the map. "Plan, don't do" has no Notes override, because a map whose destination is a Spec has nowhere to put the doing.
- Writing the Spec is not a ticket. A ticket resolves a fork, and there is no fork left once the map is empty.
- Non-engineering efforts have no home here. That is the trade accepted: they were hypothetical, and the question cost real time in every session that was not one.
