# A Coding standards rule is hard unless it is marked judgement

A rule in a repo's **Coding standards** that starts with `[judgement]` is a **Judgement call** when the diff breaks it, so it never sends an `/implement` run into another **Iteration**. A rule that starts with `[hard]`, or with no marker, is a **Hard violation** when broken. A break that names a defect (a wrong result, a crash, or lost data) is a Hard violation whatever the marker says. A repo can hold a rule it wants followed without paying an Iteration for every break, and every rule written before the marker existed keeps its weight.

## Considered Options

- **Judgement as the default, with `[hard]` to opt in.** Rejected: every existing rule would change weight on the day the plugin updates.
- **A marker on a heading that covers the rules beneath it.** Rejected: a standards file is a flat list of rules under one heading, so there is no section to carry it.
- **Separate files for hard and judgement rules.** Rejected: standards files are split by topic, and a rule's weight would then decide where a reader looks for it.
- **A severity scale with more than two levels.** Rejected: a review has two outcomes, another Iteration or not.

## Consequences

- `/code-review` carries the marker into the Standards brief, and the Implementer treats a `[judgement]` rule as its own to weigh.
- A rule `/retro` writes has no marker, so it is hard. A person adds `[judgement]` when a rule should only advise.
