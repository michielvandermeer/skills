---
name: validate-spec
description: Validate an Issue, a Spec, a plan, or the current conversation against this repo's own template rules and the current codebase — fix stale references and contradictions in place, flag real decisions as open questions.
disable-model-invocation: true
user-invocable: false
---

# Validate Spec

Validate an Issue, a Spec draft, a plan, or a conversation against the checklist below. A **fact** — a stale reference, a broken link, a contradiction resolvable by rereading the doc or the code — gets corrected in place. A **decision** — anything that would change scope, or trades one valid design against another — gets flagged as a question instead, the same fact/decision split `/grilling` uses.

## Process

### 1. Pin the target

An Issue reference or a file path passed in; otherwise the Issue or plan already under discussion; otherwise the Issue the run slug in the current branch's name points to, as the Tracker ref says. Ask if none of these resolve.

Issues live in the repo's **Tracker**: carry out each operation on one — file, read, list, rewrite, set status, comment, link, close — as `.agents/refs/tracker.md` says, or as [setup/LOCAL.md](../setup/LOCAL.md) says when the repo has no ref.

Note the target's type — the Shape check below differs by type. An Issue's status sets it: a `needs-` status makes it a **`needs-` Issue**; `ready-for-agent` or `ready-for-human` makes it a **Spec**. A file path — such as the draft a Validator is handed — or a plan is a Spec too. An Issue in `wayfinding` is a Map, which this checklist does not cover: say so and stop. If the target exists only in the conversation so far (not yet published), validate it there and restate the corrected version in chat instead of writing it anywhere. Corrections to an Issue land in one rewrite of its body, once step 3 is done.

### 2. Read the whole target once

Before changing anything, read start to finish. Partial reads miss the cross-section contradictions the Internal Consistency check exists to catch.

### 3. Walk the checklist

Go section by section through the doc, checking every applicable item below against it. For each hit, apply the fact/decision split from above.

<validation-checklist>

- **Shape** — the target has the sections its type's template requires:
  - `needs-` Issue: Motivation, Goal, Decisions (locked), Out of scope, Open questions.
  - Spec: Problem Statement, Solution, How to Check It, User Stories, Implementation Decisions, Testing Decisions, Out of Scope, Further Notes. A Spec without How to Check It is a fact: write it from the Solution and User Stories, as the `/to-spec` template lays out.

  An Issue carries exactly one status: `needs-triage`, `needs-info`, `needs-grilling`, `needs-human`, `wayfinding`, `ready-for-agent`, or `ready-for-human`. Any other status, or a second one, is a question: which status it holds is a decision. Until it is answered, check the Issue as the type its sections fit. A `needs-` Issue carries none of the banned implementation detail — file paths, class/method names, schemas, code blocks.

- **Internal consistency** — no User Story lacking matching Implementation Decision coverage; no Out of Scope bullet that a Decision or Testing Decision then contradicts; no Decision resting on an Open Question still unresolved.

- **Drift** — every named file, class, method, glossary term, or docstring claim still matches the current codebase. Grep or read to confirm — don't take the doc's word for it. A claim of absence is a claim too: "X does not mention Y", "nothing else uses Z", "no other code changes", "no X needs editing". Search the repo for the thing it says is missing. Check each "needs no edit" claim against the repo's own rules in `CLAUDE.md`, `AGENTS.md`, and the files they point to, such as a rule to update the README on every change. A false claim is a fact: correct it, and when a rule requires an edit the Spec ruled out, add that edit to Implementation Decisions.

- **Product reader** — Problem Statement, Solution, How to Check It, and User Stories name only what a person meets on the product, and terms `CONTEXT.md` defines. A file, function, class, or internal part named there is a fact: reword it as what the person meets, and carry the detail to Implementation Decisions when they do not already hold it. Every screen, control, or message a Hand check names is in the markup or the code, or the Solution adds it.

- **Width** — Spec only. Search the code for how it already does each job an Implementation Decision takes on. A decision that builds a new mechanism where the code already does the same job another way, without saying why that way falls short, is a question. So is a decision that guards against a failure without naming the failure and how it realistically happens. Both stay questions: how wide a Spec builds is a decision.

- **Principles** — Spec only. Apply each of the **Planning principles** in [to-spec/PRINCIPLES.md](../to-spec/PRINCIPLES.md) whose "In a Spec" signs the Spec shows. Each miss is a question: meeting it changes what gets built, or needs a person to split, prototype, or decide.

- **Testing shape** — Testing Decisions describe external behavior, not markup or implementation structure. Every element, class, attribute, or output a test is said to read is one the repo's testing documents allow: read those documents, found the way `/code-review` finds Coding standards. One they forbid is a fact: reword it to what they allow, such as the element's text or state.

- **Completeness** — every Problem Statement claim is addressed by the Solution; every Solution element has at least one User Story and one Hand check, unless How to Check It says nothing changes for a person; anything adjacent the doc doesn't cover is named in Out of Scope, not left implicit.

</validation-checklist>

### 4. Report

Read [`technical-writing/SKILL.md`](../technical-writing/SKILL.md) and follow it — `/technical-writing` does not load as a skill. Then report in under 200 words, at its bar: what you corrected, and what's still open as a question.

Done when every checklist item has been checked against every section it applies to, and every finding is either corrected in place or listed as an open question — none silently dropped.
