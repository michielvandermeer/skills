# A hunt files needs-triage Issues

A hunt run (`/hunt-codebase-improvements` or `/hunt-application-improvements`) files each finding as its own Issue in `needs-triage`, with no category label, and stops. It does not run `/triage`. You run `/triage` on those Issues when you want them sorted into Specs or parked statuses. Before filing, a hunt lists the open Issues and adds its evidence as a comment to one that already covers a finding.

A hunt runs unattended and can find dozens of problems at once. Sorting them is a judgement about what the repo should build, and that judgement belongs to the person who owns the repo, at the time they choose. A `needs-triage` list is also the inbox `/triage` already reads, so a hunt needs no ending of its own.

## Considered Options

- **A hunt runs `/triage` on its findings.** Rejected: one run would write many Specs and parks without anyone reading them, and a vague finding would land in `needs-grilling` or `needs-info` before its owner saw it.
- **A hunt sets the category and flags infrastructure fixes.** Rejected: a hunt cannot judge `bug` against `enhancement` or who builds a fix better than `/triage` does, which sets both when it runs.

## Consequences

- The `ready-for-human` override for infrastructure findings is gone from the hunts. `/triage` decides that status.
- A finding filed with no status label counts as `needs-triage` on every Tracker, so the Tracker templates need no change.
- Screenshots still reach each Issue through the Attach operation, as [ADR-0076](0076-screenshots-reach-an-issue-as-an-attach-comment.md) says.
