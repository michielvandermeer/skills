# Session logs

Where each host keeps a repo's past sessions, for a skill that reads a **Window**. Read every host on this machine, not only this one. Look up where each keeps them; today:

- Claude Code keeps `~/.claude/projects/<cwd with / as ->/<session>.jsonl`. Skip `/subagents/`.
- Grok keeps `~/.grok/sessions/<url-encoded cwd>/<session>/`. Only a session whose `prompt_context.json` says `"audience": "primary"` is top-level.

A worktree's sessions belong to its repo.
