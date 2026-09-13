---
name: resolving-merge-conflicts
description: "Use when you need to resolve an in-progress git merge or rebase conflict."
---

1. **See the current state** of the merge or rebase. Check git status, git history, and the conflicting files.

2. **Find the primary sources** for each conflict. Read the commit messages on both sides, and the Spec, ADRs, and `CONTEXT.md` that motivated them. A PR or issue is a source when one exists.

3. **Resolve each hunk.** Preserve both intents where possible. Where they cannot both stand, pick the one matching the merge's stated goal and note the trade-off. Do not invent new behaviour. Always resolve; never `--abort`.

4. Discover the project's **automated checks** and run them — typically typecheck, then tests, then format. Fix anything the merge broke.

5. **Finish the merge or rebase.** Stage everything and commit. If rebasing, continue until every commit is replayed.
