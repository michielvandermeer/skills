# Skill output is plain; skill source stays dense

Every sentence a skill puts in front of a person now runs at ISO 24495-1:2023 plain language, held by the `/plain-language` skill. The skills' own prose does not. The split looks inconsistent until you ask who reads each one. A skill file is read by the agent, where a leading word like *frontier* or *fog of war* buys a whole region of behaviour for one token. A grilling round is read by a person, six hours into a day of them, and that same word costs a lookup they cannot perform.

The reader we write for is a developer new to the repo. They know software. They do not know this codebase. Three tiers of vocabulary follow: terms `CONTEXT.md` defines are used bare, a skill's own terms get one plain-words **gloss** per session, and a **definition site** spends whatever words precision needs.

A document in the Tracker has a second reader. QA testers and product owners read Issues, Maps, and Specs, and they know the product but not its code. That **Product reader** gets the part that says what is wrong and what changes: a Spec's Problem Statement, Solution, How to Check It, and User Stories, a `needs-` Issue's Motivation and Goal, and a Map's Destination. That part names only what a person meets on the product. `CONTEXT.md` terms stay bare there, because in a product repo they are the product's own words. The rest of the document keeps the developer reader, because the agents and developers who build from it need the files and parts named. ADRs, architecture reviews, research files, and PR descriptions keep the developer reader throughout, because their readers look for the code.

The Product reader was rejected as the reader of every durable document: a reviewer reading a PR description or an ADR would lose the names they look for. A separate summary section for people was rejected: it tells the problem twice, and the two versions drift apart.

## Why a skill rather than a shared file

The rule could have been a file at the repo root that each skill reads. It is a model-invoked skill instead, and that costs one description in every user's context, on every turn, forever.

The cost buys two things a file cannot. The rule reaches the agent even from a skill that forgot to point at it, because a description is always loaded. And it never resolves against the wrong file: these skills run inside other people's repos, where a relative path is a guess and a bare filename could hit something of theirs.

## Consequences

- A durable document spends plain words rather than a gloss, because it travels. An Issue is read in the Tracker by people who were never in the session, and a Spec is read weeks later by someone who was never in the room. Where a template fixes a section name, the name stays and carries its gloss underneath.
- An architecture review may use `/codebase-design` terms bare — module, interface, seam, and the rest of that vocabulary — when they are the natural claim. The report otherwise stays at this bar, so the review can name the structure it is judging.
- Text written for a sub-agent is unchanged — a sub-agent prompt, a handoff.
- One check applies the bar: `/validate-spec`'s Product reader item, on the four sections of a Spec that are the Product reader's. Specs that QA could not follow showed the bar being ignored there, and the Validator already reads every new Spec, so the check costs little. Nothing else checks output against the bar: a checking pass on every round and every document would degrade into a rubber stamp.
