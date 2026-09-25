# 01 — Retro turns Corrections into Coding standards rules

Status: done

## What to build

After this step, a **Retrospective** reads the code its session changed, finds **Corrections** in that diff, and writes the rule a Correction points to into the repo's **Coding standards** as a **High-priority** edit applied without asking. Only `skills/retro/SKILL.md` changes; the glossary entries (**Correction**, **High-priority**, **Coding standards**) and [ADR-0050](../../../docs/adr/0050-retro-learns-from-corrections.md) already exist.

The edits the Spec names, all in `skills/retro/SKILL.md`:

- **Opening line.** Narrow "`/code-review` and `/improve-data-structures` own the product diff": they still review the diff; `/retro` reads it only to find Corrections.
- **Sources.** Add the session's code changes: the commits the session log records, plus any uncommitted changes in the working tree. Same for the current and a named session. It must not depend on a branch or a recorded start commit — `/implement` deletes its branch before `/retro` runs.
- **The Correction test**, following the glossary entry:
  - Old code = lines the session's diff removed or changed that were committed before the session's first commit; `git blame` shows which commit wrote each line.
  - The session also shows the old code was wrong: the user said so, a bug was being fixed, a test failed, or a review flagged it.
  - Code written earlier in the same session is not a Correction (the existing "reviewer missed a mistake" bar covers what the reviewer let through). A change that follows a changed requirement is not a Correction. Who wrote the old code does not matter.
- **When a Correction becomes a rule.** Only when the fix points to a pattern future code could repeat. No rule for a one-off fact (such as a wrong constant); no rule when a check could catch it (Automated checks applies); no rule when the Coding standards already hold it (the reviewer-missed bar applies). When a Correction contradicts a rule already written, change or remove that rule instead of adding a second.
- **Coding standards category.** Add the Correction as a second *Use when* bar beside "the reviewer missed a mistake".
- **Where the rule goes.** The repo's existing Coding standards — `.agents/refs/` first, then a root `CODING_STANDARDS.md` or `CONTRIBUTING.md`. None exists → create `.agents/refs/coding-standards.md`. A Correction in a file the repo does not own still writes its rule here.
- **Apply.** The rule a Correction points to joins the **High-priority** list: applied without asking, only to **Owned files**, in the single retrospective commit, as the smallest change that encodes what the session showed, and listed under applied items in the summary with its path.

Reading filled from the walk, where the Spec is silent: when `.agents/refs/` holds several files, the rule goes into the one that already holds Coding standards; the new file is created only when the repo keeps no Coding standards in any of the named places.

Keep the skill in the house style of `skills/writing-for-agents/SKILL.md`, use `CONTEXT.md` terms exactly, and run `/writing-for-agents` on the edited file, as `AGENTS.md` requires.

## Footprint

Projects: none

- `skills/retro/SKILL.md` — opening paragraph, `## Sources`, `## Categories` (Coding standards bullet), `## Apply`, `## Present`
- `CONTEXT.md` — **Correction**, **High-priority**, **Coding standards**, **Owned file** entries (read for terms; edit only if the skill coins a new term)
- `docs/adr/0050-retro-learns-from-corrections.md` — the decision the skill text must match (read only)

## Acceptance criteria

- [ ] The opening line no longer says the product diff belongs solely to `/code-review` and `/improve-data-structures`; it says `/retro` reads the diff only to find Corrections.
- [ ] `## Sources` includes the session's code changes from the commits the session log records plus uncommitted working-tree changes, for both the current and a named session, with no reliance on a branch or start commit.
- [ ] The skill defines old code via lines committed before the session's first commit (with `git blame` named) and requires proof in the session that the old code was wrong (user said so, bug fix, failing test, or review finding).
- [ ] Same-session code and changes following a changed requirement are excluded; authorship (person or agent) is stated not to matter.
- [ ] A Correction yields a rule only for a repeatable pattern; one-off facts, check-catchable mistakes, and rules already present yield none; a contradicted existing rule is changed or removed rather than duplicated.
- [ ] The Coding standards category carries the Correction as a second *Use when* bar next to "the reviewer missed a mistake".
- [ ] The rule's location order is `.agents/refs/`, then root `CODING_STANDARDS.md` or `CONTRIBUTING.md`, else a new `.agents/refs/coding-standards.md`; a Correction in a non-owned file still writes its rule to the repo's own Coding standards.
- [ ] The Correction rule is listed as **High-priority** in `## Apply`: applied without asking to Owned files, in the one retrospective commit, smallest change, and shown under applied items with its path.
- [ ] Behaviour check: tracing a session that fixed old code after the user said it was wrong through the skill text leads to a Coding standards rule; tracing one that changed old code for a new requirement leads to nothing.
- [ ] No file other than `skills/retro/SKILL.md` changes (unless `CONTEXT.md` needs a newly coined term), and `/writing-for-agents` has been run on the edited skill.

## Outcome

`skills/retro/SKILL.md` now reads the session's code changes and turns Corrections into Coding standards rules, per the checklist above. Changes:

- Opening line narrowed: `/code-review` and `/improve-data-structures` still review the product diff; `/retro` reads it only to find Corrections.
- `## Sources` gained the session's code changes (commits the session log records, plus uncommitted working-tree changes), with an explicit note that this does not depend on a branch or a recorded start commit.
- A new `### Finding Corrections` subsection under `## Sources` defines old code (lines predating the session's first commit, per `git blame`), the proof bar for "the old code was wrong", the same-session and changed-requirement exclusions, authorship not mattering, the repeatable-pattern bar for writing a rule (excluding one-off facts, check-catchable mistakes, and already-held rules), and the change-or-remove rule for a contradicted existing rule.
- `## Categories`' Coding standards bullet gained the Correction as a second *Use when* bar.
- `## Apply`'s High-priority paragraph now names the Correction rule, and a new paragraph gives the location order (`.agents/refs/` holder first, then root `CODING_STANDARDS.md`/`CONTRIBUTING.md`, else create `.agents/refs/coding-standards.md`), including for a Correction in a non-owned file.
- `## Present` already covered applied items generically (path in this tree, concrete enough to undo), so no change was needed there for the Correction rule.

No new term was coined, so `CONTEXT.md` was not edited. No project has tests (`Projects: none`); verification was the read-through against each acceptance criterion above, plus a `/writing-for-agents` self-review pass that tightened two sentences for redundancy (git blame phrasing; the Coding standards location sentence).

No deviations from the Spec or Step file.
