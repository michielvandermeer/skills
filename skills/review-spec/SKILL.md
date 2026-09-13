---
name: review-spec
description: Re-evaluate a Spec's Solution on this session's model and write the edits you approve.
argument-hint: "[path-or-slug]"
disable-model-invocation: true
---

# Review Spec

The Driving session is the reviewer.

Run `/plain-language` before every message the user reads.

## 1. Pin the Spec

A path or slug in the argument; otherwise the Spec already under discussion; otherwise the newest file under `.agents/specs/`. Stop if that is not a Spec file on disk. One Spec per run.

**Done** when a Spec file path is in hand, or the run has stopped.

## 2. Read

Read the Spec start to finish. Walk the application code the Solution would change — the modules, callers, and data it touches — until further files would not change the verdict. Start from paths and behaviour the Spec names. This session reads those files.

**Done** when the Spec and that area have been read in this session.

## 3. Judge

Hunt relentlessly: every **Unstated claim** that would change the Solution, every Spec claim the code contradicts, every decision with a real alternative the Solution did not take. Other sections only when they bear on the Solution.

Pick one verdict: `good`, `good with named changes`, or `not good`. `not good` may mean do not build this.

**Done** when every such claim is named and one verdict is chosen.

## 4. Propose

No Spec edits → state the verdict and stop.

Otherwise state the verdict, then one numbered list. Each item is a Spec edit: which section, why (one or two sentences), the exact replacement text. Other advice sits in the verdict.

Ask for numbers (`1,3,5`), `everything`, or `none`.

**Done** when the numbered list is in chat and the session is waiting for a reply.

## 5. Apply

Starts when the reply is in.

Parse:

- `everything` / `all` / similar → every item
- `none` / `nothing` / similar → empty set
- numbers and ranges (`1,3,5`, `1-3`) → those items
- otherwise ask once more; a second unparseable reply is an empty set

Write the approved items in list order into the Spec file. The list text is what lands. Leave the write uncommitted.

Empty set → stop.

Any write → run `/validate-spec` on that Spec. Its report ends the run.

**Done** when the Spec on disk matches the approved set, and either `/validate-spec` has reported or nothing was written.
