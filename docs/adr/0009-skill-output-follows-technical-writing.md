# Skill output follows /technical-writing; skill source stays dense

Every sentence a skill puts in front of a person runs at the **Writing bar** the `/technical-writing` skill sets. The skills' own prose does not. The split looks inconsistent until you ask who reads each one. A skill file is read by the agent, where a leading word like *frontier* or *fog of war* buys a whole region of behaviour for one token. A grilling round is read by a person, six hours into a day of them, and that same word costs a lookup they cannot perform.

The reader we write for is a developer new to the repo. They know software. They do not know this codebase. Three tiers of vocabulary follow: terms `CONTEXT.md` defines are used bare, a skill's own terms get one plain-words **gloss** per session, and a **definition site** spends whatever words precision needs.

The sentence rules come from pstack's `technical-writing` skill: the four document types for a free-form document, Google developer style, one instruction per sentence, and wording with one reading. pstack's `unslop` catalogue of AI tells is the final editing pass, in `UNSLOP.md` beside the skill. Text a person reads carries no em dash, en dash, or semicolon, and a colon only introduces a list, an example, or a block. Each of those marks reads as machine-written, and each one hides a sentence break the reader has to find.

A document in the Tracker has a second reader. QA testers and product owners read Issues, Maps, and Specs, and they know the product but not its code. That **Product reader** gets the part that says what is wrong and what changes: a Spec's Problem Statement, Solution, How to Check It, and User Stories, a `needs-` Issue's Motivation and Goal, and a Map's Destination. That part names only what a person meets on the product. `CONTEXT.md` terms stay bare there, because in a product repo they are the product's own words. The rest of the document keeps the developer reader, because the agents and developers who build from it need the files and parts named. ADRs, research files, and PR descriptions keep the developer reader throughout, because their readers look for the code.

## Considered Options

- **ISO 24495-1 plain language alone**, the earlier `/plain-language` skill. Replaced: it set the reader and the vocabulary tiers but said little about the sentence itself, and output still carried AI tells.
- **Importing pstack's two skills as they are.** Rejected: they carry pstack's own house rules (tabs in code snippets, no swarm logs in PRs), and they know nothing of `CONTEXT.md`, the Gloss, or the Product reader.
- **Two skills, `/technical-writing` and `/unslop`.** Rejected: every caller would have to run both, and one that forgot the second would ship the tells.
- **The Product reader as the reader of every durable document.** Rejected: a reviewer reading a PR description or an ADR would lose the names they look for.
- **A separate summary section for people.** Rejected: it tells the problem twice, and the two versions drift apart.

## Why a Library skill

`/technical-writing` is a Library skill that every caller reads by path ([ADR-0074](0074-skills-other-skills-follow-are-read-by-path.md)). It started as a model-invoked skill, whose description reached the agent even from a skill that forgot to point at it. That description cost context on every turn, and it rarely fired on its own. In 60 days, 54 of its 55 loads came from a skill that already named it. Each caller links the file relative to its own folder, which resolves inside the plugin and never against a file in the user's repo.

## Consequences

- A durable document spends plain words rather than a gloss, because it travels. An Issue is read in the Tracker by people who were never in the session, and a Spec is read weeks later by someone who was never in the room. Where a template fixes a section name, the name stays and carries its gloss underneath.
- Text written for a sub-agent is unchanged: a sub-agent prompt, a handoff.
- One check applies the bar: `/validate-spec`'s Product reader item, on the four sections of a Spec that are the Product reader's. Specs that QA could not follow showed the bar being ignored there, and the Validator already reads every new Spec, so the check costs little. Nothing else checks output against the bar: a checking pass on every round and every document would degrade into a rubber stamp.
