# `/retro` runs only when the user types it

A **Retrospective** starts when the user types `/retro`, usually in a clean session, and no skill starts one. It reads a **Window** of past sessions, the last 100 in this repo unless the argument names another, and acts only on a **Lesson** at least three of them show. A retrospective of one session cannot tell a one-off from a pattern, and it applies **High-priority** changes without asking, so one that judged a single session fixed one-off things and missed context that later sessions supply. Most things one session shows do not need fixing.

A retrospective still applies **High-priority** suggestions without asking, since a wrap-up helps only if the changes land. That includes a judgement-call coding standard and a new check that only configures a tool the repo already runs, when the pain will recur every turn or every session and three sessions showed it. A new check that would fail on the current branch still applies. The rest stay in the chat summary. Where the edits land is [ADR-0040](0040-retro-writes-only-owned-files.md). What the retrospective looks at, including global agent files, is [ADR-0022](0022-retrospective-includes-global-agent-files.md). Repo edits are one commit.

## Considered Options

- **A list of skills that each start a retrospective when they finish.** Rejected: it ran after every session and judged one session alone.
- **Starting one only after a run that went wrong.** Rejected: a run that went wrong is still one session, so a one-off in it still became a rule.
- **Asking the user at the end of each skill whether to run one.** Rejected: it adds a question to every run, and the user can already type `/retro` when they want one.
- **Waiting for confirmation before applying a change.** Rejected: the changes only help if they land.
- **Keeping a one-session run for a bare `/retro`.** Rejected: a bare run would still turn a one-off into a rule, and the main use is now a clean session over past sessions. Typing `/retro` at the end of a working session stays allowed, and that session counts as one of the Window's.
- **A minimum of two sessions.** Rejected: two is still a weak pattern, and a rule that lands without asking binds every later session.
- **A default of the past 24 hours.** Rejected: a quiet repo would usually stop at the minimum, and the last 100 matches `/learn-habits`.
- **Listing every Lesson below the minimum.** Rejected: a 100-session run would bury what matters under one-offs. A Lesson two sessions show is listed with its count, and Lessons one session shows are a single count.

## Consequences

- A skill ends when its own done condition is met, with no retrospective after it.
- `/retro` is typed-only ([ADR-0074](0074-skills-other-skills-follow-are-read-by-path.md)).
- A Window of fewer than three sessions stops and says so.
- A Correction one session shows becomes no rule until three sessions show the same Lesson. The minimum holds for every category, and for filed Issues, since filing counts as applying ([ADR-0040](0040-retro-writes-only-owned-files.md)).
- Runs keep no state. A later Window that finds the same Lesson meets the rule already written or the Issue already open, and `/retro` drops a Lesson today's files already fix.
- `skills:explorer` sub-agents read the logs, about 5 sessions each, and `/retro` judges their records. `/learn-habits` gives each 15 because it picks out grilling answers. `/retro` needs the whole session, and a median log is about 800 KB.
