---
name: refine
description: Take an Issue through grilling, an optional Prototype, and a Spec that becomes the Issue's body.
disable-model-invocation: true
argument-hint: "<issue reference>"
---

# Refine

One person, often a non-developer who knows the product. Start from an Issue. Grill until nothing is left to ask, ask for a Prototype, and write a Spec that becomes the Issue's body. Its Problem Statement, Solution, and User Stories are the plain-language summary that person reads in the Issue. Finish in this session ([ADR-0039](../../docs/adr/0039-refine-ends-in-a-spec.md)).

Live rounds run `/plain-language`.

## 1. Take the input

Pull the checkout, with submodules.

The invocation is an Issue reference. Read the Issue. An issue from another tracker is seed text, and `/to-spec` files the Spec as a new Issue in this repo's Tracker. Anything else — a typed sentence, a markdown file, an empty invocation — stop and ask for an Issue reference. An Issue that cannot be read is the same stop.

Issues live in the repo's **Tracker**: carry out each operation on one — file, read, list, rewrite, set status, comment, link, close — as `.agents/refs/tracker.md` says, or as [setup/LOCAL.md](../setup/LOCAL.md) says when the repo has no ref.

In a repo with a `CONTEXT-MAP.md`, every `.agents/<kind>/` path in this skill gains a context subfolder — follow [domain-modeling/CONTEXT-PATHS.md](../domain-modeling/CONTEXT-PATHS.md).

Name the slug once: the Issue's run slug as the Tracker ref gives it, or a kebab-case slug of the change for seed text. `/prototype` uses that slug. A second `/refine` on the same Issue replaces its Spec.

Done when you have the Issue in hand and the slug is named.

## 2. Grill

Run `/grilling` with the subject pinned to **functional** for the whole session. How it is built is declared from the codebase. A developer who wants to grill implementation types `/grill-with-docs`.

Facts from the code come from grilling's explorers.

Run `/domain-modeling`. Glossary entries land in `CONTEXT.md` as terms settle. An ADR that passes the three-part test is written at Spec time, without a Question about it.

Screen behaviour is settled in words. `/prototype` waits for step 3.

If they stop before the frontier is empty, write every settled decision and unanswered Question to the Issue as `/grilling` does on an early stop, commit, and stop.

Done when the frontier is empty.

## 3. Ask for a Prototype

Ask whether to build a Prototype of the agreed behaviour. Build one unless they say no.

If they say no, go to step 4.

If they say yes, follow `/prototype` as serving a larger effort. The folder is `.agents/prototypes/<slug>/`.

If the verdict opens new questions, grill those under step 2's rules, then ask whether to change the Prototype. Loop until the frontier is empty and they have declined a further change, or accepted the current Prototype.

Done when they have declined a Prototype, or `.agents/prototypes/<slug>/` is on disk and the frontier is empty.

## 4. Read-back, then Spec

The grilling read-back. After it is confirmed, run `/to-spec` as serving `/refine`. The confirmed Read-back approves the Spec `/to-spec` writes to the Issue.

Write ADRs that passed the three-part test in the same turn as the Spec.

Done when the Issue carries the Spec and `/to-spec` has returned from a finished Validator report. That report is the check this step waits on.

## 5. Commit

Commit every file this session changed — glossary and ADR edits, the Prototype folder, and the Issue's own file when the Tracker keeps Issues in the repo — staged by name, on this branch, without asking. A commit that writes an ADR names the Issue's reference in its message.

Then run `/retro`.

Done when the commit is made and `/retro` has finished.
