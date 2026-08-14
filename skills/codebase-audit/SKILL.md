---
name: codebase-audit
description: Audit the whole codebase for simpler data structures and organizing models. Read-only.
disable-model-invocation: true
---

# Codebase Audit

You are the **driving session**. Inspect the whole codebase for **material** simplifications in data structures, state representation, or organizing model. The only write is the **Codebase audit** at `.agents/codebase-audits/<timestamp>/report.md`. Leave every other file untouched — no tests, no implementation, no commit, no push.

Distinct from `/improve-data-structures` (recent work, may implement) and `/improve-codebase-architecture` (module depth, then grill).

Continue until every identifiable subsystem has been reviewed and the report passes step 3.

## Process

### 1. Coverage contract

Determine a timestamp. Create the report from [REPORT.md](REPORT.md). Run `/plain-language` before any sentence a person will read there. Read `CONTEXT.md` first so subsystem names use the project's terms.

Inspect the repository. Inventory every identifiable subsystem — frontend, backend, shared infrastructure, platform bridges, generated-contract ownership, test and tooling — wherever each is material.

Each row gets a stable ID, a name, an exact **ownership boundary**, key implementation files, relevant public interfaces / major call sites / tests, and status `queued`. The inventory is the **coverage contract**: every row names an exact boundary. A catch-all row is not coverage.

Done when every identifiable subsystem has a complete `queued` row and the report file exists.

### 2. Bounded reviews

Dispatch fresh `skills:explorer` agents. One distinct subsystem and exact, non-overlapping ownership boundary per worker. Give each the absolute path to [WORKER.md](WORKER.md) in this skill's directory and the filled-in inventory row. Mark the row `in review`.

Keep **lanes** to the number you can actively coordinate. One consolidated wait. Let a slow lane finish. Close a worker after you harvest it.

On harvest, verify every finding against the current repository before accepting it. Reject, narrow, or demote a recommendation that is vague, duplicates another, misunderstands intentional semantics, or only relocates complexity. A skip is completed coverage. Deduplicate overlapping findings and assign each accepted recommendation to one authoritative subsystem.

Open the next `queued` row as a lane frees.

Done when every inventory row is `recommend` or `skip`, every accepted finding has every field in [WORKER.md](WORKER.md), and every duplicate is recorded as superseded.

### 3. Audit the audit

Dispatch a fresh `skills:explorer` that was not a subsystem worker. Give it the report path and [WORKER.md](WORKER.md). It returns missing subsystems (each with an exact boundary), overlapping or duplicate findings, recommendations that fail the materiality bar, findings missing a required field, and a suggested ranking.

A real omission becomes a new inventory row and gets its own lane — resume step 2 for that row. Never absorb it into a completed boundary.

Rank accepted recommendations by concrete impact, confidence, implementation effort, blast radius, and prerequisites. Name the best first implementation slices.

The audit is complete only when:

- every identifiable subsystem is `recommend` or `skip`
- every finding has complete evidence, scope, risk, and validation
- duplicates and weak abstractions are gone
- priorities and dependencies are internally consistent
- no file outside the audit folder has changed

Give the user the report's absolute path and a short ranking of what to do first.
