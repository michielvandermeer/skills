# Coding standards

## Branches

Skill and agent prose names a branch by its role in the run: the **Base branch**, the current branch, or a recorded SHA such as `<start>`. A literal name like `master` assumes the user is on it, and a run started elsewhere then lands somewhere the user did not choose ([ADR-0055](../../docs/adr/0055-a-run-lands-on-the-branch-it-started-from.md)).

## Run scratch

A file only agents read during a run — a Proof script, a screenshot, a transcript — is run scratch. The skill that writes it names where its run deletes it, and a halt keeps it for the resume. A file outlives the run only when a later session or skill reads it, and the prose names that reader. "So the user can look at it" names no reader: the Proof folder was kept on that reason and piled up ([ADR-0053](../../docs/adr/0053-green-needs-a-proof.md)).

Run scratch lives inside the run's working tree, in a folder whose own `.gitignore` holds `*`. A host that isolates a session in its worktree refuses writes outside it, the git common directory included. `b6cdf22` moved the Proof folder in from `<git common dir>/proof/`, where Claude Code refused Step agents' and Checkers' writes in five repos.

## Coined terms

Before a skill edit coins a term, grep `skills/` and `CONTEXT.md` for it. A skill may already use the words in another sense that never reached the glossary: "context folder" meant the folder holding a `CONTEXT.md` in `skills/implement/PROOF.md` when a new path level nearly took the same name. A coined term gets its `CONTEXT.md` entry in the same commit.

## Sibling implement commands

`/implement`, `/implement-oneshot`, and `/implement-yolo` differ only in planning and worktree ([ADR-0054](../../docs/adr/0054-the-implement-commands-differ-only-in-planning-and-worktree.md)). An edit to a rule they share — in-flight detection, resume, land, cleanup — greps the other two `SKILL.md` files for the same passage and changes each one in the same commit. `c981138` taught oneshot and yolo that a bare branch `<slug>` is a run in flight and left `/implement` resetting over it.

## Moved passages

An edit that moves, merges, or deletes a passage lists each duty the old passage carried — a `/retro` call, a path level, a commit — and gives each one a home in the new text. `3e6a1f2` moved writing a map's Specs into a fresh session and left its `/retro` behind. `f245997` deleted the CONTEXT-PATHS row for Decision tickets and lost their context subfolder. An ADR rewrite keeps every exception the old text stated: `ad43b88` cut ADR-0010 to "Snippets are banned" and lost the snippet that `## What to build` may hold.

## Loading other skills

A skill's step never starts a user-invoked skill (`disable-model-invocation: true` in its frontmatter): no skill can reach one. The step tells the user to run it instead. `/diagnosing-bugs` once handed off to `/improve-codebase-architecture` this way, and the hand-off could never fire.

## Hosts

Skill and agent prose names the agent to dispatch (`skills:explorer`, a sub-agent), never the host tool that dispatches it, such as Claude Code's Agent tool or a `subagent_type=` argument. The plugin also runs on Grok, where those names do not exist.

A command skill or agent prose hands an agent is **plain**: every argument spelled out, run from the working directory. A value such as a path from `git rev-parse` is resolved once and handed on as a literal path, never as a `$(…)` to paste into commands. Claude Code refuses other forms in a session it isolates in a worktree — a `cd` or `git -C` to another path, a shell variable, `$(…)`, a heredoc — and refused about 70 such commands across nine `/implement` runs before `2a305be`.
