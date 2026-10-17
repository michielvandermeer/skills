---
name: code-review
description: Review changes since a commit, branch, or tag against the coding standards and the Spec. Use when the user wants a branch, a PR, or work in progress reviewed.
---

Two-axis review of the diff between `HEAD` and a fixed point the user supplies:

- **Standards** — does the code conform to this repo's documented coding standards?
- **Spec** — does the code faithfully implement the originating issue / PRD / spec?

Both axes run as **parallel sub-agents** so they don't pollute each other's context, then this skill aggregates their findings.

## Process

### 1. Pin the fixed point

Whatever the user said is the fixed point — a commit SHA, branch name, tag, `main`, `HEAD~5`, etc. If they didn't specify one, ask for it.

Capture the diff command once: `git diff <fixed-point>...HEAD` (three-dot, so the comparison is against the merge-base). Also note the list of commits via `git log <fixed-point>..HEAD --oneline`.

Before going further, confirm the fixed point resolves (`git rev-parse <fixed-point>`) and the diff is non-empty. A bad ref or empty diff should fail here — not inside two parallel sub-agents.

### 2. Identify the spec source

Look for the originating spec, in this order:

1. An Issue reference or a Spec path passed in. Inside an implement run the caller passes the path of the run's Spec copy, `.agents/runs/<slug>/spec.md`.
2. The Issue under discussion.
3. The Issue the run slug in the current branch's name points to, as the Tracker ref says.
4. If nothing is found, ask the user where the spec is. If they say there isn't one, the **Spec** sub-agent will skip and report "no spec available".

Issues live in the repo's **Tracker**: carry out each operation on one — file, read, list, rewrite, set status, comment, link, close — as `.agents/refs/tracker.md` says, or as [setup/LOCAL.md](../setup/LOCAL.md) says when the repo has no ref.

### 3. Identify the standards sources

Anything in the repo that documents how code should be written. Check `.agents/refs/` first — the canonical spot for these — but also pick up root-level docs like `CODING_STANDARDS.md` or `CONTRIBUTING.md` if the repo has them there instead.

On top of whatever the repo documents, the Standards axis always carries the **design principles** in [PRINCIPLES.md](PRINCIPLES.md) in this skill's directory, which apply even when a repo documents nothing. Two rules bind them:

- **The repo overrides.** A documented repo standard always wins; where it endorses something a principle would flag, suppress the finding.
- **A judgement call unless it names a defect.** Each principle is a labelled heuristic ("possible Boundary discipline breach"). Its finding is a hard violation only when it names a wrong result, a crash, or lost data — and, like any standard here, skip anything tooling already enforces.

### 4. Spawn the reviewers

Spawn the two axes in parallel as `skills:reviewer` (`agents/reviewer.md` at the plugin root), which is pinned to Opus at high effort ([ADR-0049](../../docs/adr/0049-agents-are-pinned-in-their-agent-files.md)). A caller that names another model and effort for the reviewers has them passed as `model` and `effort` on each Agent call, which override the pin. A caller that names **one axis** spawns only that axis's reviewer, and the report carries only that axis. A host without that agent type dispatches `general-purpose` with the same prompt.

Both briefs end with the same instruction: "Run the `/technical-writing` skill and write your findings to its bar. Your entire report is one message." You present their reports nearly verbatim, so the plainness has to come from them. The parent keeps only the last message. A caller that says only agents read the report, as `/implement` does, gets briefs that end with "Your entire report is one message." alone: no person reads the report, so the bar protects no one.

**Standards sub-agent prompt** — include:

- The full diff command and commit list.
- The list of standards-source files you found in step 3, and the absolute path of PRINCIPLES.md, with the instruction to list the headings of each first (`grep -n '^#'`) and read the sections that bear on the diff.
- The Spec's path from step 2, when a Spec was found, with the instruction to read its Implementation Decisions section (`grep -n '^## '` finds it) before judging. A Judgement call that a decision there explicitly settles is dropped from the report. A Hard violation that a decision there explicitly mandates is reported as a Judgement call that names the decision.
- Findings the caller says were declined before, each with its reason, when the caller hands any: raise one again only when its reason does not hold, and say why.
- Findings the caller hands to check, when it hands any, as `/implement` does from its second Iteration: judge each as fixed or declined, and judge the fix itself against the standards.
- The brief: "Report — per file/hunk where relevant — (a) every place the diff violates a documented standard: cite the standard (file + the rule); and (b) any place the diff goes against a design principle: name the principle and quote the hunk. Open each finding with `Hard violation:` or `Judgement call:`. A hard violation breaks a rule a documented standard states, or names a defect — a wrong result, a crash, or lost data — whichever principle or rule it falls under. Every other finding is a judgement call, and a documented repo standard overrides a principle. Skip anything tooling enforces. Under 400 words."

**Spec sub-agent prompt** — include:

- The diff command and commit list.
- The path or fetched contents of the spec.
- The brief: "Report: (a) requirements the spec asked for that are missing or partial; (b) behaviour in the diff that wasn't asked for (scope creep); (c) requirements that look implemented but where the implementation looks wrong. Quote the spec line for each finding. Under 400 words."

If the spec is missing, skip the Spec sub-agent and note this in the final report.

### 5. Aggregate

Present the two reports under `## Standards` and `## Spec` headings, verbatim or lightly cleaned; a caller that named one axis gets only that heading. Do **not** merge or rerank findings — the two axes are deliberately separate (see _Why two axes_).

End with a one-line summary: total findings per axis, and the worst issue _within each axis_ (if any). Don't pick a single winner across axes — that's the reranking the separation exists to prevent.

## Why two axes

A change can pass one axis and fail the other:

- Code that follows every standard but implements the wrong thing → **Standards pass, Spec fail.**
- Code that does exactly what the issue asked but breaks the project's conventions → **Spec pass, Standards fail.**

Reporting them separately stops one axis from masking the other.
