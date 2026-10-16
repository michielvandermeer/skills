# A repeated implement command waits for its run

When an implement command arrives again in the session already driving that run, and a sub-agent the session dispatched for the run has not reported yet, the run is still going. The repeat claims nothing, resets nothing, and dispatches nothing. The session says the run is already going and keeps waiting for that report. A run is the same run when the argument gives the same slug.

On 2026-10-10, in `mvdmio-suite`, `/implement #294` arrived twice, 26 seconds apart. The second arrived while the first run's sub-agent was still at work. Step 1 found the run in flight and said to run `git reset --hard && git clean -fd`, which deletes whatever that agent has not committed yet. The session skipped the reset, but only by going against the skill. Under `/implement-yolo`, which never resets, the repeat would send a second Implementer to the work the first is still building.

The session knows which sub-agents it dispatched and which have reported, so it can tell a repeat from a resume without a lock or a file.

## Considered Options

- **Locking the run worktree to the session's own process.** Rejected: the in-flight check reads a lock that names a live process as another session's run. A run that halted would then not resume in the same session.
- **Relying on the committed Spec copy.** Rejected: it keeps the Spec safe, but not the uncommitted work of an agent still running.
- **Leaving it to the session's judgement.** Rejected: the skill says to reset, and a session that follows it deletes the work.

## Consequences

- A repeat after a halt, or in a new session, still resumes: the session has no sub-agent waiting to report.
- `/implement` and `/implement-yolo` both check for a repeat right after they derive the slug, before they claim the Issue or look for a run in flight.
