# Verify skill upkeep

A feature map goes stale as the app changes. The pass covers every feature twice: from the source, and live.

This is `/setup verify` on a repo that already has its Verify skill, as [VERIFY.md](VERIFY.md) describes. Edit only the Verify skill's own folder: its `SKILL.md`, `features/`, and the scripts it ships. Behaviour the map describes that the app no longer has is either drift, which the map fixes, or a broken app, which goes to the user and stays out of the map.

1. **Index.** Read `features/README.md` and list the folder. Fix entries that are missing, extra, duplicated, or dead.
2. **Read the source.** Dispatch one `skills:explorer` per feature file, all in one message. Each explains how its feature works from the source, cites any drift between the source and the file, and returns one recipe to check it live.
3. **Reconcile.** Merge recipes that need the same app state. Open each cited drift to confirm it. Look through recent commits for a user-facing feature the map lacks, and call it missing only with the source path that adds it.
4. **Drive.** Run every feature live at least once, even when the source looked clean, following the skill's own Launch section. Through the whole pass:
   - Run the doctor before the first drive, on every fresh session, and after any failed drive. When the doctor cannot see what went wrong, such as a stuck screen on a healthy process, reset the state or relaunch.
   - Check that the evidence captured so far is still where the skill says, after every cleanup.
   - Clean up what each drive started once it is no longer needed, including after a failure.
   A doctor that fails because the skill drifted gets fixed and retried once, then the pass is blocked. A feature counts as unreachable only with the prerequisite it needs and the route tried, such as a paid account or another operating system. A prerequisite the map leaves out is drift.
5. **Sort the failures.** A wrong or missing description is drift: fix it. Working behaviour the harness cannot drive is a harness gap: fix it, and drive the fix live before it counts. Behaviour that is broken in the app is a product bug: list it for the user, with a suggestion to take it to `/triage`.
6. **Finish.** End the pass in one outcome, and say which:
   - **clean**: every feature covered from the source and live, nothing to fix, no commit.
   - **changed**: one commit of corrections, each proven by a drive, staged by name, every changed file read again first.
   - **blocked**: what stopped the pass, and the coverage reached before it.

Done: the outcome is reported with the features covered, the unreachable ones with their prerequisites, the drift fixed, and the product bugs found.
