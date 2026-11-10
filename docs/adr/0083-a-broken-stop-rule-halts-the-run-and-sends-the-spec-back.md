# A broken Stop rule halts the run and sends the Spec back

A Spec may carry **Stop rules**: numbers the finished change must stay within for the Spec's premise to hold. The michielvandermeer/mvdmio-suite#1194 Spec said to stop if its run touched less than a third of the measured starting set. The run touched 1 of 9 tests in one app and 2 of 12 in another, then landed and reported the gap as a Deviation. So a Spec writes each Stop rule in a Stop Rules section of its own, the Verifier checks every one in each Verify, and a broken one halts the run at once, with no further Iteration. A broken Stop rule means the Spec described the code wrongly. That is a Spec to settle again, not code to fix, so the halt leaves no Halt record and writes nothing to the Tracker. The run's final report names the rule, the count it measured, and that the Issue needs a new grilling session. The branch and worktree stay, as with every halt.

## Considered Options

- **A Verify finding.** Rejected: a finding sends the run into another Iteration to fix it. For a rule that the change touched too little, the fix would be to touch more, which is exactly what the rule warns against.
- **The Implementer checks after each Step.** Rejected: a Step sees only its slice, and a Stop rule judges the whole change, as Review and Verify do.
- **The halt moves the Issue to `needs-grilling`.** Rejected: [ADR-0028](0028-implement-claims-its-issue-and-pushes-only-what-lands.md) limits a run's writes outside its working trees to the claim and the push of what lands.
- **A Halt record that makes a resume halt again before it builds.** Rejected: a resume with no Halt record already reaches Verify and stops on the same rule. Building the corrected Spec takes deleting the branch and worktree and running again ([ADR-0004](0004-the-run-folder-is-outside-the-tracker.md)), so a record would save one Verify on a run nobody should resume.
- **A Stop rule written anywhere in the Spec.** Rejected: the #1194 rule sat in one sentence of Implementation Decisions, where nothing looked for it.

## Consequences

- `/to-spec` writes the Stop rules the session settled into Stop Rules and leaves the section out when there are none. Each rule names what is counted, over what scope, the threshold, and the figure measured before the Spec.
- The Validator moves a stop instruction found outside Stop Rules into it, and reports a rule whose count or scope reads two ways, or that has no measured figure, as an open question.
- The Planning principle Explain the number asks for a Stop rule when a Spec relies on a count that only the finished change can confirm.
