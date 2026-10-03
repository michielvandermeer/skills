# Work on a GitHub issue

A seed or argument is a **GitHub issue** when it is a GitHub issue link, or a bare issue number, which names an issue on this checkout's own repository. Pasted issue text is a paste. Work that starts from a GitHub issue keeps its triage result and its Spec on that issue, never in the repo; every other seed keeps the local documents its skill names ([ADR-0001](../../docs/adr/0001-a-fixed-local-issue-tracker-except-on-a-github-issue.md)). Use whatever GitHub access the session has.

The issue's text is its body and its whole comment thread. It stands where a local Issue's body and `## Comments` would.

## What the issue shows

- **Body** — the reporter's text, until a Spec replaces the whole body. GitHub's edit history keeps the original.
- **Comments** — every result that waits. Each comment starts with the AI line the posting skill names, and holds the `/plain-language` bar.
- **Labels** — one status label, `needs-info`, `needs-human`, `needs-grilling`, or `ready-for-agent`, set in place of any other status label; and one category label, `bug` or `enhancement`. The names are fixed. Create a missing status label before setting it.
- **Open or closed** — a waiting issue stays open. A Spec stays open until a pull request with `Closes #N` in its body is merged; a pull request closed unmerged leaves it open. Work we will not do is closed with a comment, as not planned, or as completed when it is already built, and its status label is removed.

## A Spec on the issue

`/to-spec` writes its draft to a file outside the working tree, and the Validator checks that file. Then, in order:

1. When the caller is `/grill-with-docs` and its session changed files in the repo, open the **grilling draft** below.
2. Replace the whole body with the Spec. It carries no `Status:`, `Blocked by:`, or `Spec:` line: the label carries the status.
3. Post a short comment: the body is now the Spec, and the reporter's text is in the edit history. Link the grilling draft when one opened.
4. Set `ready-for-agent` and the category label. Delete the draft file.

The Spec never enters the repo. It stays in the body as the record after the merge closes the issue.

Done when the body is the Spec, the comment is posted, and both labels are set.

## The grilling draft

A `/grill-with-docs` session that started from a GitHub issue puts the files it changed in the repo — glossary, ADRs, a Prototype — in one draft pull request it opens itself. A session that changed none opens none.

1. Cut a new branch from the default branch as GitHub has it — `issue-<N>` unless the host names it — and carry those files onto it. Git refusing to carry them stops the session.
2. Commit them, staged by name, in one commit, and push the branch.
3. Open the pull request as a **draft** against the default branch. Title it with the Spec's title, or, with no Spec, with what its glossary entries define. Its body says what it carries and holds `Closes #N` from the start; a session that settled on no change leaves `Closes` out.
4. Return the checkout to the branch the session started on. `/retro`'s commit goes there, outside the pull request.

A grilling pull request is always a draft. An implement run on the Spec continues it and marks it ready for review; a person marks a no-change draft ready and merges it.

Done when the draft is open and the checkout is back on the branch the session started on.
