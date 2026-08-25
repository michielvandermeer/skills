---
status: superseded by ADR-0022
---

# A retrospective looks at global agent files as well as the repo

A **Retrospective** proposes changes to the host's global agent files (`AGENTS.md`, `CLAUDE.md`, and the same always-loaded files in the user scope) as well as the current repo. That holds for a named session skill's close and a typed `/retrospective`.

Looking at the repo only was rejected because the global files load on every session and are where steering often piles up. Looking at global files only when you type `/retrospective` was rejected because the named session skills are the sessions that always run one, and that is when the pain showed up.

Global scope is the always-loaded user files plus files this session actually reached. It does not inventory the whole user config tree. Each suggestion states whether it is repo or global, and gives the path. Host paths are looked up, not hardcoded.
