# pstack is imported, then owned

pstack comes into this plugin as a one-way copy of [pstack-claude](https://github.com/michael-denyer/pstack-claude) at one pinned commit, made by `tools/import_pstack.py`. Once imported, its files are this repo's to edit like any other, and nothing keeps them in step with upstream. Upstream changes arrive only when a maintainer reruns the import on purpose.

The import never undoes an edit. `tools/pstack-import-manifest.txt` records the git blob id of every file the import wrote, and a rerun stops before it overwrites or deletes a file whose content has changed since, naming each one. `--force` writes over them, for a deliberate re-import whose diff the maintainer reads to carry each edit forward. A file that this repo tracks and no import wrote is never written over, even with `--force`.

This repo owns some files outright, and the import never writes them: `hooks/hooks.json`, `hooks/session-start.sh`, `hooks/session-start-context.md`, `skills/setup/MODELS.md`, `skills/setup/scripts/read-sheet.sh`, `skills/poteto-help/SKILL.md`, `skills/technical-writing/SKILL.md`, `skills/fix-merge-conflicts/SKILL.md`, `skills/poteto-mode/playbooks/bug-fix.md`, `skills/thermo-nuclear-review/SKILL.md`, `agents/thermo-nuclear-review-subagent.md`, `agents/thermo-nuclear-code-quality-review-subagent.md`, `skills/retro/scripts/find-transcript.mjs`, `skills/technical-writing/SLOP-PATTERNS.md`, `skills/poteto-mode/playbooks/figure-it-out.md`, and `NOTICE.md`. Each began as upstream's file. Upstream's `setup-pstack` skill became the Models part of `/setup`, `/technical-writing` became the standard for every sentence a person reads ([ADR-0009](0009-technical-writing-for-output-not-source.md)), `/fix-merge-conflicts` took over from this repo's own merge-conflict skill and finishes the merge or rebase it starts, the Bug fix playbook took in this repo's own debugging skill, `/thermo-nuclear-review` runs both thermos passes itself with each rubric in its agent, `reflect`'s transcript finder moved to `/retro` when `reflect` was dropped, `unslop`'s pattern catalog became part of `/technical-writing`, and `figure-it-out` became a poteto-mode playbook. The `OWNED` map in the import, from each upstream path to where this repo keeps the file, is the source for all but `NOTICE.md`, which the import never had.

## Considered Options

- **Depending on the separate pstack plugin.** Rejected: its skills register as `pstack:`, so this plugin's skills would dispatch into another plugin, and the operator could not change them.
- **A re-import that overwrites edits.** Rejected: it undoes the edits that make pstack this repo's own.
- **Import rules that rewrite even the mostly rewritten files.** Rejected: a rule set that rewrites most of a file is a second copy of it, and it breaks on every upstream change to that file.
- **Merging upstream as a git subtree.** Rejected: upstream ships Codex, GitHub Copilot, and Pi files this plugin leaves out, and each merge would bring them back.

## Consequences

- An edit to an imported file is an ordinary commit. After the next re-import with `--force`, the maintainer re-applies the edits that still hold.
- To own another file, add it to `OWNED`. The next run stops listing it in the manifest and leaves the file in place.
- The manifest holds git blob ids, not hashes of the bytes on disk, so a Windows checkout with CRLF line endings does not count as an edit.
- `NOTICE-pstack.md` is the import's own output, and `NOTICE.md` points at it.
