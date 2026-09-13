# 01 — Bound the Planner walk

Status: done
Blocked by: none

## What to build

`/implement` starts building once the Planner can write every Step file. The walk is done at that point: every Footprint filled, every `Blocked by` line written. Reading after that is not the walk. A Planner that already has enough to write the files stops even if it could keep searching. A Spec that truly spans many files still gets a walk long enough to name them.

A file is opened only if it might belong on a Footprint, or to settle a slice or blocker the Spec left to the code. That is the whole permission to read. Documents the host already placed in the Planner's context stay already-read. Historical Step files from other runs are not a template; the slicing rules document is. Filling Spec silence stays in `What to build` and uses the walk already done — it is not a second explore.

The rest of the slicing rules stay: tracer bullets, prefactor first, Wide refactor as expand–contract, overlapping Footprints as a blocking edge, the last Step blocked by every other Step, a thinner source yielding coarser Steps, a small Spec yielding one Step, another repository planned last. The Footprint stays advisory and complete — files, symbols, every project. The Planner stays one agent at the Driving session's model and effort. `/implement-oneshot` is unchanged.

Write every Step file, commit once, return only the index. The index line still names title, blockers, and a short deliverable. The Planner's whole reply is that index: one line per Step, `NN | title | blocked by: none|<NNs> | one-line deliverable`. Extra prose, a design note, or a question is not the index — the same shape as a Step agent that does not return the three-line report.

The Driving session already halts when the Planner fails or returns no Steps. It now also halts when `.agents/steps/<slug>/` is missing or contains no Step files, and when the reply is not the index. It does not dispatch another agent to write or commit the files. The existing fallback that commits an already-written dirty directory stays.

A halt is the existing Halting section: non-destructive, session over, worktree and Spec left in place so the user can re-invoke `/implement`. Report that the Planner failed and why. There is no Planner retry inside the run.

A missing or empty steps directory is not a planned run. On re-invoke, treat that as a fresh plan so the Planner runs again; do not skip to running Steps, and do not treat an empty directory as every Step done. A non-index reply with Step files already on disk is still a failed Planner this run; re-invoke then finds those files and resumes at running Steps — that is existing in-flight behaviour, not a writer dispatch.

After a successful plan, Ready Steps still run together.

The `Planner` glossary entry and the ADR-0010 amendment already name the bound (landed with this Spec). They stay the definition site and the why. This Step writes the operational rule into the slicing rules and the halt into the plan step. Do not coin a new term. Do not restore an unbounded walk as "what 0010 asked for".

## Footprint

Projects: none

- `skills/implement/STEPS.md` — walk completion, permission to read, silence-fill from the walk already done
- `skills/implement/SKILL.md` — plan step halt (missing or empty steps directory, reply that is not the index, no writer dispatch); dirty-directory commit fallback; Halting
- `CONTEXT.md` — `Planner`
- `docs/adr/0010-steps-record-their-footprint.md` — Amendment — the walk stops at the Footprint

## Acceptance criteria

- [x] The slicing rules end the walk when every Step file can be written, including Footprint and `Blocked by`.
- [x] A file is opened only if it might belong on a Footprint, or to settle a slice or blocker the Spec left to the code.
- [x] Host-provided documents are not opened again; historical Step files from other runs are not a template.
- [x] Filling Spec silence stays in `What to build` and uses the walk already done.
- [x] Tracer bullets, prefactor first, Wide refactor as expand–contract, overlapping Footprints as a blocking edge, the last Step blocked by every other Step, a thinner source yielding coarser Steps, and another repository planned last all remain.
- [x] The plan step halts when the steps directory is missing or empty, or when the Planner's reply is not the index, and does not dispatch an agent to write or commit the files.
- [x] The dirty-directory commit fallback remains.
- [x] A failed Planner leaves the worktree and the Spec in place; a missing or empty steps directory is a fresh plan on re-invoke.
- [x] Ready Steps still run together after a successful plan.
- [x] The `Planner` glossary entry names the bound; ADR-0010 says the paid slowness is recording the Footprint, not an unbounded extra walk.
- [x] `/implement-oneshot` is unchanged; the Planner remains one agent at the session's model and effort.
- [x] A one-Step Spec still yields one Step file; the Footprint still names files, symbols, and every project.

## Outcome

Wrote the walk completion criterion, permission to read, and silence-fill-from-the-walk into `skills/implement/STEPS.md`. Plan step now succeeds only on an index reply with Step files on disk; otherwise it halts without a writer dispatch, keeps the dirty-directory commit fallback, and treats a missing or empty steps directory as a fresh plan on re-invoke. In-flight detection now keys off the run worktree (branch `<slug>`) as well as the steps path, so a failed Planner with no Step files still resumes into that worktree.

Footprint drift: `CONTEXT.md` (`Planner`) and `docs/adr/0010-steps-record-their-footprint.md` (Amendment — the walk stops at the Footprint) already named the bound from the triage commit that landed this Spec; this Step did not edit them. Operational edits landed only in `STEPS.md` and `SKILL.md`. `/implement-oneshot` untouched.
