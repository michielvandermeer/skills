# Coding standards

## Branches

Skill and agent prose names a branch by its role in the run: the **Base branch**, the current branch, or a recorded SHA such as `<start>`. A literal name like `master` assumes the user is on it, and a run started elsewhere then lands somewhere the user did not choose ([ADR-0055](../../docs/adr/0055-a-run-lands-on-the-branch-it-started-from.md)).

A command that builds on the Base branch after a test run, a verification, or a dispatch names the SHA the run held when it last synced with that branch. Git reads a branch name when the command runs, and other sessions land in between. `cd5eeed` fixed `/implement`'s `commit-tree -p <base>`, which took a newer tip than the tree held and nearly undid another run's fix.

## Run scratch

A file only agents read during a run — a verification script, a screenshot, a transcript — is run scratch. The skill that writes it names where its run deletes it, and a halt keeps it for the resume. A file outlives the run only when a later session, skill, or person reads it, and the prose names that reader and what they read it for. "So the user can look at it" names no reader: an earlier evidence folder was kept on that reason and piled up. The Run directory outlives its run for the trail's reader, the person who reviews the run after stepping away, and a later run on the same slug replaces it.

Run scratch lives inside the run's working tree, in a folder whose own `.gitignore` holds `*`. A host that isolates a session in its worktree refuses writes outside it, the git common directory included. `b6cdf22` moved the run's evidence folder in from `<git common dir>/proof/`, where Claude Code refused delegates' writes in five repos.

## Coined terms

Before a skill edit coins a term, grep `skills/` and `CONTEXT.md` for it. A skill may already use the words in another sense that never reached the glossary: "context folder" meant the folder holding a `CONTEXT.md` in an implement reference file when a new path level nearly took the same name. A coined term gets its `CONTEXT.md` entry in the same commit.

## Sibling implement commands

`/implement` and `/implement-yolo` differ only in the worktree ([ADR-0054](../../docs/adr/0054-the-implement-commands-differ-only-in-the-worktree.md)), and `/implement-yolo`'s `SKILL.md` is a pointer that runs `/implement`'s file. A rule they share lives once, in `skills/implement/`; `/implement-yolo`'s file names only what the waived worktree changes. When three sibling bodies each held the flow, `c981138` taught two of them that a bare branch `<slug>` is a run in flight and left the third resetting over it.

`/hillclimb` copies `/implement`'s worktree entry, run scratch, and landing passages, the last from `skills/implement/LANDING.md`. An edit to one of those greps `skills/hillclimb/SKILL.md` too and changes its copy in the same commit, whether or not a Hillclimb has hit the problem yet. `b6cdf22` and `2a305be` fixed the scratch folder and the `cd … &&` advice in the implement commands only, and the user filed #21 to bring `/hillclimb` along.

## Moved passages

An edit that moves, merges, or deletes a passage lists each duty the old passage carried — a `/retro` call, a path level, a commit — and gives each one a home in the new text. `3e6a1f2` moved writing a map's Specs into a fresh session and left its `/retro` behind. `f245997` deleted the CONTEXT-PATHS row for Decision tickets and lost their context subfolder. An ADR rewrite keeps every exception the old text stated: `ad43b88` cut an ADR to "Snippets are banned" and lost the one place the old text let a snippet stand.

## Loading other skills

A skill's step never starts a user-invoked skill (`disable-model-invocation: true` in its frontmatter): no skill can reach one. The step tells the user to run it instead. `/diagnosing-bugs` once handed off to `/improve-codebase-architecture` this way, and the hand-off could never fire. The same goes for the implement commands, though they are model-invoked: their pin would swap the calling skill's model ([ADR-0067](../../docs/adr/0067-the-implement-commands-are-model-invoked-so-a-goal-can-start-them.md)).

## Hosts

Skill and agent prose names the agent to dispatch (`skills:explorer`, a sub-agent), never the host tool that dispatches it, such as Claude Code's Agent tool or a `subagent_type=` argument. The plugin also runs on Grok, where those names do not exist.

A command skill or agent prose hands an agent is **plain**: every argument spelled out, run from the working directory. A value such as a path from `git rev-parse` is resolved once and handed on as a literal path, never as a `$(…)` to paste into commands. Claude Code refuses other forms in a session it isolates in a worktree — a `cd` or `git -C` to another path, a shell variable, `$(…)`, a heredoc — and refused about 70 such commands across nine `/implement` runs before `2a305be`.

Prose that has an agent wait on work it started — a reviewer, a background build — names that work's own report or exit as what it waits on. Left to choose, an agent waits with a `sleep` or a watch that outlives the work and wakes it after it has reported: a per-unit review agent reported twice that way in mvdmio-suite #285, and `dc798c0` fixed it.
