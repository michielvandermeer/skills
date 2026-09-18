# `/retro` writes only files this repository owns

`/retro` used to apply high-priority changes in this repository and in global agent files, including any file this session reached. That let a session in an app edit the installed `/implement` skill. `/retro` now applies those edits only to **Owned files**. A finding for a file this repository does not own stays in the summary, high-priority first and labelled, so you can apply it yourself.

Applying every file this session reached was rejected: the installed copy is a cache, not this repository. Dropping those findings was rejected: you still want the good suggestions. Opening the skills repository from here was rejected: this session does not write a second checkout.

## Consequences

- The global write in [ADR-0022](0022-retrospective-includes-global-agent-files.md) and [ADR-0038](0038-named-session-skills-apply-high-priority-retro.md) is superseded. Looking at those files stays.
- High-priority auto-apply for Owned files stays, in one repository commit.
