---
name: document-changes
description: Write product-facing Changelog entries beside each CONTEXT.md. Use when /implement finishes before Spec delete and land, when backfilling Changelog history from git, or the user runs /document-changes with an optional context name and date window.
argument-hint: "[context] [from yyyy-mm-dd] [until yyyy-mm-dd]"
---

Write **Changelog** entries a product user can read. Run `/plain-language`, then hold a stricter bar: only words someone who uses the product already holds.

You are the **driving session**, or a `general-purpose` sub-agent at the session's own model and effort — product wording needs judgement.

## Entry shape

```markdown
## yyyy-mm-dd: <title at most six words>
<body: one paragraph, at most three sentences>
```

- **Ship date**: implement mode — the calendar day you write. Manual mode — author date of the last product-facing commit in the cluster.
- Prepend under `# Changelog` so the newest entry is always first. Same day: newer above older; within one batch, larger product changes first.
- Missing file: create `CHANGELOG.md` beside that context's `CONTEXT.md` with `# Changelog` then the entry. Only that title and `##` entries — no version sections.

## Contexts

- `CONTEXT-MAP.md` at the root → one Changelog per mapped context, beside that context's `CONTEXT.md`.
- Only a root `CONTEXT.md` → one Changelog beside it.
- Manual name filter matches the map's app name (e.g. `Compliance`), case-insensitive.

**Attribution.** Paths under an app root from the map → that context. Implement mode may also use the Spec and step **Footprints** when the diff is only under shared libraries. Manual library-only clusters: entry only when commit subjects clearly name one app; otherwise skip.

## Product-visible

An entry only for change a product user could notice — behaviour, screens, wording they see, workflows. Internal-only work (refactors, agent-doc cleanup, Spec/step chore drops, review-fix hardening of work already covered) produces no entry.

Nothing product-visible → tell the user none was needed and stop. `/implement` still lands.

## Dedup

Skip any candidate whose full heading line already exists — exact match on `## yyyy-mm-dd: title`. Only prepend; leave existing entries as they are.

## Modes

### Implement mode

`/implement` calls this after review/improve, while Spec and step **Outcomes** are still on disk, before delete and land. Branch diff vs the fixed point (usually `master`) is available.

1. Resolve affected contexts from branch-diff paths (and Spec/Footprints for library-only work).
2. For each affected context, draft **one** entry for the whole run from that context's product point of view. Prefer Spec problem/solution and Outcomes; use the diff only to confirm what landed.
3. Apply entry shape, product-visible filter, dedup.
4. Prepend survivors; create files as needed.
5. Commit on the current branch when any Changelog changed; otherwise no commit.

### Manual mode

User invoked. Optional filters: context name and/or `from` / `until` dates (inclusive). Defaults: every context in the map (or the single root context), full history.

1. Read commits in range (path-limited per context when a name filter is set).
2. Cluster into **logical product features** from subjects, bodies, and paths — not merge commits, not calendar-day buckets ([ADR-0012](../../docs/adr/0012-changelog-backfill-by-product-feature.md)). One cluster → one candidate. Keep product-visible clusters only.
3. Ship date = last product-facing commit author date in the cluster.
4. Draft, dedup, prepend **unattended**. Report per context: titles written, titles skipped as duplicate, clusters skipped as not product-visible.

## Done

Every qualifying candidate is prepended or skipped with a stated reason (duplicate / not product-visible). The user gets a short summary. Files on disk match that summary.
