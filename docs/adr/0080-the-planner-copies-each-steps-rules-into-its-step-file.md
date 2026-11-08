# The Planner copies each Step's rules into its Step file

An `/implement` run's **Planner** reads the repo's **Coding standards** and the **Design principles** once, and copies every rule and principle that bears on a **Step** into that Step's file, word for word, under `## Coding standards` and `## Design principles`. A first-Iteration **Implementer** always reads its Step file, so the rules Review will judge it by are in front of it before it writes. Naming a file in the prompt did not get it read.

In mvdmio-suite, from 2026-10-16 to 2026-11-03, the prompt named the Coding standards for 1,034 of 1,045 first-Iteration Implementers. Only 415 of them (40%) opened a standards file, and 32 (3%) opened `PRINCIPLES.md`. Half of the 484 runs reached a second Iteration, and 183 of the 187 second-Iteration prompts with a **Hard violation** cited a Coding standards file. Four earlier fixes each handed the Implementer a path and assumed it would be read (#56).

## Considered Options

- **Make the Implementer read every standards file whole before it writes.** Rejected. It is still an instruction, the kind that has failed four times. It also re-reads 0.5M to 0.9M cache-read tokens per Implementer in mvdmio-suite, and every later Implementer pays that again.
- **Read the standards by section.** Rejected. This was a stand-in for splitting the standards files, which a cost Hillclimb could not do in a read-only clone, and it was never measured on its own. mvdmio-suite has since split them into topic files with one heading each, so a section read there reads nothing.
- **Leave it to the Pre-review check ([ADR-0078](0078-an-implement-run-runs-the-pre-review-check-before-review.md)).** Not enough on its own. A check catches only the rules a script can test, and only in repos that write one.
- **Drop the Design principles from the Implementer and leave them to Review.** Rejected. At most 4 of those 187 Hard violations came from a principle, but the Implementer should meet both yardsticks Review judges by in the same way.
- **Copy section names or paths instead of the text.** Rejected. That is the current failure in another place.
- **Cap how much a Step file copies.** Rejected. A cap drops rules that Review still judges by, which brings back the Iterations this decision fixed. Rules are kept short at the source instead ([ADR-0081](0081-a-coding-standards-rule-is-one-short-line.md)).

## Consequences

- The Planner's prompt carries the Coding standards' paths and the absolute path to `PRINCIPLES.md`. The Planner reads each file the way it reads code, and it copies a rule it is unsure of rather than leaving it out.
- A section is left out when nothing applies, or when the repo has no Coding standards. There is no cap on how much a Step file copies. Each rule is kept to one short line instead ([ADR-0081](0081-a-coding-standards-rule-is-one-short-line.md)).
- The Implementer prompt still names the Coding standards for code beyond the Footprint, and drops `PRINCIPLES.md`. A later Iteration has no Step file, so its Implementer meets a rule or principle only through a finding that quotes it.
- Review is unchanged and still judges by every principle.
- Whether this cuts Iterations is measured after it lands, by repeating the count above (#57).
