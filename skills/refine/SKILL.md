---
name: refine
description: Take an Idea or Jira ticket through grilling, an optional Prototype, and a Spec, then write a plain-language summary back.
disable-model-invocation: true
argument-hint: "<idea path or Jira key>"
---

# Refine

One person, often a non-developer who knows the product. Start from an Idea or a Jira ticket. Grill until nothing is left to ask, ask for a Prototype, write a Spec, write a summary of that Spec back onto the Idea or ticket. Finish in this session ([ADR-0036](../../docs/adr/0036-refine-ends-in-a-spec.md)).

Live rounds and the write-back run `/plain-language`.

## 1. Take the input

Pull the checkout, with submodules.

The invocation is a Jira ticket key or URL, or an Idea at `.agents/ideas/<slug>.md`. Retrieve a ticket through whatever MCP tools this session has. Anything else — a typed sentence, another markdown file, an empty invocation — stop and ask for an Idea path or a Jira key. A ticket that cannot be read is the same stop.

Name the slug once: the Idea filename stem, or a kebab-case slug of the change, not the ticket key. `/prototype` and `/to-spec` use that slug. A second `/refine` on the same Idea or ticket replaces the Spec and replaces the summary.

Done when you have the Idea file or the ticket body in hand and the slug is named.

## 2. Grill

Run `/grilling` with the subject pinned to **functional** for the whole session. How it is built is declared from the codebase. A developer who wants to grill implementation types `/grill-with-docs`.

Facts from the code come from grilling's explorers.

Run `/domain-modeling`. Glossary entries land in `CONTEXT.md` as terms settle. An ADR that passes the three-part test is written at Spec time, without a Question about it.

Screen behaviour is settled in words. `/prototype` waits for step 3.

If they stop before the frontier is empty, write every settled decision and unanswered Question back onto the Idea or ticket, commit that, and stop.

Done when the frontier is empty.

## 3. Ask for a Prototype

Ask whether to build a Prototype of the agreed behaviour. Build one unless they say no.

If they say no, go to step 4.

If they say yes, follow `/prototype` as serving a larger effort. The folder is `.agents/prototypes/<slug>/`.

If the verdict opens new questions, grill those under step 2's rules, then ask whether to change the Prototype. Loop until the frontier is empty and they have declined a further change, or accepted the current Prototype.

Done when they have declined a Prototype, or `.agents/prototypes/<slug>/` is on disk and the frontier is empty.

## 4. Read-back, then Spec

The grilling read-back. After it is confirmed, run `/to-spec` as serving `/refine`.

Write ADRs that passed the three-part test in the same turn as the Spec.

Done when `.agents/specs/<slug>.md` exists and `/validate-spec` has run.

## 5. Write the summary back

Write a plain-language summary of the Spec: the problem, the solution, and the user stories. Leave implementation and testing in the Spec.

Show the payload and wait for a yes.

- Idea, yes: overwrite the file with a `Spec:` line at the top and the summary in markdown.
- Jira, yes: replace the ticket description with the summary in Jira markup. The description is the summary alone.
- No: leave the Idea or ticket as it was.

Commit the Spec, the overwritten Idea when write-back replaced one, and any glossary, ADR, or Prototype folder — staged by name, on this branch, without asking. A Jira replace is an API call in this close. A no still commits the Spec and those other files.

Then run `/retro`.

Done when write-back has a yes or a no, the commit is made, and `/retro` has finished.
