---
extends: feature, bug-fix, refactoring, perf-issue, visual-parity
when: An /implement run builds a Spec to landing with no person in the loop.
---

# Implement overlay

`/implement` applies these changes to whichever bundled playbook its Spec routed to, after the consuming repo's own `.agents/playbooks/`. Each change anchors on the bundled step's own words, and `check-playbooks.mjs` proves every anchor before the run starts.

- **Before** "`how` over the affected subsystem." The design-skip rule: when the Spec's Implementation Decisions already name the data shape and its organizing structure, and the change touches one or two files, skip this step and the `architect` step with `skip: <the Spec line that fixed the shape>`. Otherwise both run.
- **In** "Give every file-writing delegate its own worktree" The run worktree is the delegate's worktree, and delegates write in it one at a time. Only a workstream the throughput checkpoint names as disjoint gets its own worktree, branched from the run branch's head, and merges back in order.
- **After** "Verify on the matching surface." The verification gate from `/implement`'s Gates section: a fresh Verifier that wrote none of the code drives the same surface and runs every Hand check in `spec.md`. Only VERIFIED on every item passes.
- **After** "Verify on the same surface." The same verification gate, whose pass also needs the step 1 red output in `evidence/`.
- **In** "Reproduce it yourself on the matching surface" Save the red output to `evidence/repro-red.txt`, trimmed to the assertion and the counts. A symptom that never goes red halts the run, with every way you tried in the report.
- **In** "Ask the user only with a stated, specific reason the control surface cannot reach the target, and only after driving it as far as it goes." Nobody is there to ask: that reason is a halt reason, stated in the report.
- **In** "If the baseline looks wrong, stop and ask, don't edit it." The stop is a halt; the report says what looks wrong.
- **In** "Stack follow-ups." A follow-up is a new Issue in the Tracker, with a category and a Spec stub, never a second landing in this run.
- **Replace** "If the design is contested, `interrogate` before shipping." No person reviews before landing, so the review gate always runs `interrogate`, with `spec.md` as the stated intent.
- **Replace** "Cite the measurement in the PR." Cite the baseline and post-fix numbers in the landing commit's body.
- **Replace** "Run **Opening a PR**" The review gate (`/deslop`, `/no-comments`, `interrogate`, each Act-on finding to a fresh delegate), then the landing gate (`check-run.mjs`), then `LANDING.md`. No pull request is opened: the landing commit's message plays the description, and one landing covers every component and unit.
