# Grilling profiles live in the repo, one per person

A grilling session marks one option on each question as recommended. Across 136 grilling sessions on two hosts, the maintainer picked another option about one time in four, and the rate did not rise over six weeks. The same kinds of override kept coming back, such as widening a change to every related area, or leaving out a safeguard for a case with no users yet. Nothing carried them from one session to the next.

So each person now has a **Grilling profile** in each repo, at `.agents/refs/profiles/<name>.md`, holding their **Habits**. `/learn-habits` writes it, and only when you type it: it rebuilds your profile from your last 100 grilling sessions in this repo, on every host. No grilling skill runs it. A grilling session reads every profile in the repo. Your own Habit moves the recommendation, and a `*Your habit:*` line names it. Each teammate whose Habit applies is named on the option they would likely pick.

One person may commit under a different git email on each machine, so a profile lists every email its person commits with. A session finds yours by `git config user.email`. When no profile lists that email, the profile named after your `git config user.name` is yours, and `/learn-habits` adds the email to it. A rebuild keeps the list.

The profile lives in the repo so it travels with git and the whole team can see it. Each person has their own file, so teammates never edit the same one. A profile learns only from its own repo's sessions, because the same person chooses differently in different repos.

## Considered Options

- **One profile per person in the home folder, read from every repo.** Rejected: it does not travel with git, and a teammate's session cannot read it to show what that person would pick.
- **Host memory.** Rejected: each host keeps its own memory, and this plugin runs on Claude Code and Grok. Grok's memory also records single answers rather than habits.
- **Learning from every repo's sessions.** Rejected: a person's habits differ between repos, and a client repo's sessions would shape a file in another repo, which may be public.
- **Leaving the recommendation as the agent's own view, with a second mark for the expected pick.** Rejected: the agent would keep recommending what it expects you to turn down. The `*Your habit:*` line already shows when a Habit set the pick, and the agent says when it disagrees.
- **Letting a strong Habit turn a question into a declaration.** Rejected: functional decisions stay questions however much the person agrees, and a wrong guess would pass in silence.
- **Learning inside `/retro`.** Rejected: `/grilling` never starts `/retro`.
- **Running `/learn-habits` at the end of every grilling session.** This was the first design, and it folded in the one session that had just finished. Rejected: the maintainer chose to have it run only when typed.
- **Changing grilling's default to recommend wider scope.** Rejected: that would move every person's recommendations. A profile moves them only for the person it describes.
- **A git `.mailmap` that maps each of a person's emails to one.** Rejected: someone must write and keep it by hand in every repo, while the profile's file name already names the person.
- **One profile per email.** Rejected: one person's sessions would split across files that each learn more slowly, and grilling would name the person as their own teammate.
- **Asking before adding an email to the profile found by git name.** Rejected: that file name is already taken, so a person with that name could not get a profile of their own either way.

## Consequences

- A profile in a public repo publishes a named person's Habits and every git email they commit with. Git commits already carry those emails.
- Two teammates with the same git name share one profile. A person whose git name differs between machines gets a second profile, and joining the two is a hand edit.
- `/learn-habits` is typed only (`disable-model-invocation`), because no skill loads it. It does not start a `/retro` of its own.
- A profile holds the sessions up to the last typed run. Later sessions do not move it until someone types `/learn-habits` again.
- A new teammate has no profile until they type `/learn-habits`.
- The profile is an **Owned file**, and `/learn-habits` is not `/retro`, so [ADR-0040](0040-retro-writes-only-owned-files.md) is unchanged.
