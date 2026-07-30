# mvdmio Skills

A collection of software-engineering [skills](https://docs.claude.com/en/docs/claude-code/skills) for Claude Code, distributed as a Claude Code **plugin**. This repository is both the plugin and its own single-plugin **marketplace**, so adding the marketplace and installing the plugin gets you every skill below.

These skills are based on [Matt Pocock's skills](https://github.com/mattpocock/skills) — see [Credits](#credits).

## Install

**1. Add the marketplace.** This registers the catalog; nothing is installed yet.

```
/plugin marketplace add michielvandermeer/skills
```

`/plugin marketplace add` also accepts the full git URL (`git@github.com:michielvandermeer/skills.git`) if you prefer SSH.

**2. Install the plugin.** This opens a scope picker.

```
/plugin install skills@mvdmio
```

| Scope | Where it applies | Written to |
|-------|------------------|------------|
| **User** | you, in every project | `~/.claude/settings.json` |
| **Project** | everyone working on this repo | `.claude/settings.json` (committed) |
| **Local** | you, in this repo only | `.claude/settings.local.json` |

Pick **user** unless you specifically want to share the plugin with collaborators on one repo. The scope you choose matters later — `/plugin update` targets one scope at a time (see [Updating](#updating)).

**3. Activate it.** Plugins load at startup, so a fresh install is inert until you reload:

```
/reload-plugins
```

**4. Check it worked.** `/plugin list` shows the installed version. Skills are namespaced by plugin name, so they invoke as `/skills:<name>`:

```
/skills:code-review
/skills:implement
```

### Non-interactive install

The same two steps from a shell, for dotfiles or provisioning scripts:

```sh
claude plugin marketplace add michielvandermeer/skills
claude plugin install skills@mvdmio --scope user
```

## Updating

Installed plugins are cached under `~/.claude/plugins/cache/`; they are **not** committed into your consuming repos.

This plugin has **no pinned version**, so Claude Code uses the git commit SHA as the version — every commit to the default branch is a new version.

### Manual

```
/plugin update skills@mvdmio
```

Or `claude plugin update skills@mvdmio` from the CLI. Two things to watch:

- **Use the qualified `skills@mvdmio` id.** The bare name `skills` can fail to resolve with `Plugin "skills" not found`.
- **Both default to `--scope user`.** If you installed at project or local scope, pass the matching `--scope` or the update won't find your install:

  ```sh
  claude plugin update skills@mvdmio --scope project
  ```

Updates apply on restart, or run `/reload-plugins` to pick them up in the current session.

### Automatic

Auto-update is **off by default for this plugin.** Claude Code enables it only for official Anthropic marketplaces; third-party ones like this must opt in. Two ways:

- **UI:** `/plugin` → **Marketplaces** → `mvdmio` → **Enable auto-update**.
- **Settings:** add `"autoUpdate": true` to the `mvdmio` entry under `extraKnownMarketplaces` in `~/.claude/settings.json`:

  ```json
  {
    "extraKnownMarketplaces": {
      "mvdmio": {
        "source": { "source": "github", "repo": "michielvandermeer/skills" },
        "autoUpdate": true
      }
    }
  }
  ```

> The flag is only read from **user**, `--settings`, and managed settings. Setting it in a repo's `.claude/settings.json` or `.claude/settings.local.json` is ignored, so it can't be enabled on your collaborators' behalf from a checked-out repo — each person opts in on their own machine.

Once enabled, Claude Code refreshes the marketplace and its plugins shortly after a session starts (a random delay of up to ten minutes, so the running session keeps the version it launched with). You'll be prompted to run `/reload-plugins`, or the new version loads on next launch.

Setting `DISABLE_AUTOUPDATER` turns off plugin auto-updates along with Claude Code's own. To keep plugin updates while pinning Claude Code, set `FORCE_AUTOUPDATE_PLUGINS=1` alongside it.

> To switch to deliberate, versioned releases instead, add a `version` field to `.claude-plugin/plugin.json`; consumers would then update only when you bump it.

## Repository layout

```
.
├── .claude-plugin/
│   ├── plugin.json        # plugin manifest (name, metadata)
│   └── marketplace.json   # marketplace catalog (this repo is its own marketplace)
├── agents/                # sub-agents the skills dispatch, one markdown file each
│   ├── explorer.md
│   ├── implementer.md
│   └── researcher.md
├── docs/adr/              # architecture decision records
├── skills/                # one directory per skill, each with a SKILL.md
│   ├── code-review/
│   ├── implement/
│   └── ...
├── CONTEXT.md             # the vocabulary these skills share
├── LICENSE
└── README.md
```

The `skills/` and `agents/` directories are discovered automatically by the plugin loader — no manifest fields are required. Agents register under a scoped name, so `agents/implementer.md` is dispatched as `skills:implementer`.

## Sub-agent cost tiers

These skills pin the model and effort of the sub-agents they dispatch, to keep spend off work whose scope was already decided. Two roles carry the policy:

- A **spec-bound dispatch** works to a document settled before it started, so it runs cheaper — `skills:implementer` at Sonnet, and all three shipped agents at `effort: medium`.
- Anything carrying design or review judgement is left at your session's own model and effort. That covers `/implement`'s planner, both `/code-review` reviewers, the `/improve-data-structures` pass, and the `/codebase-design` design-it-twice fan-out.

> **These skills assume a session on Opus or above.** The tiers are absolute, not relative to your session, so starting a Sonnet or Haiku session does **not** scale them down — a Haiku session gets Sonnet step agents and spends more than you chose. [ADR-0007](docs/adr/0007-pinned-subagent-model-tiers.md) records why it works that way and what it costs.

## Skills

| Skill | Description |
|-------|-------------|
| `cleanup-specs` | Removes all Spec, Plan, and Idea documents that have been implemented. |
| `code-review` | Review changes since a fixed point along two axes — Standards and Spec — in parallel sub-agents. |
| `codebase-design` | Shared vocabulary for designing deep modules. |
| `diagnosing-bugs` | Diagnosis loop for hard bugs and performance regressions. |
| `domain-modeling` | Build and sharpen a project's domain model. |
| `grilling` | Grill the user relentlessly, round by round, about a plan or design. |
| `grill-me` | A relentless round-by-round interview to sharpen a plan or design. |
| `grill-with-docs` | A relentless round-by-round interview that also produces ADRs and a glossary as you go. |
| `handoff` | Compact the current conversation into a handoff document for another agent. |
| `implement` | Implement a spec by slicing it into steps and running each one in its own sub-agent. |
| `improve-codebase-architecture` | Scan for deepening opportunities, report them, then grill the one you pick. |
| `improve-data-structures` | Review recent work for data structures that would materially simplify the code. |
| `migrate-doc-layout` | Move spec, idea, reference, and architecture-review documents into this repo's canonical `.agents/` layout. |
| `prototype` | Build a throwaway prototype to answer a design question. |
| `refine` | Grill a change into a functional description with Product, QA, and Development in the room. |
| `research` | Investigate a question against high-trust primary sources and capture findings as Markdown. |
| `to-spec` | Turn the current conversation into a spec and publish it to `.agents/specs/`. |
| `triage` | Move issues through a triage state machine into agent-ready briefs. |
| `validate-spec` | Validate a plan or spec against this repo's template rules and codebase; fix stale references in place. |
| `wayfinder` | Plan a huge chunk of work as a shared map of investigation tickets, resolved one at a time. |
| `writing-great-skills` | Reference for writing and editing skills well. |

## Credits

These skills are derived from and inspired by [**Matt Pocock's skills**](https://github.com/mattpocock/skills). Many thanks to Matt for the original work.

## License

[MIT](./LICENSE)
