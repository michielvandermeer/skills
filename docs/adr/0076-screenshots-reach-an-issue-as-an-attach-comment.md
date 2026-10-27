# Screenshots reach an Issue as an Attach comment

A skill that has images for an Issue, such as the screenshots behind a `/simulate-first-users` finding, adds them through the Tracker ref's **Attach** operation: a comment that carries the images, never the Issue's body. `/to-spec` rewrites the whole body when it turns an Issue into a Spec, so an image in the body would be lost the first time the Issue is triaged. On GitHub, `gh issue comment --attach` uploads the images. A local Tracker commits them under `.agents/attachments/`, and Jira attaches them to the issue.

## Considered Options

- **Images in the Issue body.** Rejected: `/to-spec` rewrites the body and drops them.
- **Text only, with the screenshots left in a temporary folder.** Rejected: a person who picks the Issue up later cannot see the moment it describes, and for a First user's finding the screenshot is the evidence.
- **Committing the images to the repo on every Tracker.** Rejected: the images would stay in the repo's history for good, as [ADR-0060](0060-pr-is-model-invoked-so-every-description-carries-evidence.md) says of `/pr` screenshots. Only a local Tracker, whose Issues are repo files already, commits them.

## Consequences

- A Tracker ref copied before Attach existed has none, because later template changes never reach a copied ref. `/triage` then comments the image paths and its summary names each file for the user to add, as `/pr` does when it cannot attach. Copying the Attach line from the template into the ref fixes it.
- A local Tracker's Issue takes its attachments folder with it when it closes.
- `/simulate-first-users` keeps its scratch folder when the triage summary names images for the user to add, and deletes it otherwise.
