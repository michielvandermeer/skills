# Skill output is plain; skill source stays dense

Every sentence a skill puts in front of a person now runs at ISO 24495-1:2023 plain language, held by the `/plain-language` skill. The skills' own prose does not. The split looks inconsistent until you ask who reads each one. A skill file is read by the agent, where a leading word like *frontier* or *fog of war* buys a whole region of behaviour for one token. A grilling round is read by a person, six hours into a day of them, and that same word costs a lookup they cannot perform.

The reader we write for is a developer new to the repo. They know software. They do not know this codebase. Three tiers of vocabulary follow: terms `CONTEXT.md` defines are used bare, a skill's own terms get one plain-words **gloss** per session, and a **definition site** spends whatever words precision needs.

## Why a skill rather than a shared file

The rule could have been a file at the repo root that each skill reads. It is a model-invoked skill instead, and that costs one description in every user's context, on every turn, forever.

The cost buys two things a file cannot. The rule reaches the agent even from a skill that forgot to point at it, because a description is always loaded. And it never resolves against the wrong file: these skills run inside other people's repos, where a relative path is a guess and a bare filename could hit something of theirs.

## Consequences

- A durable document spends plain words rather than a gloss, because it travels. A Refinement is written back to a Jira ticket, and a Spec is read weeks later by someone who was never in the room. Where a template fixes a section name, the name stays and carries its gloss underneath.
- `/refine` holds a stricter bar than the rest: readable aloud once, in a room, to someone who does not write code.
- Text written for a sub-agent is unchanged — a Step, an agent brief, a handoff.
- Nothing checks output against the bar. A checking pass would run on every round and every document, and it would degrade into a rubber stamp. If the bar starts getting ignored, that is when a check earns its cost.
- The ADRs written before this one, and `README.md`, were left as they are.
