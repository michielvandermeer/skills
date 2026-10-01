# Coding standards

## Branches

Skill and agent prose names a branch by its role in the run: the **Base branch**, the current branch, or a recorded SHA such as `<start>`. A literal name like `master` assumes the user is on it, and a run started elsewhere then lands somewhere the user did not choose ([ADR-0055](../../docs/adr/0055-a-run-lands-on-the-branch-it-started-from.md)).

## Run scratch

A file only agents read during a run — a Proof script, a screenshot, a transcript — is run scratch. The skill that writes it names where its run deletes it, and a halt keeps it for the resume. A file outlives the run only when a later session or skill reads it, and the prose names that reader. "So the user can look at it" names no reader: the Proof folder was kept on that reason and piled up in `.git` ([ADR-0053](../../docs/adr/0053-green-needs-a-proof.md)).
