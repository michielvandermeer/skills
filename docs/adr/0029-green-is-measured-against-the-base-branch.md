# Green is measured against the base branch

**Green** is zero failures in the Verifier's run of the whole test suite, measured against the **base branch** ([ADR-0055](0055-a-run-lands-on-the-branch-it-started-from.md)): a failure that also fails on that branch at the merge-base is a Deviation the Verifier reports and passes over, and it does not block landing; a failure that passes on the base branch stays red until fixed.

Treating a pre-existing failure as the run's to fix was rejected: it is scope creep the Spec never asked for. Ignoring any failure the agent calls pre-existing was rejected: the claim has to be shown against the base branch, or it is just red.

## Consequences

- A test that fails and then passes on the Verifier's one re-run is a flake: a Deviation too, so a flaky test cannot send the run into another Iteration.
- After a rebase onto a moved base branch, green is unknown again and a fresh Verifier re-establishes it before the fast-forward — unless every file the base branch gained is one no build, test, or Hand check reads, such as another run's Markdown or `.agents/` edits. Then green still holds, and the run names the commits it compared. Parallel runs land retro and doc commits all day, and re-running the whole suite over them found nothing while adding a full suite run to every land.
- The final report repeats every pre-existing failure the run carried.
