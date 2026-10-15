# Principles are files poteto-mode reads, not skills

pstack's 24 principles live at `skills/poteto-mode/principles/<title>.md`. Each was a skill of its own, hidden from the slash menu but model-invoked, so its description sat in every session's context on every turn: about 4,800 characters, close to 40% of all the skill descriptions this plugin keeps loaded. `poteto-mode`'s Principles index already says when each one applies, and the playbooks, `architect`, `arena`, and the other skills that cite a principle name it where it applies. So the descriptions bought a trigger nothing needed.

A file that cites a principle links to it by a path relative to itself, such as `../principles/prove-it-works.md` from a playbook. The path resolves inside the installed plugin, next to the skill that holds it, never inside the user's repo, so it does not have the wrong-file risk [ADR-0009](0009-technical-writing-for-output-not-source.md) weighs for a repo file.

## Considered Options

- **Keep them as skills with `disable-model-invocation: true`.** Rejected: a skill that neither the user nor the model can invoke is a file with a skill's frontmatter, and its folder still reads as a skill.
- **Keep the description, as a one-line index entry per principle.** Rejected: `poteto-mode`'s Principles index already is that line.

## Consequences

- A principle no longer loads on its own outside a poteto-mode session. A skill that wants one links to it.
- `tools/import_pstack.py` lands upstream's `skills/principle-<title>/SKILL.md` at `skills/poteto-mode/principles/<title>.md`, drops its frontmatter, and rewrites the links between principles, so a re-import keeps this layout ([ADR-0070](0070-pstack-is-imported-then-owned.md)).
