# `/retro` runs only when the user types it

A **Retrospective** starts when the user types `/retro`, and no skill starts one. A retrospective of one session cannot tell a one-off from a pattern, and it applies **High-priority** changes without asking, so one that ran after every session fixed one-off things and missed context that later sessions supply. The user picks when to run it, so the lessons it applies have been seen more than once.

A retrospective still applies **High-priority** suggestions without asking, since a wrap-up helps only if the changes land. That includes a judgement-call coding standard and a new check that only configures a tool the repo already runs, when the pain will recur every turn or every session and the session demonstrated it. A new check that would fail on the current branch still applies. The rest stay in the chat summary. Where the edits land is [ADR-0040](0040-retro-writes-only-owned-files.md). What the retrospective looks at, including global agent files, is [ADR-0022](0022-retrospective-includes-global-agent-files.md). Repo edits are one commit.

## Considered Options

- **A list of skills that each start a retrospective when they finish.** Rejected: it ran after every session and judged one session alone.
- **Starting one only after a run that went wrong.** Rejected: a run that went wrong is still one session, so a one-off in it still became a rule.
- **Asking the user at the end of each skill whether to run one.** Rejected: it adds a question to every run, and the user can already type `/retro` when they want one.
- **Waiting for confirmation before applying a change.** Rejected: the changes only help if they land.

## Consequences

- A skill ends when its own done condition is met, with no retrospective after it.
- `/retro` is typed-only ([ADR-0074](0074-skills-other-skills-follow-are-read-by-path.md)).
