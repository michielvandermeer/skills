---
name: hunt-codebase-improvements
description: Hunt your codebase for improvements along eleven axes, such as state bugs, cruft, slow pages, wasted CI time, and leaked keys, then file what the hunt finds as `needs-triage` Issues.
argument-hint: "[instructions] [stop goal] [url]"
disable-model-invocation: true
model: sonnet
effort: high
---

# Hunt codebase improvements

**Hunters**, each a sub-agent, search the codebase along one **Hunt axis** each, all at once. Their findings, merged into one list, are filed as Issues in `needs-triage`, for you to sort with `/triage`. This run fixes nothing and makes no commit.

The argument holds optional instructions in plain words, such as `make Statistics' form inputs match Compliance` or `why are our outbound calls flaky`, may hold a URL, and may hold a **stop goal**, such as `stop after 10 minutes` or `stop at 100 findings`. A stop goal comes alone or with instructions, and is not itself an instruction.

Before the first message, read [`technical-writing/SKILL.md`](../technical-writing/SKILL.md) and follow it — `/technical-writing` does not load as a skill — and hold its bar for every message and for the findings list. The briefs you send Hunters are for agents and sit outside that bar.

The eleven Hunt axes, in this order, each briefed in [AXES.md](AXES.md): State bugs, Cruft, Outbound calls, UI polish, Performance, CI time, Scheduled jobs, Scaling needs, Security, Payments, Operations.

## 1. Read the instructions and pick the axes

- No instructions: all eleven axes.
- Instructions: each axis whose ground they name gets a Hunter, with the instructions as its focus.
- Instructions that name no axis: one **free-form** Hunter, whose whole brief is the instructions and the shared rules in step 4.

A URL in the instructions is the app's URL. It is also a reference app's URL when the instructions name a reference app and the URL is clearly that app's.

A stop goal becomes each Hunter's own limit. A time limit goes to every Hunter whole: with `stop after 10 minutes`, each Hunter stops searching after 10 minutes and reports what it has. A count is split evenly between the Hunters that run, rounded up, and each Hunter's share replaces its cap of five findings: with `stop at 100 findings` and ten Hunters, each stops at 10. With no stop goal, each Hunter reports at most five.

Done: the axes, or the one free-form Hunter, are chosen, and each Hunter's limit is known.

## 2. Reach the app

Skip this step when no chosen axis needs a running app. Only UI polish and performance do; a free-form Hunter may use the app when one is up.

1. Start the app. When the repo has a Verify skill (`.claude/skills/verify/`, or a context's own in a repo with a `CONTEXT-MAP.md`), follow its Launch and Doctor sections and take the URL they reach the app at. Otherwise take the URL from the instructions.
2. With neither, never ask and never stop. UI polish and performance work from the code alone, and the closing summary says the app was not run and which checks skipped.
3. Only this run launches the app, once, so no two Hunters start copies on one port.
4. A reference app named in the instructions is reached the same way: through its Verify skill when it lives in the same repo, else through a URL in the instructions. When neither reaches it, the UI polish Hunter compares against the reference app's code where the repo holds it, and the summary says the reference app was not run.

Done: the app answers at the URL, or the run has noted that it could not be reached.

## 3. Check what can run

Make the scratch folder first: `.agents/hunts/<yyyy-mm-dd-hhmm>/` at the repo root, holding a `.gitignore` of `*`, with one subfolder per Hunter named for its axis: `state-bugs`, `cruft`, `outbound-calls`, `ui-polish`, `performance`, `ci-time`, `scheduled-jobs`, `scaling-needs`, `security`, `payments`, `operations`, `free-form`. Resolve its absolute path once and hand every path on as a literal. The folder's stamp, `<yyyy-mm-dd-hhmm>`, is the `<stamp>` below.

Before any Hunter goes out:

- **Browser**, only when UI polish is chosen and the app is running: run the check in [`hunt-application-improvements/BROWSER.md`](../hunt-application-improvements/BROWSER.md), by path, with the `ui-polish` subfolder as its one subfolder and the config below, session `<stamp>-check`. When it fails, UI polish works from the code alone and the summary says why. Unlike `/hunt-application-improvements`, a failed check does not stop the run.
- **CI time**: read the remote with `git remote get-url origin` and run `gh auth status`. A remote that is not GitHub, or a failed `gh auth status`, means the CI time axis does not run: it gets no Hunter and the summary says why. A focused run that names an axis that cannot run still reports that line.

Done: the scratch folder exists, and every chosen axis is marked as running, running from the code alone, or not running with its reason.

## 4. Send the Hunters

Dispatch one `general-purpose` sub-agent per Hunter that runs, all in one message, on your own model and effort. Each brief carries:

- its axis's brief from [AXES.md](AXES.md), or for the free-form Hunter the instructions alone
- the instructions, when there are any
- its limit from the stop goal, when there is one
- the app's URL, when the app is running
- its own subfolder's absolute path, for screenshots and logs
- these rules:
  - Change no file outside your subfolder.
  - Run only commands that change nothing.
  - Report at most five findings, or your share of the stop goal's count, your strongest by evidence, and say how many more you saw.
  - With a time limit, check the time with `date` as you go, and report what you have once the limit passes.
  - When you find nothing along your axis, report zero findings and say so. Invent none.
  - Report in plain text: each finding's title, axis, evidence, and screenshot paths, then the count of further findings you saw.

The UI polish Hunter's brief also carries BROWSER.md's commands with every value filled in and its own session named `<stamp>-ui`. Its own `cli.json`, in the `ui-polish` subfolder, is the one BROWSER.md writes, with its 1440 by 900 desktop viewport. No Hunter uses a phone width.

Wait for each Hunter's own report. Done: every Hunter has reported.

## 5. Stop the app and write the findings list

When step 2 started the app through the Verify skill, stop it with that skill's Cleanup section.

Merge the reports into `findings.md` in the scratch folder: one finding per distinct problem. A problem two Hunters both found is one finding naming both axes. Group the findings by axis in the order above. Do not rank them by severity. Above the findings: the instructions, the stop goal when there is one, the URL when the app ran, the date, and each axis that did not run, with its reason. Each finding has:

- a title naming the problem as a developer meets it
- its axis, or both axes
- its evidence, as the Hunter reported it
- its screenshots as Markdown images with absolute paths and alt text, such as `![Statistics: the save button has no disabled state](/abs/path/ui-polish/01.png)`

Done: every report's findings belong to exactly one finding, and every screenshot a report names is in `findings.md`.

## 6. File the findings

Read [`hunt-application-improvements/FILING.md`](../hunt-application-improvements/FILING.md) and follow it with `findings.md` as the findings. Add to its summary:

- one line per axis that could not run, with the reason
- one line per axis that ran from the code alone because the app was not running, and the reference-app line from step 2 and the browser line from step 3 when they apply
- for each axis whose Hunter saw more findings than it reported, the axis and how many more it saw

Done: the closing summary is shown, and the scratch folder is deleted or named.
