# Green is measured against the base branch

**Green** is zero failures in the Footprint's projects, measured against the **base branch** ([ADR-0055](0055-a-run-lands-on-the-branch-it-started-from.md)): a failure that also fails on that branch at the merge-base is a Deviation the agent that meets it reports and finishes over, and it does not block landing; a failure that passes on the base branch stays red until fixed.

Treating a pre-existing failure as the Step's to fix was rejected: it is scope creep the Spec never asked for. Ignoring any failure the agent calls pre-existing was rejected: the claim has to be shown against the base branch, or it is just red.

## Consequences

- After a rebase onto a moved base branch, green is unknown again and is re-established before the fast-forward.
- The final report repeats every pre-existing failure the run carried.
