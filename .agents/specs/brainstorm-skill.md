# `/brainstorm` turns a vague problem into Ideas by exploring very different Directions

Status: ready-for-agent

## Problem Statement

Sometimes a developer has a problem but no clear idea of how to solve it. Examples: "How can we test the way our CLI and API work together while both run locally?" or "How could the request pipeline give us better error logs, performance monitoring, and faster requests?"

None of the skills in this plugin helps at that stage. `/grilling`, `/grill-with-docs`, and `/refine` all converge: they stress-test a plan that already exists and aim for the smallest change. The only skill that deliberately generates very different options is the "Design It Twice" step in `/codebase-design`, and it only covers module interfaces. So a developer either jumps straight into grilling with their first idea, or explores by hand in chat. In both cases the options tend to cluster around the first thought, and nobody checks how other people already solve the problem.

## Solution

A new skill, `/brainstorm`, that only a person can start by typing it. You give it a problem in plain words, or the path to an existing Idea.

First, a read-only explorer maps the code the problem touches. The skill then opens with its reading of the problem, the constraints it takes as fixed, and the four angles it will explore from. It asks a question before exploring only when the problem can be read two ways that would lead to different results. Otherwise you correct its reading by replying.

Four helper agents then run in parallel, one per angle, and each writes one **Direction**: a very different way to tackle the problem. One angle is always "How are other people solving this?", and that agent searches the web so it can name real, current tools and techniques. Each Direction arrives as a short card: the pitch, how it works, what it costs, what it is best at, and its biggest risk. The skill ends the set with its own pick and the reason for it.

After each set you decide what happens next. You can keep Directions, ask for a narrower pass ("go deeper on 2", "combine 1 and 4"), or stop. The loop runs until you pick.

Each Direction you keep becomes its own Idea. The skill commits all the Ideas in one commit and then runs `/retro`. It never writes a Spec and never starts another grilling skill. The next step is `/grill-with-docs` or `/refine` on one of the Ideas.

## User Stories

1. As a developer with a vague problem, I want to type `/brainstorm` followed by the problem in plain words, so that I can start exploring without writing a document first.
2. As a developer, I want to pass the path to an existing Idea instead, so that I can brainstorm an Idea that is still too loose to grill.
3. As a developer, I want `/brainstorm` to start only when I type it, so that the agent never starts a long exploration on its own.
4. As a developer, I want the skill to read the code the problem touches before it builds Directions, so that the Directions start from what my system does today.
5. As a developer, I want Directions not to be limited to what the code already does, so that a bold option is not ruled out just because it needs new structure.
6. As a developer, I want the skill to open with its reading of the problem and the constraints it takes as fixed, so that I can correct a wrong reading before it matters.
7. As a developer, I want to see which angles the skill will explore from, so that I know why the Directions differ.
8. As a developer, I want the skill to ask me a question first only when my problem can be read two ways that lead to different results, so that exploration is not delayed by questions I cannot answer in the abstract.
9. As a developer, I want the Directions to come from separate helper agents, each with its own angle, so that they really differ instead of clustering around one first thought.
10. As a developer, I want one angle always to be "How are other people solving this?", so that I learn about existing tools and known approaches before I build my own.
11. As a developer, I want that agent to search the web, so that the tools it names exist today and are not remembered wrongly.
12. As a developer, I want other helper agents to be able to search the web when their Direction depends on an outside tool or technique, so that every Direction rests on real facts.
13. As a developer, I want the skill to pick the other three angles for my problem from a starter list, so that the angles fit the problem instead of being the same every time.
14. As a developer, I want the starter list to cover the smallest change to what exists, building it the ideal way from scratch, reframing or avoiding the problem, and borrowing from another field, so that the set spans very different kinds of answer.
15. As a developer, I want each Direction shown as a short card with its pitch, how it works, what it costs, what it is best at, and its biggest risk, so that I can compare Directions quickly.
16. As a developer, I want the skill to close each set with its own pick and the reason for it, so that I get a strong opinion and not only a menu.
17. As a developer, I want to ask for more angles than four, so that I can widen the search when the first set feels narrow.
18. As a developer, I want to ask for a narrower pass on one or two Directions, so that a vague problem becomes concrete step by step.
19. As a developer, I want to ask the skill to combine two Directions, so that I can keep the best parts of each.
20. As a developer, I want a narrower pass to use fresh helper agents with the tighter brief, so that the new set is still spread out rather than a rewrite of the old cards.
21. As a developer, I want a narrower pass to reuse the first code map, so that it does not spend time reading the same code again.
22. As a developer, I want the "How are other people solving this?" angle to stay in every pass, so that each narrowing step is checked against what already exists.
23. As a developer, I want to keep more than one Direction, so that I can take two promising Directions forward and grill each one later.
24. As a developer, I want each kept Direction written as its own Idea, so that each one can go into its own `/grill-with-docs` or `/refine` session.
25. As a developer, I want each Idea to use the usual Idea sections, so that `/grill-with-docs`, `/refine`, and `/validate-spec` read it like any other Idea.
26. As a developer, I want the Directions I dropped listed under Out of scope with the reason, so that a later session does not suggest them again without knowing why they were dropped.
27. As a developer, I want the open points of a kept Direction listed under Open questions, so that the next grilling session knows where to start.
28. As a developer, I want the outside sources a kept Direction relies on to be linked in its Motivation, so that I can check them later.
29. As a developer who started from an Idea, I want the first kept Direction to replace that Idea's content, so that the loose Idea does not linger beside its sharper version.
30. As a developer who started from an Idea and kept several Directions, I want every Direction after the first to become a new Idea, so that nothing I kept is lost.
31. As a developer who stops before picking, I want the skill to write one Idea holding the problem and every Direction shown so far, so that the exploration is not lost.
32. As a developer, I want no other brainstorm file kept, so that `.agents/` holds only documents another skill will read.
33. As a developer, I want all Ideas from one run in a single commit, so that I can review or revert the run in one go.
34. As a developer, I want `/brainstorm` never to write a Spec or start another grilling skill, so that each typed run produces one kind of document.
35. As a developer, I want `/retro` to run after the commit, so that lessons from the session improve the skills.
36. As a developer, I want every round and card written in plain language, so that I can read it quickly late in a long day.
37. As a developer browsing the plugin, I want `/brainstorm` listed in the README's Skills table, so that I can find it.
38. As a maintainer of this repository, I want **Direction** defined in `CONTEXT.md`, so that the skills use one word for it and do not confuse it with a lettered option inside a Question.
39. As a maintainer, I want ADR-0038 to list `/brainstorm` among the skills that start a retrospective, so that the ADR and the skill agree.

## Implementation Decisions

- **New skill.** A new skill named `brainstorm` in the plugin's skills folder. It gets `disable-model-invocation: true`, a one-line description written for people with no trigger list (the rule for user-invoked skills in `/writing-for-agents`), and the argument hint `<problem or idea path>`. The plugin finds skills on its own; no manifest field changes.
- **Explorer first.** The Driving session dispatches one read-only `skills:explorer` to map the code the problem touches. It carries the report, not the files, as `/grilling` does (ADR-0027). When the problem touches no code in the repository, the report says so and the run goes on. The Driving session does not read the code itself.
- **Opening message.** The session's reading of the problem, the constraints it takes as fixed, and the four chosen angles come in the same message as the first set of Directions. The skill asks a question first only when the problem can be read two ways that lead to different Directions.
- **Angles.** "How are other people solving this?" is fixed in every set, and its agent must search the web. The Driving session picks the other three from a starter list: smallest change to what exists, build it the ideal way from scratch, reframe or avoid the problem, borrow from another field. The list is a starting point; the session may write a problem-specific angle when that gives a wider spread. The user can ask for more than four.
- **Fan-out.** One general-purpose sub-agent per angle, dispatched in parallel, on the session's own model and effort. Generating Directions is judgement work, the same class as the Design It Twice fan-out that README's "Sub-agent cost tiers" section leaves unpinned. That section gains the `/brainstorm` fan-out in the same list. No new agent file. Each agent gets the problem, the constraints, the explorer report, its angle, and the instruction to produce one Direction that differs as much as possible from the obvious answer. A Direction is not limited to what the code already does. Any agent may search the web when its Direction depends on an outside tool or technique.
- **Direction card.** Pitch, how it works, what it costs, what it is best at, biggest risk, and sources when the agent used any. The Driving session puts the cards side by side and closes with its own pick and reason, in the spirit of Design It Twice's "be opinionated".
- **Loop.** After each set the user keeps, narrows, combines, or stops. A narrower or combined pass sends out a fresh set of agents with the tighter brief. It reuses the first explorer report, and the "How are other people solving this?" angle stays in. The loop ends when the user picks.
- **Idea shape.** Each kept Direction is written to `.agents/ideas/<slug>.md`, with the slug in kebab-case from its title. The sections are the ones `/validate-spec` enforces: Motivation, Goal, Decisions (locked), Out of scope, Open questions. There is no Status line, no file paths, and no code. Dropped Directions go under Out of scope with the reason. Outside sources go in Motivation as links. The Idea is written to the durable-document bar of `/plain-language`.
- **Starting from an Idea.** The first kept Direction overwrites the source Idea's content under the same slug. Every other kept Direction becomes a new Idea.
- **Stopping early.** If the user stops before any pick, the skill writes one Idea holding the problem, with every Direction shown so far under Open questions. It commits that Idea and runs `/retro`, the same as a normal end.
- **No session folder.** Directions live only in the chat. Nothing else is written under `.agents/`.
- **End.** All Ideas from the run go into one commit, staged by name, on the current branch. `/retro` runs after that commit. `/brainstorm` is now on the Named session skill list in ADR-0038, which was already rewritten in place in this Spec's commit.
- **Boundaries.** The skill never writes a Spec, never writes an ADR, and never starts `/grill-with-docs`, `/refine`, or `/implement`. It may point the user at `/grill-with-docs` or `/refine` as the next step. This follows ADR-0035: each typed run produces one kind of document.
- **Plain language.** The opening, every card, and the closing pick run at `/plain-language`. Prompts sent to helper agents do not.
- **README.** Add a `brainstorm` row to the Skills table, in alphabetical order.
- **Glossary.** `CONTEXT.md` already defines **Direction** (written in the grilling session). The skill uses that word and not "option", which is a lettered answer inside a Question.
- The skill file must match `/writing-for-agents`, and `/writing-for-agents` runs on it afterwards, as this repository's `CLAUDE.md` requires.

## Testing Decisions

- This repository has no automated tests. Every change is prose in a skill file.
- The frontmatter hook checks the new skill's frontmatter on every edit. It must pass.
- A good check looks at what the skill would do from the outside. Read the finished skill and walk both motivating problems through it:
  - "An E2E test setup for a local CLI and API": the explorer maps both. The "How are other people solving this?" agent searches for existing tools. The set shows four clearly different Directions and a pick. Keeping one writes one Idea with the dropped Directions under Out of scope.
  - "A request pipeline with better errors, monitoring, and speed": the opening states the three goals as its reading. A "go deeper on 2" pass sends out fresh agents and reuses the explorer report. Keeping two Directions writes two Ideas in one commit.
- Walk the edge cases: starting from an Idea path, stopping before a pick, and a problem that touches no code.
- Run `/validate-spec` on one Idea the walkthrough would produce, to confirm the shape passes the Idea rules.
- Read ADR-0038 next to the skill. They must agree that `/brainstorm` starts a retrospective.

## Out of Scope

- Grilling a chosen Direction. That stays with `/grill-with-docs` and `/refine`.
- Writing Specs or ADRs from a brainstorm.
- A saved brainstorm session or a folder under `.agents/` for one.
- A new Idea section for Directions considered. Dropped Directions use Out of scope.
- Changes to `/codebase-design`'s Design It Twice.
- Letting the agent start `/brainstorm` on its own.
- A new plugin agent file for the helper agents.

## Further Notes

- The grilling session that produced this Spec settled these points in its own words. Directions come from parallel agents with different angles. At least one agent always asks "How are other people solving this?" and searches the web. The user narrows step by step until they pick. No questions come before the first set unless the problem is ambiguous. One Idea is written per kept Direction. `/brainstorm` starts a retrospective.
- No existing Idea or Issue started this session.
