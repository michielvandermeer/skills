# mvdmio Skills

A collection of software-engineering [skills](https://docs.claude.com/en/docs/claude-code/skills) for Claude Code, distributed as a Claude Code **plugin**. This repository is both the plugin and its own single-plugin **marketplace**, so adding the marketplace and installing the plugin gets you every skill below.

These skills are based on [Matt Pocock's skills](https://github.com/mattpocock/skills) — see [Credits](#credits). The plugin also includes [pstack](#pstack).

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
/skills:implement
/skills:poteto-mode
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

## Where your work lives

Each piece of work is one **Issue**, kept in your repo's **Tracker**. Out of the box, the Tracker is a folder of Markdown files in the repo itself, `.agents/issues/`. To use GitHub Issues or Jira instead, or another system you describe, run `/setup`. It writes `.agents/refs/tracker.md`, which tells the skills how to work with your Tracker. That file belongs to your repo, so you can edit it.

An Issue has exactly one status at a time:

| Status | What it means |
|--------|---------------|
| `needs-triage` | Nobody has looked at it yet. |
| `needs-info` | It waits on the person who reported it. |
| `needs-grilling` | A person must decide how to solve it. |
| `needs-human` | It waits on a secret or a manual test. |
| `wayfinding` | It is the map of a `/wayfinder` effort. |
| `ready-for-agent` | It carries a Spec for an agent to build. |
| `ready-for-human` | It carries a Spec for a person to build. |

A first rough thought and the Spec it grows into are the same Issue. When the Spec is written, it replaces the Issue's text. The earlier text stays in the Tracker's history (git, for the local Tracker), and comments stay as they are. Finished work is closed as done; work you decide against is closed as not planned.

The implement commands read an Issue and claim it before they start, so other runs leave it alone. On GitHub and Jira, claiming assigns the Issue to you, and a run stops on an Issue that is assigned to someone else. The claim is the only thing they write to the Tracker. A run lands on your branch as one commit named after the work, and then pushes your branch. That commit closes the Issue when your Tracker can do that from a commit, such as `Closes #42` on GitHub. Otherwise the final report names the Issue for you to close. When the run's retrospective then changes a file, the run pushes a second time.

To stop runs from pushing, add a line to your repo's `AGENTS.md` or `CLAUDE.md` saying implement runs do not push. Do this when a push to your branch deploys, or when you want to push yourself. If someone else pushed to your branch during the run, the run tells you, and the work waits on your machine for you to pull and push.

Everything else stays in the repo, whichever Tracker you use: Prototypes, codebase audits, ADRs, `CONTEXT.md`, and the files under `.agents/refs/`, Grilling profiles included. The run directory of an implement run sits in the checkout too, under `.agents/runs/`, but git ignores it, so it never lands. [ADR-0001](docs/adr/0001-each-repo-describes-its-tracker.md) records why.

## Repository layout

```
.
├── .claude-plugin/
│   ├── plugin.json        # plugin manifest (name, metadata)
│   └── marketplace.json   # marketplace catalog (this repo is its own marketplace)
├── agents/                # sub-agents the skills dispatch, one markdown file each
│   ├── explorer.md
│   ├── poteto-agent.md    # pstack's delegate, which the implement commands dispatch
│   ├── researcher.md
│   ├── validator.md
│   └── ...                # pstack's other agents
├── docs/adr/              # architecture decision records
├── hooks/                 # pstack's SessionStart hook
├── skills/                # one directory per skill, each with a SKILL.md
│   ├── implement/         # SKILL.md, LANDING.md, the overlay, and scripts/ (open-todo.mjs, check-run.mjs)
│   ├── implement-yolo/
│   └── ...
├── tools/import_pstack.py # imports pstack from pstack-claude
├── CONTEXT.md             # the vocabulary these skills share
├── LICENSE
├── LICENSE-pstack         # and LICENSE-cursor-team-kit, LICENSE-thermos: pstack's licenses
├── NOTICE.md              # the work by others this plugin includes
├── NOTICE-pstack.md       # what pstack brings in, and from where
└── README.md
```

The `skills/` and `agents/` directories and `hooks/hooks.json` are discovered automatically by the plugin loader — no manifest fields are required. Agents register under a scoped name, so `agents/explorer.md` is dispatched as `skills:explorer`.

## Model and effort pins

These skills pin the model and effort they run on, so parallel runs do not all inherit your session's most expensive setting. Nothing is pinned above `high`. A pin lives in a skill's or agent's header, so it is the same in every repo and there is no per-repo setting. [ADR-0049](docs/adr/0049-agents-are-pinned-in-their-agent-files.md) records why.

**Skills you type.** Only the skills that no other skill loads pin their own model, because a loaded skill would swap its caller's model for the rest of the turn.

- Opus at high: `/grill-with-docs`, `/brainstorm`, `/wayfinder`, `/implement`, `/implement-yolo`.
- Sonnet at high: `/triage`, `/codebase-audit`, `/doctor`, `/explain`, `/learn-habits`, `/setup`, and the pstack skills you type: `/automate-me`, `/babysit`, `/bro`, `/correct`, `/ketchup`, `/maintain-verification-skill`, `/poteto-help`, `/pr`, `/what-did-i-get-done`.

**Sub-agents.**

- Sonnet at medium: `skills:validator`, `skills:researcher`.
- Haiku at high: `skills:explorer`.
- Opus at high: the two `/thermo-nuclear-review` passes.

**Implement delegates.** An implement run dispatches pstack's `skills:poteto-agent` for every code-writing delegate and for the verifier, and runs pstack's `how`, `architect`, and `interrogate` skills. Each of those roles takes its model from `~/.claude/pstack-models.md`, the sheet `/skills:setup models` writes, so the cost of a run is set in one place you already own.

Everything else runs on the setting of the skill that starts it: the `/codebase-design` and `/brainstorm` fan-outs.

> **Your environment can override a pin.** When `CLAUDE_CODE_EFFORT_LEVEL` is set, it beats every effort pin. Your session's settings and `/effort` do not.

## Skills

| Skill | Description |
|-------|-------------|
| `brainstorm` | Explore a vague problem as very different Directions, side by side, and file the ones you keep as Issues. |
| `codebase-audit` | Audit the whole codebase for simpler data structures and organizing models. Read-only. |
| `codebase-design` | Shared vocabulary for designing deep modules. |
| `doctor` | Moves documents into the current project's canonical layout, turns old local Ideas, Specs, and Issues into Issues on the local Tracker, closes the ones already built, and brings every ADR to state the decision in force. Once `/setup` has run, it leaves Issues alone. |
| `domain-modeling` | Build and sharpen a project's domain model. |
| `explain` | Explain anything as a talk or a diagram in the chat, an HTML page, or a narrated video, picking the format that fits. |
| `grilling` | Grill the user relentlessly, round by round, about a plan or design. |
| `grill-with-docs` | A relentless round-by-round interview that also produces ADRs and a glossary as you go. |
| `implement` | Implement an Issue's Spec, or a description, as a pstack poteto-mode run in its own worktree: the matching playbook, Hillclimb included for a number to push toward a target, design before code, a verifier that wrote none of the code, an adversarial review, then one commit landed on your branch. |
| `implement-yolo` | The same run on this checkout and this branch. No worktree, no new branch, no merge. |
| `learn-habits` | Learn how each person answers grilling questions into a profile per person in the repo, so later rounds recommend what you would likely pick and name what each teammate would likely pick. Type it to rebuild your profile from past sessions; no grilling session runs it for you. |
| `prototype` | Build a throwaway prototype to answer a design question, then turn the answer into a Spec. |
| `research` | Investigate a question against high-trust primary sources and capture findings as Markdown. |
| `retro` | Look at a finished session, apply high-priority changes this repository owns, and summarise the rest. Skills such as `/implement` start this when they finish. |
| `setup` | Choose where the repo's Issues live — local Markdown, GitHub Issues, Jira, or another system — and write the `.agents/refs/tracker.md` file the other skills follow. Then choose which model each pstack role runs on, and whether the SessionStart hook routes tasks; `/setup models` does only that part. |
| `to-spec` | Turn the current conversation into a Spec and write it to the Issue the session started from, or to a new Issue. |
| `triage` | Sort incoming reports, or the Issues nobody has triaged yet, into Specs and parked Issues, one Issue per distinct problem, and close what won't be done. |
| `validate-spec` | Validate a plan or spec against this repo's template rules and codebase; fix stale references in place. |
| `wayfinder` | Plan a huge chunk of work as a map — an Issue whose child tickets are decisions — and resolve them one at a time until its Specs can be written. |
| `wizard` | Generate an interactive bash wizard that walks a person through steps only they can perform. |
| `writing-for-agents` | Reference for writing any document an agent consumes — skills, AGENTS.md, CLAUDE.md. |

## pstack

The plugin includes pstack, Lauren Tan's (poteto) way of working with agents, as ported to Claude Code by Michael Denyer in [pstack-claude](https://github.com/michael-denyer/pstack-claude). Start with `/skills:poteto-mode`, which picks a playbook for the task and runs the other pstack skills as it needs them. `/skills:poteto-help` answers questions about the rest. Its skills are in [`skills/`](skills/), its principles in [`skills/poteto-mode/principles/`](skills/poteto-mode/principles/), next to the ones above, and its agents are in [`agents/`](agents/).

A SessionStart hook tells each new session to use `poteto-mode` for work that touches more than one file, involves a design choice, or chases an unknown bug. To turn it off, or to choose which models pstack's roles use, run `/skills:setup models`. It writes `~/.claude/pstack-models.md`, the same file the separate pstack plugin reads.

**If you installed the separate `pstack` plugin, uninstall it.** With both installed, every pstack skill loads twice and two SessionStart hooks run:

```
/plugin uninstall pstack@pstack-claude
```

pstack's files are this repo's own, to edit like any other ([ADR-0070](docs/adr/0070-pstack-is-imported-then-owned.md)). [`tools/import_pstack.py`](tools/import_pstack.py) copied them from one pstack-claude commit and rewrote them for this plugin. Rerun it to bring in a newer commit: it stops before it writes over a file edited since the last import, and `--force` writes over those edits. [NOTICE-pstack.md](NOTICE-pstack.md) names the upstream commit and the sources.

## Credits

These skills are derived from and inspired by [**Matt Pocock's skills**](https://github.com/mattpocock/skills). Many thanks to Matt for the original work.

[pstack](#pstack) is Lauren Tan's (poteto) [pstack](https://github.com/cursor/plugins/tree/main/pstack), with skills from Cursor's cursor-team-kit and thermos plugins, as ported to Claude Code by Michael Denyer in [pstack-claude](https://github.com/michael-denyer/pstack-claude). Many thanks to both.

## License

[MIT](./LICENSE). pstack keeps its own MIT licenses and copyright notices, listed in [NOTICE-pstack.md](NOTICE-pstack.md).
