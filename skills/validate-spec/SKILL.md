---
name: validate-spec
description: Validate a plan, spec, or the current conversation against this repo's own template rules and the current codebase — fix stale references and contradictions in place, flag real decisions as open questions.
---

# Validate Spec

Validate a plan, spec, idea doc, or conversation against the checklist below. A **fact** — a stale reference, a broken link, a contradiction resolvable by rereading the doc or the code — gets corrected in place. A **decision** — anything that would change scope, or trades one valid design against another — gets flagged as a question instead, the same fact/decision split `/grilling` uses.

## Process

### 1. Pin the target

A path or slug the user names; otherwise the plan/idea already under discussion; otherwise the most recently touched file under `.agents/plans/` or `.agents/ideas/`. Ask if none of these resolve.

Note the doc's type — an **idea** (`.agents/ideas/`) or a **plan/spec** (`.agents/plans/`) — the Shape check below differs by type. If the target exists only in the conversation so far (not yet published), validate it there and restate the corrected version in chat instead of writing a file.

### 2. Read the whole target once

Before changing anything, read start to finish. Partial reads miss the cross-section contradictions the Internal Consistency check exists to catch.

### 3. Walk the checklist

Go section by section through the doc, checking every applicable item below against it. For each hit, apply the fact/decision split from above.

<validation-checklist>

- **Shape** — the doc has the sections its type's template requires:
  - idea: Motivation, Goal, Decisions (locked), Out of scope, Open questions.
  - plan/spec: Problem Statement, Solution, User Stories, Implementation Decisions, Testing Decisions, Out of Scope, Further Notes.

  A `Status:` line sits under the H1 with a valid value ([triage-labels.md](../../ref/triage-labels.md)). An idea doc carries none of the banned implementation detail — file paths, class/method names, schemas, code blocks, PR sequencing ([issue-tracker.md](../../ref/issue-tracker.md)).

- **Internal consistency** — no User Story lacking matching Implementation Decision coverage; no Out of Scope bullet that a Decision or Testing Decision then contradicts; no Decision resting on an Open Question still unresolved.

- **Drift** — every named file, class, method, glossary term, or docstring claim still matches the current codebase. Grep or read to confirm — don't take the doc's word for it.

- **Testing shape** — Testing Decisions describe external behavior, not markup or implementation structure.

- **Completeness** — every Problem Statement claim is addressed by the Solution; every Solution element has at least one User Story; anything adjacent the doc doesn't cover is named in Out of Scope, not left implicit.

</validation-checklist>

### 4. Report

Under 200 words: what you corrected, and what's still open as a question.

Done when every checklist item has been checked against every section it applies to, and every finding is either corrected in place or listed as an open question — none silently dropped.
