# `/retro` writes only files this repository owns

`/retro` applies high-priority edits only to **Owned files**. A finding for a file this repository does not own stays in the summary, high-priority first and labelled, so you can apply it yourself. A session in an app would otherwise edit the installed `/implement` skill, which is a cache of another repository. Looking at global agent files stays ([ADR-0022](0022-retrospective-includes-global-agent-files.md)).

Applying every file this session reached was rejected: the installed copy is a cache, not this repository. Dropping those findings was rejected: you still want the good suggestions. Opening the skills repository from here was rejected: this session does not write a second checkout.

## Consequences

- High-priority auto-apply for Owned files stays, in one repository commit.
