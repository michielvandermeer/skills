# Idea — Passing carries its proof

## Motivation

The implement commands call a Step finished when its tests pass, plus "any verification the repo's conventions demand for the surface touched". A repo with no such convention skips that part. No skill creates the verification, keeps it current, or asks for evidence that the feature works in the running app. The agent that builds a Step records what it built, but never says why the change is safe or how strong its evidence is. Small but risky changes — cache eviction, teardown order, wire formats, flags — land on passing tests that never touched the risky path. Tests can pass while the feature is broken, and nothing in a run would notice.

A `/brainstorm` run on 2026-10-01 compared this library with Cursor's pstack plugin ([pstack skills](https://github.com/cursor/plugins/tree/main/pstack/skills)). Other agent toolkits have settled, independently of each other, on two things we lack:

- A recipe, kept in the project, for launching and driving the app: pstack's verification-skill generator, Claude Code's own verify and run-skill commands, gstack's per-project test plans, and Anthropic's webapp-testing skill.
- A rule that nobody claims "done" without fresh evidence quoted next to the claim: superpowers' [verification before completion](https://raw.githubusercontent.com/obra/superpowers/main/skills/verification-before-completion/SKILL.md), [Claude Code best practices](https://code.claude.com/docs/en/best-practices) ("show evidence rather than asserting success"), and gstack's QA screenshots.

Because several toolkits arrived at these on their own, we adopt something proven in practice rather than one author's taste. More sources: [gstack skills](https://github.com/garrytan/gstack/blob/main/docs/skills.md), [Anthropic webapp-testing](https://www.skills.sh/anthropics/skills/webapp-testing), [AGENTS.md](https://github.com/agentsmd/agents.md), [Claude Code skills](https://code.claude.com/docs/en/skills).

Three pstack mechanisms say what the evidence must prove and what to do when it fails:

- pstack's blast-radius skill asks for "the one fact it's safe because of" and ranks the evidence for that fact on a ladder. The ladder runs from "someone said so", through "you ran real code", to "you reproduced it in the running app".
- pstack's attack-the-premise principle says that once two fixes resting on the same assumption have failed, the next move is to question the assumption, not to write a third fix.
- pstack's encode-lessons-in-structure principle prefers a mechanism over more text when a lesson recurs.

The user wants these skills to become a system that learns from past mistakes and writes the lesson down for future runs. Two loops here do that: a run recipe that the first run writes and later runs correct, and a `/retro` that encodes a recurring mistake in the strongest mechanism that can catch it.

The run first kept these as two Ideas. The user merged them, because naming the fact and proving it are one claim.

## Goal

A Step, or an Oneshot agent's whole run, counts as Green only when it names the one fact the change is safe because of and quotes evidence for that fact that a fresh agent re-ran and saw. The way to launch and drive the app is learnt once per repo, saved in that repo, and corrected only when it leads an agent wrong. Agents stop retrying fixes that share a wrong assumption. `/retro` turns a recurring mistake into the strongest check that can catch it.

## Decisions (locked)

What the run settled about this Direction.

- The change lives inside the existing implement commands, diagnosing-bugs and retro. No new command or agent.
- **One record.** The builder's Outcome gains one entry: the safety fact, its level on the evidence ladder, and the evidence behind it. The evidence is the command run, its exit code and an excerpt of its output, or a screenshot or transcript saved for the run.
- The fact must name what breaks if it is false, so "it compiles" does not qualify.
- The Checker re-runs that evidence itself and refuses Green without it. In a repo with no verification convention it no longer skips: it writes a throwaway script that calls the real code and tries to break the fact, runs it, deletes it, and records the level reached.
- The final report quotes the evidence instead of saying "all passing".
- **Run recipe.** The first Checker or Oneshot agent that has to drive the running app writes down what worked: how to launch it, how to tell it is ready, how to drive it, what evidence to keep, and how to clean up. That record lives in the consuming repo. Later runs follow it, and an agent edits it only when it steered them wrong, so a run that follows it makes no change to it.
- **Question the shared assumption.** After two fixes for the same failing check have failed, the agent writes down the one sentence both fixes assumed and tests it before trying a third. This applies in the Checker's loop back to Green and in diagnosing-bugs once every ranked guess is disproved.
- **Learning loop.** `/retro` treats a recipe that steered an agent wrong as a lesson, the way it treats a Correction today. When it sends a mistake to an automated check, it picks the strongest mechanism first: a type that cannot hold the bad state, then a lint or CI rule, then a shared helper, then a runtime check.
- Driving the app stays local, inside the rule that implement never changes a live system.
- The rule works on every host the plugin supports. A host's own browser tools may help write the recipe, but the recipe must run from a plain shell command.
- Adding a blast-radius check to `/code-review` was rejected: its reviewers see only the diff, and the Checker already acts on what they find.
- pstack's grouping of review findings by agreement between models was rejected: its value comes from reviewers on different models, which the plugin does not pin.

## Out of scope

Directions shown in the run that the user did not keep.

- **Proofs written before the code, kept as a regression suite.** Each Spec claim would get a script, written before the feature, that stays in the repo for good. Dropped because it adds a second test suite to maintain, which risks becoming slow and flaky beside the repo's real one.
- **Every rule ships with a test.** Each skill edit would need a small scenario showing that agents behave differently with the edit than without it. Dropped for now because it changes how this repo itself is maintained and costs a full agent run per arm per edit. It fits the user's aim of a learning system and may come back as its own Idea.
- **A reviewer on a second model**, from pstack's multi-model review. Blocked because no agent may pin a model, since other hosts cannot honour a pinned Claude tier.
- pstack's sticky mode, naming a principle in every reply, and cloud worker swarms. Only pstack does these, and they do not fit hosts other than Cursor.

## Open questions

Where the next grilling session starts.

- What are the glossary terms? The run used "Proof" for the quoted evidence, "Safety fact", "Evidence rung" and "Verify recipe". The dropped regression-suite Direction also used "Proof", with a different meaning.
- How many levels does the ladder have, and which level does a Step need before Green? Does a Spec's testing decisions set it?
- Where in the consuming repo does the recipe live? The open Agent Skills layout puts a project skill under its own skills folder. Claude Code's own verify command may write a second recipe in its own folder. Should we read that one first, or adopt it outright?
- What counts as evidence for each surface (web, command line, HTTP service, library), and what does a library with no running surface quote?
- How does a flaky recipe stay from blocking a land on noise? Does a flaky failure follow the same rule as a flaky failure after rebase?
- Does the recipe have a check a run performs before trusting it, like pstack's "doctor" section?
- How does the Checker stop an agent from pasting output it never ran? Is re-running from a fresh context enough?
- Does the Spec axis of `/code-review` flag a safety fact that names nothing that could break?
- How does the Checker keep its throwaway script out of the Step's commit in every case?
- Does the assumption rule count fixes per failing check, or per Step?
- Does widening the Checker's job need its own ADR, next to the one that set up a fresh Checker for each Step, and does Green's definition in the glossary change?
