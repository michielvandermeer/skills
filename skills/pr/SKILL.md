---
name: pr
description: Pull request descriptions. Use when writing the description of a pull request or merge request.
---

# Pull request description

A description shows a reviewer what changed, that it works, and how risky it is to merge, in three sections, in this order:

```markdown
## What changes

<the smallest picture that makes the change clear, with the sentence it supports>

## Evidence

<the one fact the change is safe because of, naming what breaks if it is false>

**Before:** <output, screenshot, or one sentence>
**After:** <output or screenshot>

## Merge risk

**Undo:** <easy — reverting the commits restores the old behaviour | hard — what stays changed after a revert>
**Affects:** <who or what would notice if it went wrong>

<the Issue's closing reference>
```

Its reader is a reviewer who was never in the session. Write it at the bar the `/plain-language` skill sets: the repo's `CONTEXT.md` terms stand as they are, and this plugin's own words — Safety fact, Proof, rung, Step — stay out. When the work came from an Issue, end with the closing reference the repo's Tracker ref (`.agents/refs/tracker.md`) gives; a ref that gives none gets the Issue's reference on its own line.

Write the description to a file outside the repo and pass it with `--body-file` to `gh pr create` or `gh pr edit`, or the host's equivalent.

## What changes

Pick the smallest view that makes the point. One is usual and several is fine:

- Logic or an algorithm: pseudocode.
- Runtime control flow: a call tree.
- UI structure: a component tree, with the state and module boundaries that matter.
- File responsibility or a broad refactor: a shallow file tree, one comment per folder.
- Interaction or data flow between parts: a Mermaid sequence diagram.
- A change inside a shape that already exists: a `diff` of that shape — component tree, file tree, call tree, or control flow — rather than of the code:

  ```diff
   submitForm
     createSession
       persistPrompt
  +    expandSkillMention
       launchAgent
  ```

- Code that is mostly new, or whose order matters: the whole block.

Keep only the calls, files, props, and states the point needs, and put each picture next to the sentence it supports.

## Evidence

Open with the one fact the change is safe because of, naming what breaks if it is false. Then show the check that proves it:

- **After**: output from a run on the exact code being pushed. When the code changed since the check last ran, run it again.
- **Before**: the same check on the target branch, in a throwaway worktree, when it can fail there. Otherwise one sentence on what happened before.

A visual change shows a screenshot, or a short recording when the change is an interaction, taken by driving the app the way the repo's Run recipe says when it has one. Save it outside the repo, reference it in the description by that path, and upload it with `--attach '<path>#<alt text>'`, which swaps the path for the uploaded link (`gh` 2.99 and later, on GitHub.com). Where the host's tool cannot attach — GitHub Enterprise Server, GitLab, an older `gh` — leave `<!-- add <path> here -->` in its place and tell the user which file to add.

A change to no code that runs, such as a docs edit, says in one line that it needs no evidence. A check you could not run is named with the reason, in place of its output: every line of output in the description comes from a run you saw.

After an implement run in this session, its final report gives each Step's fact, check, and merge risk. Use them: the Prover re-ran every check on the code that landed, so the after half comes from the report unless the code changed since.

## Merge risk

**Undo** is easy when reverting the commits restores the old behaviour, and hard when something stays changed after the revert — data written, a migration run, a file format or API others already read, a release published. A hard Undo names what stays changed.

**Affects** names who or what would notice if the change went wrong: the users of a screen, the callers of an API, a nightly job, the layout on a phone.

After an implement run, the description's Undo is the hardest among its Steps, and its Affects covers every Step's.
