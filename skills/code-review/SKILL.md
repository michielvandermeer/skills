---
name: code-review
description: Review the changes since a fixed point (commit, branch, tag, or merge-base) along two axes — Standards (does the code follow this repo's documented coding standards?) and Spec (does the code match what the originating issue/PRD asked for?). Runs both reviews in parallel sub-agents and reports them side by side. Use when the user wants to review a branch, a PR, work-in-progress changes, or asks to "review since X".
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
- **Always a judgement call.** Each principle is a labelled heuristic ("possible Boundary discipline breach"), never a hard violation — and, like any standard here, skip anything tooling already enforces.

### 4. Spawn the reviewers

Spawn the two axes in parallel as `skills:reviewer` (`agents/reviewer.md` at the plugin root), which is pinned to Opus at high effort ([ADR-0049](../../docs/adr/0049-agents-are-pinned-in-their-agent-files.md)). A caller that names another model and effort for the reviewers has them passed as `model` and `effort` on each Agent call, which override the pin. A caller that names **one axis** spawns only that axis's reviewer, and the report carries only that axis. A host without that agent type dispatches `general-purpose` with the same prompt.

Both briefs end with the same instruction: "Run the `/plain-language` skill and write your findings to its bar. Your entire report is one message." You present their reports nearly verbatim, so the plainness has to come from them. The parent keeps only the last message.

**Standards sub-agent prompt** — include:

- The full diff command and commit list.
- The list of standards-source files you found in step 3, and the absolute path of PRINCIPLES.md, with the instruction to list the headings of each first (`grep -n '^#'`) and read the sections that bear on the diff.
- Findings the caller says were declined before, each with its reason, when the caller hands any: raise one again only when its reason does not hold, and say why.
- The brief: "Report — per file/hunk where relevant — (a) every place the diff violates a documented standard: cite the standard (file + the rule); and (b) any place the diff goes against a design principle: name the principle and quote the hunk. Distinguish hard violations from judgement calls — documented-standard breaches can be hard, but principle findings are always judgement calls, and a documented repo standard overrides a principle. Skip anything tooling enforces. Under 400 words."

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
