# Idea — Passing carries its proof, and the run recipe grows itself

## Motivation

The implement commands call a Step finished when its tests pass, plus "any verification the repo's conventions demand for the surface touched". A repo with no such convention skips that part. No skill creates the verification, keeps it current, or asks for evidence that the feature works in the running app. Tests can pass while the feature is broken, and nothing in a run would notice.

A `/brainstorm` run on 2026-10-01 compared this library with Cursor's pstack plugin ([pstack skills](https://github.com/cursor/plugins/tree/main/pstack/skills)). Other agent toolkits have settled, independently of each other, on the two things we lack:

- A recipe, kept in the project, for launching and driving the app: pstack's verification-skill generator, Claude Code's own verify and run-skill commands, gstack's per-project test plans, and Anthropic's webapp-testing skill.
- A rule that nobody claims "done" without fresh evidence quoted next to the claim: superpowers' [verification before completion](https://raw.githubusercontent.com/obra/superpowers/main/skills/verification-before-completion/SKILL.md), [Claude Code best practices](https://code.claude.com/docs/en/best-practices) ("show evidence rather than asserting success"), and gstack's QA screenshots.

Because several toolkits arrived at these on their own, we adopt something proven in practice rather than one author's taste. More sources: [gstack skills](https://github.com/garrytan/gstack/blob/main/docs/skills.md), [Anthropic webapp-testing](https://www.skills.sh/anthropics/skills/webapp-testing), [AGENTS.md](https://github.com/agentsmd/agents.md), [Claude Code skills](https://code.claude.com/docs/en/skills).

The user wants these skills to become a system that learns from past mistakes and writes the lesson down for future runs. A recipe that the first run writes and later runs correct is one such loop.

The same run kept one other Idea: **The builder names the one fact that keeps a change safe**. The two fit together. This Idea makes a Green claim show its evidence; that one makes the builder say which fact the evidence must prove.

## Goal

A Step, or an Oneshot agent's whole run, counts as Green only when it quotes evidence that a fresh agent re-ran and saw. The way to launch and drive the app is learnt once per repo, saved in that repo, and corrected only when it leads an agent wrong.

## Decisions (locked)

What this run settled about the Direction.

- The change lives inside the existing implement commands. No new command or agent.
- Green needs quoted evidence next to the claim: the command run, its exit code and an excerpt of its output, or a screenshot or transcript saved for the run.
- The Checker re-runs that evidence itself and refuses Green without it. The final report quotes the evidence instead of saying "all passing".
- The first Checker or Oneshot agent that has to drive the running app writes down what worked: how to launch it, how to tell it is ready, how to drive it, what evidence to keep, and how to clean up. That record lives in the consuming repo.
- Later runs follow the recipe. An agent edits it only when it steered them wrong, so a run that follows it makes no change to it.
- `/retro` treats a recipe that steered an agent wrong as a lesson, the way it treats a Correction today.
- Driving the app stays local, inside the rule that implement never changes a live system.
- The rule works on every host the plugin supports. A host's own browser tools may help write the recipe, but the recipe must run from a plain shell command.

## Out of scope

Directions shown in the run that the user did not keep.

- **Proofs written before the code, kept as a regression suite.** Each Spec claim would get a script, written before the feature, that stays in the repo for good. Dropped because it is this Idea plus a second test suite to maintain, and that suite risks becoming slow and flaky beside the repo's real one.
- **Every rule ships with a test.** Each skill edit would need a small scenario showing that agents behave differently with the edit than without it. Dropped for now because it changes how this repo itself is maintained and costs a full agent run per arm per edit. It fits the user's aim of a learning system and may come back as its own Idea.
- **A reviewer on a second model**, from pstack's multi-model review. Blocked because no agent may pin a model, since other hosts cannot honour a pinned Claude tier.
- pstack's sticky mode, naming a principle in every reply, and cloud worker swarms. Only pstack does these, and they do not fit hosts other than Cursor.

## Open questions

Where the next grilling session starts.

- What is the glossary term for the quoted evidence, and for the recipe? The run used "Proof" and "Verify recipe". The dropped Direction also used "Proof", with a different meaning.
- Where in the consuming repo does the recipe live? The open Agent Skills layout puts a project skill under its own skills folder. Claude Code's own verify command may write a second recipe in its own folder. Should we read that one first, or adopt it outright?
- What counts as evidence for each surface (web, command line, HTTP service, library), and what does a library with no running surface quote?
- How does a flaky recipe stay from blocking a land on noise? Does a flaky failure follow the same rule as a flaky failure after rebase?
- Does the recipe have a check a run performs before trusting it, like pstack's "doctor" section?
- How does the Checker stop an agent from pasting output it never ran? Is re-running from a fresh context enough?
- Does this need an ADR that widens the Checker's job, and does Green's definition in the glossary change?
