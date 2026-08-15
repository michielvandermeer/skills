---
name: prototype
description: Build a throwaway prototype to answer a design question, then turn the answer into a Spec. Use when the user wants to sanity-check whether a state model or logic feels right, or explore what a UI should look like.
---

# Prototype

A prototype is **throwaway code that answers a question**. The question decides the shape.

It is built in a worktree and played with. The lasting record is `.agents/prototypes/<slug>/` — the Spec points at that folder. The worktree and its branch go.

## Process

### 1. Pick a branch

Identify which question is being answered — from the user's prompt, the surrounding code, or by asking if the user is around:

- **"Does this logic / state model feel right?"** → [LOGIC.md](LOGIC.md). Build a single shareable HTML file — free-play buttons plus tabbed guided walkthroughs — that pushes the state machine through cases that are hard to reason about on paper, and that a non-developer can drive.
- **"What should this look like?"** → [UI.md](UI.md). Generate several radically different UI variations on a single route, switchable via a URL search param and a floating bottom bar.

The two branches produce very different artifacts — getting this wrong wastes the whole prototype. If the question is genuinely ambiguous and the user isn't reachable, default to whichever branch better matches the surrounding code (a backend module → logic; a page or component → UI) and state the assumption at the top of the prototype.

### 2. Enter the worktree

Derive `<slug>`: a kebab-case slug of the question being prototyped. Check the cases in order, because they decide where you build:

- **This session is already in a worktree** → build there. The session serves a larger effort, and [Serving a larger effort](#serving-a-larger-effort) governs its ending.
- **A `prototype/<slug>` branch exists** → an earlier run handed the prototype over and stopped before its verdict. Find its worktree with `git worktree list` (or the host's equivalent), put the session's working directory there, and resume at step 4. Leave that tree exactly as it stands: a reset or a clean destroys the prototype you came back for.
- **Fresh** → open a worktree on branch `prototype/<slug>` and put the session's working directory inside it:
  - If this host has a tool that **creates the worktree and moves the session into it**, use that tool — even when its path is not the fallback below. Record the branch name it chose when that name is not `prototype/<slug>`.
  - Otherwise ensure the consuming repo ignores `.agents/worktrees/` (add the line if missing; prefer a local ignore when the repo uses one), then `git worktree add` at `.agents/worktrees/prototype/<slug>` on branch `prototype/<slug>`, and change the session's working directory there.

The session must work *inside* the worktree for the rest of the run — creating a worktree alone is not enough. A fresh worktree carries no installed dependencies, so a UI prototype installs the project's before it can start — rule 2 promises the user one command. A prompt that explicitly waives the worktree takes [Worktree waived](#worktree-waived) instead.

### 3. Build it

Follow the branch file picked in step 1, holding the [rules that apply to both](#rules-that-apply-to-both).

### 4. Hand it over and wait for the verdict

Send the file, or surface the URL and its variant keys. Then wait. The interesting moments are "wait, that shouldn't be possible" and "huh, I assumed X would be different" — those are the bugs in the *idea*, which is the whole point. If the user wants another action, scenario, or variant, add it; prototypes evolve.

When the user is not reachable, **end early**: commit the prototype on its branch, say where it is and that no verdict is in yet, and stop. The worktree and the branch stay exactly as they are. Re-invoking `/prototype` for the same question picks the run back up here.

### 5. End in a Spec

The verdict decides what the Spec will say; the folder is the playable record the Spec points at. `<branch>` is `prototype/<slug>`, or the name recorded in step 2 when a host tool chose another.

1. Write `.agents/prototypes/<slug>/` on the original checkout: a logic demo already in that folder in the worktree copies as the folder; a UI prototype copies its in-app prototype files (variants, switcher, throwaway route) into it.
2. Return the session to the original checkout — a host leave-worktree action when it does exactly that, otherwise change directory yourself.
3. Run `/to-spec` there. The Spec names **the question the prototype was built to answer**, **what playing with it settled**, and **`.agents/prototypes/<slug>/`**.
4. Remove the worktree and delete the branch: `git worktree remove --force <path>`, then `git branch -D <branch>`.

A verdict that kills the idea ends with no Spec and no folder. Report what was learned, remove the worktree and branch the same way, and write an ADR only when the decision passes the three-part test in `/domain-modeling`.

The Spec is the handover. Real code gets built from it later, by `/implement`.

## Rules that apply to both

1. **Throwaway from day one, and clearly marked as such.** A logic demo is written in the folder. A UI prototype mounts in the app next to the page it's prototyping so context is obvious — name those files so a casual reader can see they're a prototype, not production. For throwaway UI routes, obey whatever routing convention the project already uses.
2. **Trivial to run.** A UI prototype starts from one command in the project's task runner — `pnpm <name>`, `python <path>`, `bun <path>`, etc. A logic demo is a single HTML file the user double-clicks. Either way, no thinking required to start it.
3. **No persistence by default.** State lives in memory. Persistence is the thing the prototype is _checking_, not something it should depend on. If the question explicitly involves a database, hit a scratch DB or a local file with a clear "PROTOTYPE — wipe me" name.
4. **Skip the polish.** No tests, no error handling beyond what makes the prototype _runnable_, no abstractions. The point is to learn something fast.
5. **Surface the state.** After every action (logic) or on every variant switch (UI), print or render the full relevant state so the user can see what changed.

## Serving a larger effort

A `/wayfinder` prototype ticket, or a `/grilling` session reaching for a demo mid-design, invokes `/prototype` from a session that is already in a worktree. That session hands over, writes the folder in this tree, and stops: the verdict and the path go back to the effort, whose own Spec names both. Leave the worktree and its branch to the effort that opened them.

## Worktree waived

The prototype files sit in the checkout. Step 2 builds there. Step 5 writes the folder in this checkout (no copy from a worktree) and removes in-app prototype files that are not the folder.
