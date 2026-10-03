---
name: triage
description: Sort incoming reports into Specs and parked Issues — one document per distinct problem, kept on the GitHub issue when the report is one.
disable-model-invocation: true
---

# Triage

Sort a **seed** of reports into Specs and parked Issues. One distinct problem → one document. Apply each result in this run; the closing **summary** is the review.

## Seed

The seed is what the maintainer handed this session: a pasted email, a markdown file, a description, ticket text, a path to an existing local Issue, or a GitHub issue.

1. If the invocation has no seed, ask for one. Stop until it arrives.
2. If they named a path under `.agents/issues/<slug>/<NN>-<slug>.md`, that Issue is the file this problem updates. Any other file is seed text — new work.
3. A GitHub issue link or bare number is a **GitHub issue**, and its problems end on GitHub: read [GITHUB-ISSUE.md](GITHUB-ISSUE.md) now. Check that this session can write to that repository's issues; without it, stop and say so. An issue already labelled `ready-for-agent` holds a Spec: leave it unchanged and report that in the summary.
4. A paste is new work, pasted GitHub issue text included. Leave leftover files from old runs as they are.

Done: the seed text is in context.

## Split

Two findings are **distinct** when one can be resolved without the other. A list of items is the starting set. Split an item that contains more than one distinct problem. Queue extras found while investigating into this same run.

Done: every distinct problem is named. More may join during investigate; each joins this list.

## Per problem

For each distinct problem, gather → verify → apply. When the seed is an existing Issue being split, write extras first, then rewrite or delete the original as the first problem's ending. A GitHub issue splits the same way on GitHub: each extra is a new GitHub issue whose body holds only that problem and links back to the original, and the original's ending comment links each new one.

### Gather

Read the seed text for this problem. If this updates an existing Issue, read the body and `## Comments` — on a GitHub issue, the body and the whole thread — and ask only what is still open. Explore the codebase using the project's domain glossary, respecting ADRs in the area.

Search for an existing implementation of the requested behaviour by domain concept (not just the request's wording). Record where you looked. Found → skip verify, apply **not filed**.

Done: the problem is already implemented, or you have enough of the code to verify and classify.

### Verify

For a bug, reproduce it from the reporter's steps. Outcome: confirmed (with code path), failed, or insufficient detail (`needs-info`). Confirmed verification strengthens the Spec.

Done: a verify outcome is recorded.

### Apply

Trust an explicit override in the seed (`spec this`, or the old "move … to ready-for-agent" → Spec; `needs-info`, `needs-human`, `needs-grilling` → that park). Pick exactly one ending and write it. Category on any Issue is `bug` or `enhancement`, as `Category:` near the top with `Status:`.

On a GitHub issue an ending writes nothing to the repo: it goes on the issue as [GITHUB-ISSUE.md](GITHUB-ISSUE.md) lays out, with the status label it names and a category label. `needs-info` posts its Triage Notes, and `needs-human` and `needs-grilling` their short comment, as an issue comment.

Issues live at `.agents/issues/<feature-slug>/<NN>-<slug>.md`, numbered from `01` among `NN-*.md` in that directory (`map.md` is not numbered). Same feature → that directory, next number. Different feature → new directory. An existing Issue being split keeps its path; extras are new files whose body is only the extracted problem.

In a repo with a `CONTEXT-MAP.md`, every `.agents/<kind>/` path in this skill gains a context subfolder — follow [domain-modeling/CONTEXT-PATHS.md](../domain-modeling/CONTEXT-PATHS.md).

**Spec** — buildable and the solution is clear. Run `/to-spec` scoped to this problem alone; on a GitHub issue it writes the Spec into the issue body. Delete the issue file if one exists for this problem. Agent-ready work is a Spec with `Status: ready-for-agent`.

**needs-info** — not enough information. Park. Write or update the Issue. Append:

```markdown
## Triage Notes

**What we've established so far:**

- point 1

**What we still need from you (@reporter):**

- question 1
```

Questions are specific and actionable.

**needs-human** — a person is needed for secrets, manual testing, or work the maintainer will do. Park. Write or update the Issue. Short comment: why this status, what is known, what is blocked.

**needs-grilling** — a human must decide the solution in a later `/grill-with-docs` session. Park. Write or update the Issue. Short comment: why this status, what is known, what is blocked.

**Not filed** — rejected or already implemented. Delete the issue file if one exists for this problem. Mention only in the summary. A GitHub issue is closed with a comment saying why: as not planned, or as completed when it is already built.

Every comment starts with:

```
> *This was generated by AI during triage.*
```

Run `/plain-language` before any comment a reporter will read.

Done: every named problem has exactly one ending, on disk or on its GitHub issue, or is not filed, and extras found during investigate have been named and run through this section.

## Summary

End with a summary the people in the session can follow up from. For every problem: what it was, and either the path plus `Status:` of the Spec or Issue, the GitHub issue's link and status label, or that it was not filed and why. The summary is the review.

Done: the summary lists every problem this run handled. Then run `/retro`; its commit stays on the current branch.
