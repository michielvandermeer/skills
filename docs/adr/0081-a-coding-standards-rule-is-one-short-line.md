# A Coding standards rule is one short line

A rule in a repo's **Coding standards** is one imperative line of at most 40 words. It holds the requirement, its exceptions and scope, and at most one short example or reason. The story of the incident that led to it stays in git, cut to a `(#n)` or commit reference. `/retro` writes new rules in this shape, and `/doctor` brings existing rules back to it in its one commit. `/doctor` never drops a requirement, exception, or scope limit to meet the cap. A rule that cannot fit stays longer and goes in the report. The Planner copies every rule that bears on a **Step** into its Step file ([ADR-0080](0080-the-planner-copies-each-steps-rules-into-its-step-file.md)), so each word in a rule is paid again on every Implementer turn of every Step it applies to.

A rule names a kind of change, such as "a view under a folder whose name holds braces", never one file, type, or Issue, and it reads true to someone who never saw the incident. `/retro` writes it from what every session behind its **Lesson** shares: a detail only one session had is not part of the rule. An incident story, a Sentry or log ID, an error message, a stack frame, a figure from one run, and a path or symbol only the corrected bug had all stay out. The evidence goes in the retro commit's message and in the Issue when one is filed, a note to delete an interim rule goes in that Issue, and an error signature goes in the repo's triage document. A Lesson whose rule the Coding standards already hold adds nothing to that rule. A Lesson that widens it rewrites the rule to name the wider kind of change, in the same commit, and never appends the new case.

In mvdmio-suite, after ADR-0080 landed, an Implementer spawn went from about $0.50 to about $1.35, and its context from 71K to 92K tokens to about 143K. The standards and testing documents then held 19,980 words, most of it history. A hand trim on 2026-11-05 cut them to 2,282 words in 117 rules, with a median rule of 15 words and a 90th percentile of 25. Within the same day, Spec runs added rules of 66 and 112 words, so a one-off trim does not hold.

## Considered Options

- **A per-file token budget, as proposed in #58.** Rejected. The Planner copies rules, not files, so a file's size is not what a Step pays. Words can be counted without a tokenizer.
- **Let each repo set its own cap, such as on a line in `AGENTS.md`.** Rejected. One fixed number is enough, and no repo has asked for another.
- **Have `/doctor` only report oversized rules.** Rejected. `/doctor` acts on its own judgement and commits once ([ADR-0059](0059-an-adr-states-the-decision-in-force.md) rejected having it ask), and a report nobody acts on leaves every Step paying.
- **Let `/retro` encode what the sessions showed and leave the wording to `/doctor`.** Rejected. Between `/doctor` runs every Step copies the incident text, and mvdmio-suite's retro commit 38a9fb892 grew one rule to 108 words in a single edit.
- **A script that checks each rule `/retro` writes for IDs, paths, and error text.** Rejected. Whether a path is the rule's subject or the bug's detail takes judgement, and the skills have no test suite to run it. `/retro` counts the rule's words before it commits.
- **Keep a one-line pointer, such as "Enforced by MVDM0025", for a rule a check covers in full.** Rejected. `/retro` already deletes a rule once a check enforces it, and the check's own message names the fix.

## Consequences

- A rule a check covers in full is deleted, but only after `/doctor` has read the check's source. A rule a check covers in part keeps the uncovered part in full.
- `/doctor` never adds `[judgement]`. It lists candidates, as [ADR-0079](0079-a-coding-standards-rule-is-hard-unless-marked-judgement.md) leaves the marker to a person.
- Rules a Spec run adds are not checked when they are written. The next `/doctor` run catches them.
