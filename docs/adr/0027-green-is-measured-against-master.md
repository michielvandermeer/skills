# Green is measured against `master`

`/implement` required every Step to end green and said nothing about tests already red before the run. Step agents fixed unrelated failing tests and had the fix reverted at review, drivers landed with red suites on their own judgement, and one retry was spent on a failure the branch had not caused. **Green** is now zero failures in the Footprint's projects, measured against `master`: a failure that also fails on `master` at the merge-base is a Deviation the Step agent reports and finishes over, and it does not block landing; a failure that passes on `master` stays red until fixed.

Treating a pre-existing failure as the Step's to fix was rejected: it is scope creep the Spec never asked for. Ignoring any failure the agent calls pre-existing was rejected: the claim has to be shown against `master`, or it is just red.

## Consequences

- After a rebase onto a moved `master`, green is unknown again and is re-established before the fast-forward.
- The final report repeats every pre-existing failure the run carried.
