---
name: cleanup-specs
description: "Removes all Spec, Plan, and Idea documents that have been implemented."
disable-model-invocation: true
---

Go through the Idea (`.agents/ideas/`) and Spec (`.agents/specs/`) documents and remove all that have been implemented.
Do not just look at the status in the document; verify their status in the codebase.
