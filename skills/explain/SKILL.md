---
name: explain
description: Explain anything as a written walkthrough, a diagram in the chat, an HTML page, or a narrated video, picking the format that fits.
argument-hint: "[topic] [as a walkthrough | diagram | page | video]"
disable-model-invocation: true
model: sonnet
effort: high
---

# Explain

What you make is an **Explanation**, in one of four **formats**, each richer and slower than the last:

- **Walkthrough**: written sections in the chat, at the level a senior engineer needs to start working in the code. Fits "how does X work" about part of a codebase: its flow, where things live, and what is surprising.
- **Diagram** — box-drawing characters in the chat. Fits one structure or flow that fits on a screen.
- **Page** — one self-contained HTML file. Fits a topic with several parts to explore, real graphics, or controls to play with.
- **Video** — a narrated 3Blue1Brown-style MP4. Fits an idea that unfolds over time, such as an algorithm running step by step.

The topic is anything: part of this repo, a branch's changes, an ADR, or an outside idea. With no topic, explain the last thing discussed in the session. With nothing to go on, ask what to explain and wait.

Before writing anything a person reads (the confirmation, labels, page text, narration), read [`technical-writing/SKILL.md`](../technical-writing/SKILL.md) and follow it — `/technical-writing` does not load as a skill — and hold its bar throughout. Write for a developer who does not know the topic yet, unless the request names another reader.

## Process

### 1. Gather the facts

- **Repo topic**: dispatch `skills:explorer` agents, briefed as [EXPLORE.md](EXPLORE.md) says. A topic inside one module gets one explorer. A topic that spans several modules or services gets two to four, all in one message, each on its own angle of the topic, such as the entry points, the data, or one service. Carry their reports, never the files. Where two reports disagree, read the code they cite and settle it. Every box, arrow, and claim traces to a file a report names.
- **Outside idea** — well-known material comes from your own knowledge. Check anything recent, niche, or numeric against primary sources on the web.

Keep the sources as you go: files for a repo topic, links for anything looked up.

Done when every claim the Explanation will make has a source or is textbook material.

### 2. Pick the format

When the request names a format in plain words — "as a video", "draw it" — that is the format: go straight to step 3.

Otherwise pick the format that fits, by the list above, and confirm before building: the format, one line on why, and for a video the scene list. Wait, then build the format the user confirms or names instead.

Done when the user named the format or confirmed it.

### 3. Build

- **Walkthrough**: in the chat, under these headings, dropping any that has nothing to say. **Overview**: what it is, what it does, and why it exists, in one or two paragraphs. **Key concepts**: the types, services, or ideas the rest needs, one line each. **How it works**: the flow from what starts it to what it produces, in prose that names the functions and files, with one diagram when parts talk to each other. **Where things live**: the files and folders someone would open first. **Gotchas**: what surprises, what history explains, and what the explorers could not settle. List the sources under it. The run ends here.
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
