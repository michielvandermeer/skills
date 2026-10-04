# A retrospective looks at global agent files as well as the repo

A **Retrospective** looks at the host's global agent files (`AGENTS.md`, `CLAUDE.md`, and the same always-loaded files in the user scope) as well as the current repo. That holds for a named session skill's close and a typed `/retro`. Where `/retro` writes is [ADR-0040](0040-retro-writes-only-owned-files.md). It looks at files it does not write.

Looking at the repo only was rejected because the global files load on every session and are where steering often piles up. Looking at global files only when you type `/retro` was rejected because the named session skills are the sessions that always run one, and that is when the pain showed up.

Global scope is the always-loaded user files plus files this session actually reached. It does not inventory the whole user config tree. Each suggestion names its file by kind: an Owned file by its path in the tree, a plugin skill as `skills/<name>/...`, a user-global file by its host path. Host paths are looked up, not hardcoded.
