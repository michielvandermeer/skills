---
name: explain
description: Explain anything as a diagram in the chat, an HTML page, or a narrated video, picking the format that fits.
disable-model-invocation: true
argument-hint: "[topic] [as a diagram | page | video]"
---

# Explain

Answer with something to look at instead of prose. What you make is an **Explanation**, in one of three **formats**, each richer and slower than the last:

- **Diagram** — box-drawing characters in the chat. Fits one structure or flow that fits on a screen.
- **Page** — one self-contained HTML file. Fits a topic with several parts to explore, real graphics, or controls to play with.
- **Video** — a narrated 3Blue1Brown-style MP4. Fits an idea that unfolds over time, such as an algorithm running step by step.

The topic is anything: part of this repo, a branch's changes, an ADR, or an outside idea. With no topic, explain the last thing discussed in the session. With nothing to go on, ask what to explain and wait.

Run the `/plain-language` skill before writing anything a person reads — the confirmation, labels, page text, narration — and hold its bar throughout. Write for a developer who does not know the topic yet, unless the request names another reader.

## Process

### 1. Gather the facts

- **Repo topic** — dispatch a `skills:explorer` with named questions about the code the topic touches. Carry its report, never the files. Every box, arrow, and claim traces to a file it names.
- **Outside idea** — well-known material comes from your own knowledge. Check anything recent, niche, or numeric against primary sources on the web.

Keep the sources as you go: files for a repo topic, links for anything looked up.

Done when every claim the Explanation will make has a source or is textbook material.

### 2. Pick the format

When the request names a format in plain words — "as a video", "draw it" — that is the format: go straight to step 3.

Otherwise pick the format that fits, by the list above, and confirm before building: the format, one line on why, and for a video the scene list. Wait, then build the format the user confirms or names instead.

Done when the user named the format or confirmed it.

### 3. Build

- **Diagram** — in a code block in the chat, at most 80 columns wide, every box labelled in the topic's own words. List the sources under it. The run ends here.
- **Page** — follow [PAGE.md](PAGE.md).
- **Video** — follow [VIDEO.md](VIDEO.md).

Page and video files go in `explain/<slug>/` under the system temp folder, `<slug>` being the topic in a few kebab-case words.

Done when the diagram is in the chat, or the page or video has passed the check its file sets.

### 4. Hand over

Open the result — `xdg-open <path>` on Linux, `open <path>` on macOS, `start <path>` on Windows — and print its absolute path, saying that many systems empty the temp folder on restart. List the sources.

Done when the result is open, its path is printed, and its sources are listed.

## Follow-ups

The files beside the output are kept for one reader: a follow-up in this session. A follow-up — "slow down scene 2", "add a slider for the load factor" — edits those files and builds again through the same check.
