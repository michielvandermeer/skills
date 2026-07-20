# mvdmio Skills

A collection of software-engineering [skills](https://docs.claude.com/en/docs/claude-code/skills) for Claude Code, distributed as a Claude Code **plugin**. This repository is both the plugin and its own single-plugin **marketplace**, so you can install everything with two commands.

These skills are based on [Matt Pocock's skills](https://github.com/mattpocock/skills) — see [Credits](#credits).

## Install

Add the marketplace, then install the plugin:

```
/plugin marketplace add michielvandermeer/skills
/plugin install skills@mvdmio
```

`/plugin marketplace add` also accepts the full git URL (`git@github.com:michielvandermeer/skills.git`) if you prefer SSH.

## Updating

Installed plugins are cached under `~/.claude/plugins/cache/`; they are **not** committed into your consuming repos.

This plugin has **no pinned version**, so every commit to the default branch is treated as a new version — installed copies always track the latest.

- **Manual:** `/plugin update skills` (or `claude plugin update skills` from the CLI).
- **Automatic:** Claude Code auto-updates plugins in the background.

> To switch to deliberate, versioned releases instead, add a `version` field to `.claude-plugin/plugin.json`; consumers would then update only when you bump it.

## Repository layout

```
.
├── .claude-plugin/
│   ├── plugin.json        # plugin manifest (name, metadata)
│   └── marketplace.json   # marketplace catalog (this repo is its own marketplace)
├── skills/                # one directory per skill, each with a SKILL.md
│   ├── code-review/
│   ├── tdd/
│   └── ...
├── LICENSE
└── README.md
```

The `skills/` directory is discovered automatically by the plugin loader — no `skills` field in the manifest is required.

## Skills

| Skill | Description |
|-------|-------------|
| `cleanup-specs` | Removes all Spec, Plan, and Idea documents that have been implemented. |
| `code-review` | Review changes since a fixed point along two axes — Standards and Spec — in parallel sub-agents. |
| `codebase-design` | Shared vocabulary for designing deep modules. |
| `diagnosing-bugs` | Diagnosis loop for hard bugs and performance regressions. |
| `domain-modeling` | Build and sharpen a project's domain model. |
| `grilling` | Grill the user relentlessly about a plan or design. |
| `grill-me` | A relentless interview to sharpen a plan or design. |
| `grill-with-docs` | A relentless interview that also produces ADRs and a glossary as you go. |
| `handoff` | Compact the current conversation into a handoff document for another agent. |
| `implement` | Implement a piece of work based on a spec or set of tickets. |
| `improve-codebase-architecture` | Scan for deepening opportunities, report them, then grill the one you pick. |
| `improve-data-structures` | Review recent work for data structures that would materially simplify the code. |
| `migrate-doc-layout` | Move spec, idea, reference, and architecture-review documents into this repo's canonical `.agents/` layout. |
| `prototype` | Build a throwaway prototype to answer a design question. |
| `research` | Investigate a question against high-trust primary sources and capture findings as Markdown. |
| `tdd` | Test-driven development. |
| `to-spec` | Turn the current conversation into a spec and publish it to `.agents/specs/`. |
| `triage` | Move issues through a triage state machine into agent-ready briefs. |
| `validate-spec` | Validate a plan or spec against this repo's template rules and codebase; fix stale references in place. |
| `wayfinder` | Plan a huge chunk of work as a shared map of investigation tickets, resolved one at a time. |
| `writing-great-skills` | Reference for writing and editing skills well. |

## Credits

These skills are derived from and inspired by [**Matt Pocock's skills**](https://github.com/mattpocock/skills). Many thanks to Matt for the original work.

## License

[MIT](./LICENSE)
