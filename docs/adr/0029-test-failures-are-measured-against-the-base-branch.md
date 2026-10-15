# Test failures are measured against the base branch

A test failure counts against an implement run only when the test passes on the **base branch** ([ADR-0055](0055-a-run-lands-on-the-branch-it-started-from.md)): a failure that also fails on that branch at the merge-base is a Deviation the agent that meets it reports and finishes over, and it does not block landing; a failure that passes on the base branch stays red until fixed. The projects measured are the ones the change touched, or the whole suite when the run ran it.

Treating a pre-existing failure as the run's to fix was rejected: it is scope creep the Spec never asked for. Ignoring any failure the agent calls pre-existing was rejected: the claim has to be shown against the base branch, or it is just red.

## Consequences

- After a rebase onto a moved base branch, the verification is unknown again and is re-established before the fast-forward, unless every file the base branch gained is one no build, test, or verification command reads, such as another run's Markdown or `.agents/` edits. Then the verification still holds, and the run names the commits it compared. Parallel runs land retro and doc commits all day, and re-running the whole suite over them found nothing while adding a full suite run to every land.
- The final report repeats every pre-existing failure the run carried.
