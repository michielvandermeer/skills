# Grilling profiles live in the repo, one per person

A grilling session marks one option on each question as recommended. Across 136 grilling sessions on two hosts, the maintainer picked another option about one time in four, and the rate did not rise over six weeks. The same kinds of override kept coming back, such as widening a change to every related area, or leaving out a safeguard for a case with no users yet. Nothing carried them from one session to the next.

So each person now has a **Grilling profile** in each repo, at `.agents/refs/profiles/<name>.md`, holding their **Habits**. `/learn-habits` writes it. When you type it, it rebuilds your profile from your last 100 grilling sessions in this repo, on every host. `/grill-with-docs`, `/refine`, and `/wayfinder` load it just before `/retro`, and `/grill-me` loads it last, to add the session that just finished. A grilling session reads every profile in the repo. Your own Habit moves the recommendation, and a `*Your habit:*` line names it. Each teammate whose Habit applies is named on the option they would likely pick.

The profile lives in the repo so it travels with git and the whole team can see it. Each person has their own file, so teammates never edit the same one. A profile learns only from its own repo's sessions, because the same person chooses differently in different repos.

## Considered Options

- **One profile per person in the home folder, read from every repo.** Rejected: it does not travel with git, and a teammate's session cannot read it to show what that person would pick.
- **Host memory.** Rejected: each host keeps its own memory, and this plugin runs on Claude Code and Grok. Grok's memory also records single answers rather than habits. [ADR-0061](0061-hillclimb-keeps-only-measured-wins.md) rejected host memory for the Attempt log on the same ground.
- **Learning from every repo's sessions.** Rejected: a person's habits differ between repos, and a client repo's sessions would shape a file in another repo, which may be public.
- **Leaving the recommendation as the agent's own view, with a second mark for the expected pick.** Rejected: the agent would keep recommending what it expects you to turn down. The `*Your habit:*` line already shows when a Habit set the pick, and the agent says when it disagrees.
- **Letting a strong Habit turn a question into a declaration.** Rejected: functional decisions stay questions however much the person agrees, and a wrong guess would pass in silence.
- **Learning inside `/retro`.** Rejected: `/grill-me` never starts `/retro`, and the same skill that learns from one session also rebuilds from many when typed.
- **Changing grilling's default to recommend wider scope.** Rejected: that would move every person's recommendations. A profile moves them only for the person it describes.

## Consequences

- A profile in a public repo publishes a named person's Habits and git email. Git commits already carry that email.
- `/learn-habits` is model-invoked, because four skills load it. It does not start a `/retro` of its own.
- A session stopped early skips `/learn-habits`, as it skips `/retro`. The next typed run picks that session up.
- A new teammate has no profile until their first grilling session in the repo ends, or until they type `/learn-habits`.
- The profile is an **Owned file**, and `/learn-habits` is not `/retro`, so [ADR-0040](0040-retro-writes-only-owned-files.md) is unchanged.
