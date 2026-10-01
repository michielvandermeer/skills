# Idea — The builder names the one fact that keeps a change safe

## Motivation

In an implement run, the agent that builds a Step records what it built. It never says why the change is safe, or how strong its evidence for that is. When a repo has no smoke run or browser check, the Checker skips verification entirely. Small but risky changes — cache eviction, teardown order, wire formats, flags — then land on passing tests that never touched the risky path.

A `/brainstorm` run on 2026-10-01 compared this library with Cursor's pstack plugin ([pstack skills](https://github.com/cursor/plugins/tree/main/pstack/skills)). Three of its mechanisms fit into skills we already have, as a few paragraphs each:

- pstack's blast-radius skill asks for "the one fact it's safe because of" and ranks the evidence for that fact on a ladder. The ladder runs from "someone said so", through "you ran real code", to "you reproduced it in the running app".
- pstack's attack-the-premise principle says that once two fixes resting on the same assumption have failed, the next move is to question the assumption, not to write a third fix.
- pstack's encode-lessons-in-structure principle prefers a mechanism over more text when a lesson recurs.

The user wants these skills to become a system that learns from past mistakes and writes the lesson down for future runs. The third graft sharpens the loop `/retro` already runs.

The same run kept one other Idea: **Passing carries its proof, and the run recipe grows itself**. That one makes a Green claim show its evidence; this one names the fact the evidence must prove.

## Goal

Every Step names the one fact it is safe because of and how far its evidence for that fact goes. The Checker tries to break that fact with real code, even in a repo that documents no verification. Agents stop retrying fixes that share a wrong assumption. `/retro` encodes a recurring mistake in the strongest mechanism that can catch it.

## Decisions (locked)

What this run settled about the Direction.

- No new command or agent. The change is a few paragraphs in the existing Step agent, Oneshot agent, Checker, diagnosing-bugs and retro instructions.
- The builder's Outcome gains a line naming the safety fact, its level on the evidence ladder, and the command and output behind it.
- The Checker's verify step no longer skips when the repo has no verification convention. It writes a throwaway script that calls the real code and tries to break the fact. It runs that script, deletes it, and records the level reached.
- The fact must name what breaks if it is false, so "it compiles" does not qualify.
- After two fixes for the same failing check have failed, the agent writes down the one sentence both fixes assumed and tests it before trying a third. This applies in the Checker's loop back to Green and in diagnosing-bugs once every ranked guess is disproved.
- When `/retro` sends a mistake to an automated check, it picks the strongest mechanism first: a type that cannot hold the bad state, then a lint or CI rule, then a shared helper, then a runtime check.
- Adding a blast-radius check to `/code-review` was rejected: its reviewers see only the diff, and the Checker already acts on what they find.
- pstack's grouping of review findings by agreement between models was rejected: its value comes from reviewers on different models, which the plugin does not pin.

## Out of scope

Directions shown in the run that the user did not keep.

- **Proofs written before the code, kept as a regression suite.** Dropped because it adds a second test suite to maintain, which risks becoming slow and flaky beside the repo's real one.
- **Every rule ships with a test.** Each skill edit would need a small scenario showing that agents behave differently with the edit. Dropped for now because it changes how this repo itself is maintained, at the cost of a full agent run per arm per edit. It fits the user's aim of a learning system and may come back as its own Idea.

## Open questions

Where the next grilling session starts.

- What are the glossary terms for the safety fact and for the evidence ladder? The run used "Safety fact" and "Evidence rung".
- How many levels does the ladder have, and which level does a Step need before Green? Does a Spec's testing decisions set it?
- How does the safety fact meet the quoted evidence from the other kept Idea — one record or two?
- Does the Spec axis of `/code-review` flag a safety fact that names nothing that could break?
- Does widening the Checker's job need its own ADR, next to the one that set up a fresh Checker for each Step?
- How does the Checker keep its throwaway script out of the Step's commit in every case?
- Does the assumption rule count fixes per failing check, or per Step?
