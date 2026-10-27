---
name: simulate-first-users
description: Send five simulated first-time users through your app in real browsers, then triage what tripped them up into Issues with screenshots.
argument-hint: "[first success] [url]"
disable-model-invocation: true
model: sonnet
effort: high
---

# Simulate first users

Five **First users**, each a sub-agent playing a different person who meets the app for the first time, walk from the landing page toward **First success** in their own browser. Each screenshots every moment its person is confused, stuck, or annoyed. Their moments, merged and ranked by how many First users hit each one, become the seed of a `/triage` run, which files them as Issues with the screenshots attached. This run fixes nothing: to check fixes, run it again.

Run `/technical-writing` before the first message and hold its bar for every message and for the seed. The briefs you send First users are for agents and sit outside that bar.

## 1. Reach the app

The argument names First success, such as `sign up and create a project`, a URL, both, or neither.

1. Start the app. When the repo has a Verify skill (`.claude/skills/verify/`, or a context's own in a repo with a `CONTEXT-MAP.md`), follow its Launch and Doctor sections and take the URL they reach the app at. Otherwise take the URL from the argument. With neither, ask for one and stop until it arrives.
2. When the argument names no First success, read the app's landing page and README, and state in one line what a newcomer comes for: `First success: <it>`. Go on without waiting.
3. Get the browser ready as [BROWSER.md](BROWSER.md) says. When its check stops, stop the run there, before any First user goes out.

Open with one message: the URL, First success, and the five First users by name. When the URL's host is not local (`localhost`, `127.0.0.1`, or a private address), add that the breaker submits junk data there.

Done: the app answers at the URL, First success is one stated line, and BROWSER.md's check passed.

## 2. Send the First users

Make the run's scratch folder, `.agents/first-users/<yyyy-mm-dd-hhmm>/` at the repo root, holding a `.gitignore` of `*`, with one subfolder per First user, `1` to `5`. Resolve its absolute path once and hand every path on as a literal.

Dispatch five general-purpose sub-agents, all in one message, on your own model and effort. Each brief carries the URL, First success, its First user's description below, its subfolder's absolute path, BROWSER.md's commands for that First user with every value filled in, and these rules:

- You meet this app for the first time. Act on what your person sees on screen: page text, labels, buttons, messages. The repo's code, the page source, the network log, and guessed URLs stay closed to you, so a missing label is missing.
- Walk from the landing page toward First success the way your person would.
- Every time your person is confused, stuck, or annoyed, take a screenshot into your subfolder, numbered in order (`01.png`, `02.png`), and log one **moment**: the screenshot's path, what you were trying to do, what you did, what the screen showed, and why your person reacted. Quote UI text exactly.
- Stop at First success, or where your person gives up. A wall only a real person passes, such as a code sent by email or text, a card payment, or a CAPTCHA, is a stuck moment and the end of your walk. Enter obvious test values, never real payment details or real personal data.
- Close your browser session before you report.
- Report whether you reached First success, the steps you took, and every moment, in order.

The five First users:

1. **The impatient one.** Skims, and reads nothing longer than a line. Clicks the first button that looks like progress. Quits at the first error, or at any wait longer than a few seconds.
2. **The skeptic.** Before signing up, reads pricing, terms, and privacy, looking for what happens to their data and their money. Stops at a vague answer or a missing page.
3. **The mobile user.** Does everything on a 375px phone screen over slow 3G, as BROWSER.md sets up. Annoyed by anything cut off, too small to tap, or slow to appear.
4. **The non-native English speaker.** Follows only what the UI literally says, word by word. Idioms, jargon, and wordplay land as noise, and an icon without a label is a guess.
5. **The breaker.** Pastes junk into every field: very long text, emoji, a `<script>` tag, a blank. Hits back in the middle of a flow, double-clicks every button, and reloads mid-submit. Still tries to reach First success.

Wait for each First user's own report. Done: all five reports have landed.

## 3. Write the seed

Merge the moments into **findings**, one per distinct problem: the same dead button met by three First users is one finding with three First users. Order the findings by how many First users hit them, most first. Break a tie by how early in the walk the problem appears.

Write the seed as `seed.md` in the scratch folder. Above the findings: the URL, First success, the date, and which First users reached First success. Each finding has:

- a title naming the problem as a person meets it
- the First users who hit it, and their count
- what each saw and did, in words a Product reader understands, quoting UI text
- its screenshots as Markdown images with absolute paths and alt text, such as `![The impatient one: Continue does nothing](/abs/path/1/01.png)`

Done: every moment belongs to exactly one finding, and every screenshot a moment names is in the seed.

## 4. Triage

When step 1 started the app through the Verify skill, stop it with that skill's Cleanup section.

Read [`triage/SKILL.md`](../triage/SKILL.md) and follow it with `seed.md` as the seed — `/triage` does not load as a skill. It files each finding as a Spec or a parked Issue, attaches each finding's screenshots to its Issue, and ends with its summary and `/retro`.

Then delete the scratch folder. When the triage summary names screenshots for the user to add by hand, keep the folder and name its path instead.

Done: the triage summary is shown, `/retro` has finished, and the scratch folder is deleted or named.
