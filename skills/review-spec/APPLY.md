# Apply approved Spec edits

Parse the reply:

- `everything` / `all` / similar → every item
- `none` / `nothing` / similar → empty set
- numbers and ranges (`1,3,5`, `1-3`) → those items
- otherwise ask once more; a second unparseable reply is an empty set

Write the approved items in list order into the Spec file. The list text is what lands. Leave the write uncommitted.

Empty set → stop.

Any write → run `/validate-spec` on that Spec. Its report ends the run.

**Done** when the Spec on disk matches the approved set, and either `/validate-spec` has reported or nothing was written.
