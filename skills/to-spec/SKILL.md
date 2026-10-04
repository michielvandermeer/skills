---
name: to-spec
description: Turn the current conversation into a Spec and write it onto its Issue in the repo's Tracker — no interview, just synthesis of what you've already discussed.
---

This skill takes the current conversation context and codebase understanding and produces a spec (you may know this document as a PRD). Do NOT interview the user — just synthesize what you already know. A decision the conversation did not settle is not yours to close: ask it as one `/grilling` round, then continue.

## Process

1. Explore the repo to understand the current state of the codebase, if you haven't already. Use the project's domain glossary vocabulary throughout the spec, and respect any ADRs in the area you're touching.

2. Sketch out the seams at which you're going to test the feature. Existing seams should be preferred to new ones. Use the highest seam possible. If new seams are needed, propose them at the highest point you can. The fewer seams across the codebase, the better - the ideal number is one.

3. Pick the Spec's **Issue**: the one the caller names; otherwise the Issue this session started from; otherwise, or when the caller asks for a new one, a new Issue that step 5 files.

Issues live in the repo's **Tracker**: carry out each operation on one — file, read, list, rewrite, set status, comment, link, close — as `.agents/refs/tracker.md` says, or as [setup/LOCAL.md](../setup/LOCAL.md) says when the repo has no ref.

Draft the Spec using the template below in a new temporary file in the OS temp directory. On a local Markdown Tracker the Issue file itself is the draft: file it at this step when the Issue is new, and write the whole of step 5's update into it. Run the `/plain-language` skill first: a Spec is read cold, weeks later, by someone who was not in this conversation, so it holds the durable-document bar. In a repo with a `CONTEXT-MAP.md`, every `.agents/<kind>/` path in this skill gains a context subfolder — follow [domain-modeling/CONTEXT-PATHS.md](../domain-modeling/CONTEXT-PATHS.md).

4. Dispatch a fresh **Validator** (`skills:validator`, `agents/validator.md` at the plugin root) with the draft's path. That path is the whole prompt. The Validator runs on your model at medium effort ([ADR-0052](../../docs/adr/0052-a-fresh-validator-checks-a-new-spec.md)). A host without that agent type dispatches `general-purpose` with the same prompt.

Wait for it.

The report is finished when it is the Validator's checklist report: corrections, open questions, or a report that names neither. Show that report to the user. It is what you carry forward from the check. A finished report continues at step 5. Open questions leave step 5 free to run.

Any other result ends the session before step 5. Tell the user the check did not finish, and give the draft's path. The draft stays as the Validator left it. Step 5 stays unstarted, and so does anything the caller does after `/to-spec`.

5. Write the draft the Validator left to the Spec's Issue in one update: rewrite its body with the draft, set its status to `ready-for-agent` — `ready-for-human` when a person builds it — and, when the caller names an Issue that must land first, link it as blocked by that Issue. A new Issue is filed with a title naming the change and that body, status, and link. On a local Markdown Tracker the draft already holds this update.

Then commit the files this session created or changed — glossary and ADR edits, the prototype folder, and on a local Markdown Tracker the Issue files — staged by name, on the branch you are on, without asking. A commit that writes an ADR names the Issue's reference in its message. Leave every other working-tree change alone; another session may own it. When `/refine` is the caller, leave the commit to `/refine`. When `/wayfinder` is the caller, leave the commit to `/wayfinder`, which makes one commit for every Spec it cut.

<spec-template>

## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

A LONG, numbered list of user stories. Each user story should be in the format of:

1. As an <actor>, I want a <feature>, so that <benefit>

<user-story-example>
1. As a mobile bank customer, I want to see balance on my accounts, so that I can make better informed decisions about my spending
</user-story-example>

This list of user stories should be extremely extensive and cover all aspects of the feature.

## Implementation Decisions

A list of implementation decisions that were made. This can include:

- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Do NOT include specific file paths or code snippets. They may end up being outdated very quickly.

Exception: a prototype folder at `.agents/prototypes/<slug>/` is named, not inlined. A snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape) may still be inlined within the relevant decision — trim to the decision-rich parts.

## Testing Decisions

A list of testing decisions that were made. Include:

- A description of what makes a good test (only test external behavior, not implementation details)
- Which modules will be tested
- Prior art for the tests (i.e. similar types of tests in the codebase)

## Out of Scope

A description of the things that are out of scope for this spec.

## Further Notes

Any further notes about the feature.

</spec-template>
