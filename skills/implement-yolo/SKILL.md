---
name: implement-yolo
description: "Build a Spec as a poteto-mode run on this checkout and this branch, with no worktree, no new branch, and no merge, folded into one commit here. Use only when the user or a /goal names /implement-yolo."
argument-hint: "Which Issue to implement, or what to build?"
model: opus
effort: high
---

This is `/implement` with the worktree waived ([ADR-0054](../../docs/adr/0054-the-implement-commands-differ-only-in-the-worktree.md), [ADR-0042](../../docs/adr/0042-implement-yolo-is-a-second-command.md)). Read [`../implement/SKILL.md`](../implement/SKILL.md) in full and run it from its step 0, with these three differences:

- Step 2 opens no worktree and takes [Worktree waived](../implement/LANDING.md#worktree-waived): the session stays at this checkout's git root, on its branch, and `<start>` (`git rev-parse HEAD` as the run begins) stands in for `<base>` for the whole run. Step 4 runs `open-todo.mjs` with `--landing in-place --start <start>`, so `todo.md`'s header says `Landing: in-place` and `Start: <start>`.
- Step 7's land is the fold that section describes: the Issue's close as a unit commit, `git reset --soft <start>`, then one commit with the landing commit's message. The push and `/retro` are unchanged, with `<base>` the branch you are on and this checkout the original directory.
- Benchmark mode does not apply ([ADR-0066](../../docs/adr/0066-a-benchmark-run-writes-nothing-outside-its-checkout.md)).

The claim, the route, the playbook, the gates, the halts, and the report are `/implement`'s as written.
