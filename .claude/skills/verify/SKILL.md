---
name: verify
description: Drive this checkout's skills the way a user does — load the working tree as the plugin in a headless Claude Code session inside a scratch repo, type the slash commands and answers, and capture what the skill did. Use to prove a skill or agent edit behaves before it is committed or pushed, or when asked to verify, try, or run a skill.
---

# Verify

The app here is the plugin: `skills/*/SKILL.md` and `agents/*.md`, loaded by Claude Code. The host runs the **installed** plugin, so an edit in this checkout reaches no session until it is pushed. `verify.py` closes that gap: every turn runs `claude -p` with `--plugin-dir` set to this working tree, uncommitted edits included, which replaces the installed `skills@mvdmio` for that one session. The user's own `~/.claude` (CLAUDE.md, other plugins, hooks) still loads — that is the real user path.

All commands run from the repo root. The helper is `python .claude/skills/verify/verify.py <command>`, Python 3 standard library only; `--help` on any command lists its flags.

## 1. Doctor

```
python .claude/skills/verify/verify.py doctor
```

Read-only, about a cent: `claude` logged in, the plugin manifests parse, every skill and agent frontmatter passes `.claude/hooks/check-frontmatter.mjs`, no scratch repo is left from an earlier run, and one Haiku session confirms this checkout is the only plugin named `skills`, with every agent and every user-invocable skill registered and no MCP server loaded. `--offline` skips the session. Run it first, and again whenever a turn looks wrong.

Done: the last line reads `doctor: ok`.

## 2. Launch a run

```
python .claude/skills/verify/verify.py new <run-name>
```

A run is one scratch repo plus one evidence folder plus one session. `new` makes a git repo with one commit and no remote at `%TEMP%/skills-verify-<stamp>-<run-name>`, and the evidence folder at `.claude/skills/verify/runs/<stamp>-<run-name>/`. It prints both.

- `--from-repo <path>` clones a local repo as the scratch instead, with its remote removed — for a skill that needs real code or history.
- `--plugin-dir <path>` puts another tree under test, such as a worktree of an older commit for a before-and-after.

Runs are isolated by their scratch repo and session id, so several can run side by side. Drive only a scratch repo `new` made: every turn runs with `bypassPermissions`.

Done: `new` printed the run and scratch paths.

## 3. Drive

```
python .claude/skills/verify/verify.py turn <run> "/skills:setup local"
python .claude/skills/verify/verify.py turn <run> "yes"
```

One `turn` is one user message. The first starts the session; each later one resumes it, so a skill that asks a question, shows a draft, or runs grilling rounds is driven by answering in the next turn. Answer as the user would — the question asked, nothing more — so the skill's own steps decide what happens. A skill that is model-invoked is reached by asking in plain words ("write the PR description for this branch") rather than by its slash name; the summary then shows it under `skills invoked by the model`.

Every turn prints a summary and the scratch repo's git state:

- `plugin: ok` — this tree was the one plugin named `skills`. Anything else fails the turn.
- `slash commands this session` and `skill bodies loaded from` — the skill that ran, and the folder its body came from. A folder outside this checkout fails the turn.
- `plugin files read this turn`, `agents dispatched this turn` (type, model, description), `denied tool calls`.
- The result line (cost, wall time, turns) and the final message.

Flags: `--model` sets the session model (default: the user's default; a skill whose frontmatter names `model:` runs on that one); `--effort`; `--budget` USD cap per turn (default 10); `--timeout` seconds (default 1800; the process tree is killed past it).

Each skill's recipe — preconditions, the turns to send, and the end state that proves it — is in the feature map, [features/README.md](features/README.md). Read the index before the first turn, then the matching feature file. A proof drives every entry point its feature file lists.

Done: the end state the feature file names is observed in the scratch repo or the transcript.

## 4. Evidence

Everything lands in the run folder and stays there:

| File | What it holds |
|---|---|
| `meta.json` | scratch path, plugin dir, plugin commit and whether it was dirty, session id |
| `turn-NN.prompt.txt`, `turn-NN.jsonl`, `turn-NN.stderr.log` | the message sent, the stream-json output, stderr |
| `turn-NN.summary.md` | the summary `turn` printed |
| `scratch-00-start.txt`, `scratch-NN.txt` | `git log --stat`, status, branches and worktrees before the run and after each turn |
| `transcripts/` | the session transcript and every subagent transcript |
| `scratch-final/`, `scratch-final.txt` | the scratch repo as cleanup found it |

A proof cites these files. Hold it to this bar:

- Exercise the skill through the slash command or plain request a user types — never by pasting the skill's body or calling its steps by hand.
- Show the action and the result: the turn's prompt, and the files, commits, branches, or Issue states it left — a final message saying "done" proves nothing on its own.
- Check every side effect the skill claims, with a read of the scratch repo, such as `git show` or the file's contents compared to the template it copied.
- Name the plugin commit from `meta.json`, and say when the tree was dirty.

## 5. Cleanup

```
python .claude/skills/verify/verify.py cleanup <run>
```

Copies the scratch repo into `scratch-final/`, deletes it, and deletes the run's session folder under `~/.claude/projects/` once its transcripts are copied. It refuses a path that is not a `skills-verify-*` folder in the temp directory. There are no long-lived processes; a turn's process tree ends with the turn or is killed at its timeout. Run cleanup after every run, failed ones included. `runs/` is git-ignored: the evidence stays local unless someone attaches it to a PR.

Done: `cleanup` printed `evidence kept`, and `doctor` reports no scratch repo left.
