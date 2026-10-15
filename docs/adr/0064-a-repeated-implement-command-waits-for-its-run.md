# A repeated implement command waits for its run

When an implement command arrives again in the session already driving that run, and a delegate the session dispatched for the run has not reported yet, the run is still going. The repeat claims nothing, stashes nothing, and dispatches nothing. The session says the run is already going and keeps waiting for that report. A run is the same run when the argument gives the same slug.

On 2026-10-10, in `mvdmio-suite`, `/implement #294` arrived twice, 26 seconds apart, while the run's first delegate was still writing. The in-flight path of that day's skill said to reset the tree, which would have deleted the Spec copy and the delegate's uncommitted work; the session skipped the reset only by going against the skill. A builder, Verifier, or fixer still at work has uncommitted changes a reset would delete, and a resume would send a second delegate to the unit the first is still building.

The session knows which delegates it dispatched and which have reported, so it can tell a repeat from a resume without a lock or a file.

## Considered Options

- **Locking the run worktree to the session's own process.** Rejected: the in-flight check reads a lock that names a live process as another session's run. A run that halted would then not resume in the same session.
- **Leaving it to the session's judgement.** Rejected: a session that follows the resume path deletes or duplicates work.

## Consequences

- A repeat after a halt, or in a new session, still resumes: the session has no delegate waiting to report.
- `/implement` and `/implement-yolo` check for a repeat right after they derive the slug, before they claim the Issue or look for a run in flight.
- A resume stashes a dirty tree under a named stash and logs it, rather than resetting it away, so even a resume that misjudges a running delegate loses nothing.
