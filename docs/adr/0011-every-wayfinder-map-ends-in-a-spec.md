# Every wayfinder map ends in a Spec

`/wayfinder` used to ask each effort what it was finding its way to — a spec, a decision to lock, a change made in place — and called the map domain-agnostic, fit for course content as readily as for code. The destination is now fixed: a Spec at `.agents/specs/<slug>.md`, ready to hand to `/implement`. What an effort still names is the change that Spec covers.

The generality was never used. Every map drawn so far has ended in a Spec, and the one that made its ADR and its spec into terminal tickets had to declare a deliberate exception to "plan, don't do" in order to do it. Meanwhile the question was asked at the top of every charting session, at the moment the user has the least patience for it, and its answer shaped every ticket underneath — so an effort that answered it loosely paid for that for the rest of its life.

## Consequences

- Charting drops from two grilling passes to one, and that pass grills scope: what the change covers, and what it leaves alone.
- An effort can no longer carry execution into the map. "Plan, don't do" loses its Notes override, because a map whose destination is a Spec has nowhere to put the doing.
- Writing the Spec is not a ticket. A ticket resolves a fork, and there is no fork left once the map is empty — so the session that finds no tickets remaining zooms the resolved ones and runs `/to-spec`.
- Non-engineering efforts have no home here. That is the trade accepted: they were hypothetical, and the question cost real time in every session that was not one.
