---
name: hunt-application-improvements
description: Send Hunters that play outsiders, such as users, an attacker, a search crawler, and reviewers, through your locally running app to find as many problems as they can, then triage them into Issues with screenshots.
argument-hint: "[instructions]"
disable-model-invocation: true
model: sonnet
effort: high
---

# Hunt application improvements

**Hunters**, each a sub-agent playing one kind of outsider along one **Hunt axis**, go through the locally running app all at once. Each sees only what its person can see. The repo's code is closed to every one of them. Their findings, merged and ranked, become the seed of a `/triage` run, which files them as Specs or parked Issues with the screenshots attached. This run fixes nothing: to check fixes, run it again.

The argument holds optional instructions in plain words, such as `the attacker and the breaker on the billing pages` or `stop after 10 minutes`.

Before the first message, read [`technical-writing/SKILL.md`](../technical-writing/SKILL.md) and follow it. `/technical-writing` does not load as a skill. Hold its bar for every message and for the seed. The briefs you send Hunters are for agents and sit outside that bar.

The ten Hunt axes, in this order, each briefed in [AXES.md](AXES.md) with its subfolder slug: the impatient one, the skeptic, the slow-connection user, the non-native English speaker, the breaker, the attacker, the search crawler, the keyboard user, the design reviewer, the privacy reviewer.

## 1. Read the instructions and pick the axes

- No instructions: all ten axes.
- Instructions that name axes: each axis they name gets a Hunter, with the instructions as its focus.
- Instructions that name no axis: one **free-form** Hunter, slug `free-form`, whose whole brief is the instructions and the shared rules in step 3. It may see whatever any axis sees, and the repo stays closed to it too.

A **stop goal** in the instructions, such as `stop after 10 minutes` or `stop at 100 findings`, is given to every Hunter as its own limit. A count is split evenly between the Hunters that run, rounded up. With no stop goal, each Hunter stops when no kind of page is left unvisited.

Done: the axes, or the one free-form Hunter, are chosen, and the stop goal is stated or absent.

## 2. Start the app

1. Find the repo's Verify skill: `.claude/skills/verify/`, or a context's own in a repo with a `CONTEXT-MAP.md`. With none, stop with `no Verify skill: run /setup verify`.
2. Follow its Launch and Doctor sections, and take the URL they reach the app at. This run takes no URL from the user and asks for none.
3. Make the scratch folder: `.agents/hunt-application/<yyyy-mm-dd-hhmm>/` at the repo root, holding a `.gitignore` of `*`, with one subfolder per Hunter named for its slug. Resolve its absolute path once and hand every path on as a literal. The folder's stamp, `<yyyy-mm-dd-hhmm>`, is the `<stamp>` in BROWSER.md.
4. Unless the search crawler is the only Hunter, get the browser ready as [BROWSER.md](BROWSER.md) says. When its check stops, stop the app with the Verify skill's Cleanup section and stop the run there, before any Hunter goes out.

Open with one message: the URL, the axes that run, and the stop goal when there is one.

Done: the app answers at the URL, the scratch folder exists, and BROWSER.md's check passed or was not needed.

## 3. Send the Hunters

Dispatch one `general-purpose` sub-agent per Hunter, all in one message, on your own model and effort. Each brief carries:

- its axis's brief from [AXES.md](AXES.md), or for the free-form Hunter the instructions alone
- the instructions, when there are any
- the app's URL
- its own subfolder's absolute path
- BROWSER.md's commands for its axis with every value filled in, its session named `<stamp>-<slug>`
- its stop goal, when there is one
- these rules:
  - Act on what your person can see. The repo's code is closed to you, so a missing label is missing and a key counts only where an outsider finds it. Report a key, token, or password by where you found it, never by its value.
  - Go through the whole app. Follow every link and menu you can reach, logged out and then logged in. Visit one page of each kind: one project page, not all of them. Stop at your stop goal, or when no kind of page is left unvisited.
  - With a time limit, check the time with `date` as you go, and report what you have once the limit passes.
  - Stay on the app's host and port. A link to another host or port is noted, never followed.
  - Signing in is the app's job, and a local run may need none. A sign-in wall you meet anyway, or one only a real person passes, such as a code sent by email, a CAPTCHA, or a card payment, is a finding and ends your logged-in walk. Enter obvious test values, never real payment details or real personal data.
  - Log every finding. Where there is a screen, screenshot it into your subfolder, numbered in order (`01.png`, `02.png`). For each finding log the screenshot's path, what you were trying to do, what you did, what you saw, quoting UI text exactly, and why your person reacted.
  - Close your browser session before you report.
  - Report the kinds of page you covered, then every finding, in order.

Wait for each Hunter's own report. Done: every Hunter has reported.

## 4. Stop the app and write the seed

Stop the app with the Verify skill's Cleanup section.

Merge the findings into one per distinct problem: the same dead button met by three Hunters is one finding with three Hunters. Give each a severity: `security or data loss`, `blocks a person`, or `annoys`. Order the findings by severity, in that order, then by how many Hunters hit them, most first, then by how early in a walk the problem appears.

Write the seed as `seed.md` in the scratch folder. Above the findings: the URL the Verify skill gave, the date, the axes that ran, the stop goal when there was one, and each Hunter's coverage. Each finding has:

- a title naming the problem as a person meets it
- its severity
- the Hunters who hit it, and their count
- what each saw and did, in words a Product reader understands, quoting UI text
- its screenshots as Markdown images with absolute paths and alt text, such as `![The impatient one: Continue does nothing](/abs/path/impatient/01.png)`

Done: every Hunter's finding belongs to exactly one finding in the seed, and every screenshot a Hunter names is in the seed.

## 5. Triage

Read [`triage/SKILL.md`](../triage/SKILL.md) and follow it with `seed.md` as the seed. `/triage` does not load as a skill. It files each finding as a Spec or a parked Issue, attaches each finding's screenshots to its Issue, and ends with its summary.

Then delete the scratch folder. When the triage summary names screenshots for the user to add by hand, keep the folder and name its path instead.

Done: the triage summary is shown, and the scratch folder is deleted or named.
