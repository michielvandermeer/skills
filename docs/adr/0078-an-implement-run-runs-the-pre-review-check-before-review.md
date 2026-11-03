# An implement run runs the Pre-review check before Review

A repo can name a **Pre-review check** on a `Pre-review check:` line in its `AGENTS.md` or `CLAUDE.md`: a command that takes `<base>`, lists the Coding standards breaks it finds in what the branch adds, and exits non-zero when it lists any. `/implement` hands it to every Implementer, which must leave it passing, and runs it again as part of the structural check after each dispatch, before Review. A failed run earns the agent's one retry like any structural failure. A check still red after the retry does not halt the run: Review gets its findings and judges each one, because the check reads text and can be wrong. A repo without the line skips all of it.

In mvdmio-suite, over 14 days of transcripts (396 runs, 2026-10-21 to 2026-11-03), 45% of runs needed a second Iteration and those runs cost 77% of all `/implement` tokens. Review sent almost all of them back: Iteration 1's Review failed about half the time, its Verify about 6%. About a quarter of the Hard violations since 2026-10-31 were mechanical (a copied test helper, constant casing, an every-element check on a list never shown non-empty, a comment path not from the repo root, a long Changelog title). Naming the rule in the Implementer's prompt did not prevent them: Implementers handed a testing document by name opened it in about 38% of runs, at the same rate in runs that passed Review and runs that failed it.

## Considered Options

- Name more rules in the Implementer's prompt — rejected. The run's Retrospectives kept doing this, and Review still failed about half of Iteration 1s.
- Put each rule in the repo's build as an analyzer — the strongest form where it fits, and the check does not replace it. A diff-scoped script checks only what the branch adds, so it can hold a rule the existing code still breaks, and a heuristic rule an analyzer could not hold without false positives on old code.
- Halt the run when the check stays red — rejected. A text heuristic can be wrong, and halting would make a false positive cost the whole run.

## Consequences

- The Implementer waives a wrong finding the way the check's output says, with a reason, and the Review judges that reason.
- The check's command is the repo's to write and keep. The skills read only the line that names it.
