"""Import pstack from a pstack-claude checkout into this plugin.

  python tools/import_pstack.py <pstack-claude checkout> <upstream sha>

Copies the Claude Code plugin's skills, agents, and SessionStart hook, drops what only Codex, GitHub Copilot, or Pi
use, and writes NOTICE.md and the upstream licenses. The checkout is read as data: nothing in it is run.

Rerunning over the same upstream changes nothing. tools/pstack-import-manifest.txt lists every file this writes. A
later run deletes only listed files that upstream no longer has, and stops before writing over an unlisted one.
Python 3 standard library only."""
import os
import posixpath
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tools/pstack-import-manifest.txt"
UPSTREAM_URL = "https://github.com/michael-denyer/pstack-claude"
PLUGIN = "plugins/pstack"

# (upstream directory, destination directory, file glob)
TREES = [
    (f"{PLUGIN}/skills", "skills", "**/*"),
    (f"{PLUGIN}/agents", "agents", "*.md"),
    (f"{PLUGIN}/effort-agents", "agents", "*.md"),
]
# The Claude Code SessionStart hook. session-start.ps1 is Codex's Windows entry point, so it stays behind.
HOOKS = ["hooks.json", "session-start.sh", "session-start-context.md"]
LICENSES = {"LICENSE": "LICENSE-pstack", "LICENSE-cursor-team-kit": "LICENSE-cursor-team-kit",
            "LICENSE-thermos": "LICENSE-thermos"}

# Destination paths (files, or directories ending in /) that only Codex, GitHub Copilot, Pi, or the skills-only
# distribution use. Each must match an upstream file, so an upstream rename is caught.
DROP = [
    "skills/poteto-mode/references/codex-tools.md",
    "skills/poteto-mode/references/copilot-tools.md",
    "skills/poteto-mode/references/pi-tools.md",
    "skills/poteto-mode/references/agents/",  # a skills-only copy of agents/comment-sicko.md
    "skills/poteto-mode/references/licenses/",  # the skills-only NOTICE; NOTICE.md and LICENSE-* replace it
    "skills/setup-pstack/copilot.md",
    "skills/setup-pstack/scripts/check-sheet.sh",  # this and the two awk files run only on Copilot's sheet
    "skills/setup-pstack/scripts/check-sheet.awk",
    "skills/setup-pstack/scripts/sheet.awk",
]

EFFORT = [f"skills/{s}/SKILL.md" for s in ("architect", "arena", "how", "interrogate", "poteto-mode", "reflect",
                                            "swarm", "why")]
SETUP = ["skills/setup-pstack/SKILL.md"]
HELP = ["skills/poteto-help/SKILL.md"]
HOOK = ["hooks/session-start.sh"]

# (name, files or None for every imported text file, old, new, old is a regex). Applied in order. Each must match.
RULES = [
    ("namespace pstack: becomes skills:", None, r"\bpstack:(?=[A-Za-z<])", "skills:", True),
    ("Codex platform-mapping line", None,
     "On Codex, read the [platform mapping](../poteto-mode/references/codex-tools.md), including its per-skill notes, "
     "before following this skill.\n\n", "", False),
    ("Copilot platform-mapping line", None,
     "On GitHub Copilot, read the [platform mapping](../poteto-mode/references/copilot-tools.md), including its "
     "per-skill notes, before following this skill.\n\n", "", False),
    ("poteto-mode Platform Adaptation is Claude Code only", ["skills/poteto-mode/SKILL.md"],
     " On Codex, read [`references/codex-tools.md`](references/codex-tools.md) for the Codex equivalent of a Claude "
     "tool, model, or skill named by these workflows. On Pi, read [`references/pi-tools.md`](references/pi-tools.md) "
     "instead. On GitHub Copilot, CLI or app, read [`references/copilot-tools.md`](references/copilot-tools.md) "
     "instead. Other runtimes can discover the same Agent Skills tree, but they must use their own tool, model, and "
     "configuration equivalents. No one of these mappings is a cross-runtime map.", "", False),
    ("Reasoning effort: Codex sentence", EFFORT,
     " On Codex, pass the level as `spawn_agent`'s `reasoning_effort` and keep the usual instructions.", "", False),
    ("Models: upstream generator and per-runtime path", EFFORT,
     "Role defaults, stamped from `plugins/pstack/models.json` (edit there, rerun `tools/generate.mjs`). A matching "
     "role line in the `pstack-models.md` override sheet overrides each at runtime; `/setup-pstack` writes it and "
     "lists its path per runtime.",
     "Role defaults. A matching role line in the `pstack-models.md` override sheet overrides each at runtime; "
     "`/setup-pstack` writes it.", False),

    ("setup-pstack: description", SETUP, "writes the current runtime's override sheet", "writes the override sheet",
     False),
    ("setup-pstack: Copilot setup line", SETUP,
     "On GitHub Copilot, follow [the Copilot setup](copilot.md) in place of steps 1, 3, 4, and 7 and step 6's "
     "header.\n\n", "", False),
    ("setup-pstack: other-runtime line", SETUP,
     "On another runtime, read [Other runtimes](#other-runtimes) below for where the sheet lives and how it loads; "
     "the steps are the same.\n\n", "", False),
    ("setup-pstack: sheet path", SETUP,
     "Write the current runtime's per-role model override sheet, using the path in [Other runtimes](#other-runtimes).",
     "Write the per-role model override sheet, `<config>/pstack-models.md`.", False),
    ("setup-pstack: Codex home", SETUP,
     "The Codex home directory is `$CODEX_HOME` when that variable is set and `~/.codex` otherwise. This skill calls "
     "it `<codex-home>`.\n\n", "", False),
    ("setup-pstack: one sheet", SETUP, "the current runtime's sheet", "the sheet", False),
    ("setup-pstack: hook on Claude Code only", SETUP,
     "On Claude Code and Codex, the plugin's `SessionStart` hook injects the poteto-mode mandate on startup, resume, "
     "clear, and compact. Codex asks the user to trust plugin hooks through `/hooks` before running them. On Pi, the "
     "pstack extension adds the same mandate to the system prompt at every agent start.",
     "The plugin's `SessionStart` hook injects the poteto-mode mandate on startup, resume, clear, and compact.",
     False),
    ("setup-pstack: line inert elsewhere", SETUP, " The line is inert on other runtimes.", "", False),
    ("setup-pstack: Codex effort levels", SETUP,
     " On Codex, the levels are the `reasoning_effort` values your Codex models accept instead.", "", False),
    ("setup-pstack: sheet text names one hook", SETUP,
     "stops the Claude Code or Codex SessionStart hook, or the pstack Pi extension, from injecting",
     "stops the SessionStart hook from injecting", False),
    ("setup-pstack: Codex wiring", SETUP,
     "On Codex, paste the model rows and the `default effort` line into `<codex-home>/AGENTS.md`; Codex has no `@` "
     "include. Do not paste the `session hook` line there: the plugin hook reads it directly from "
     "`<codex-home>/pstack-models.md`.\n\n", "", False),
    ("setup-pstack: Other runtimes section", SETUP, r"(?s)## Other runtimes\n.*?(?=## Models\n)", "", True),
    ("setup-pstack: upstream generator note", SETUP,
     "Stamped from `plugins/pstack/models.json` (edit there, rerun `tools/generate.mjs`).\n\n", "", False),

    ("poteto-help: public copies live in this repo", HELP,
     "`https://github.com/michael-denyer/pstack-claude/blob/main/plugins/pstack/` followed by its path",
     "`https://github.com/michielvandermeer/skills/blob/master/` followed by its path", False),
    ("poteto-help: no platform mappings", HELP, "skills, playbooks, and platform mappings that own",
     "skills and playbooks that own", False),
    ("poteto-help: model questions", HELP,
     "- For model or routing questions, identify the runtime and installation type, then read "
     "[`setup-pstack`](../setup-pstack/SKILL.md#other-runtimes) for the sheet's location and how that runtime "
     "loads it.",
     "- For model or routing questions, read [`setup-pstack`](../setup-pstack/SKILL.md) for the sheet's location and "
     "how it loads.", False),
    ("poteto-help: install", HELP,
     "1. Identify the user's runtime and whether they want a native plugin/package or skills-only installation. Read "
     "its section in the [README](https://github.com/michael-denyer/pstack-claude/blob/main/README.md#install) or "
     "[shared installation reference](https://github.com/michael-denyer/pstack-claude/blob/main/docs/reference.md"
     "#shared-skills-installation), then give the matching install command.",
     "1. pstack ships inside this plugin. Give the install commands from the "
     "[README](https://github.com/michielvandermeer/skills/blob/master/README.md#install).", False),
    ("poteto-help: setup-pstack and the hook", HELP,
     "2. Read [`/setup-pstack`](../setup-pstack/SKILL.md), including its Other runtimes table, before explaining "
     "model choices, effort, sheet loading, or automatic routing. For a bundled routing hook or extension, use its "
     "persistent `session hook: off` setting in the current runtime's sheet to turn routing off.",
     "2. Read [`/setup-pstack`](../setup-pstack/SKILL.md) before explaining model choices, effort, sheet loading, or "
     "automatic routing. The sheet's `session hook: off` line turns the routing hook off.", False),
    ("poteto-help: invocation syntax", HELP,
     " Use the current runtime's invocation syntax from the "
     "[slash-command reference](https://github.com/michael-denyer/pstack-claude/blob/main/docs/reference.md"
     "#slash-commands).", " Skills invoke as `/skills:<name>`.", False),
    ("poteto-help: runtime mappings paragraph", HELP,
     "Before giving runtime-specific instructions or adapting a recipe, read the "
     "[Codex mapping](../poteto-mode/references/codex-tools.md) or [Pi mapping](../poteto-mode/references/pi-tools.md) "
     "when applicable. Their routing sections cover hook trust, extension loading, and skills-only installs. For other "
     "runtimes, use the [runtime support reference](https://github.com/michael-denyer/pstack-claude/blob/main/docs/"
     "reference.md#runtime-support).\n\n", "", False),
    ("poteto-help: subagent defaults", HELP,
     "(../poteto-mode/SKILL.md#subagents) and the current runtime's mapping.", "(../poteto-mode/SKILL.md#subagents).",
     False),
    ("poteto-help: model-choice row", HELP,
     "Read [setup-pstack](../setup-pstack/SKILL.md#other-runtimes) and the current runtime's mapping, then check its "
     "sheet location and loading method.",
     "Read [setup-pstack](../setup-pstack/SKILL.md), then check the sheet's location and how it loads.", False),
    ("poteto-help: principle picker", HELP, "; other runtimes may list them in their skill picker.", ".", False),

    ("session-start.sh: Codex branch", HOOK,
     '  codex)\n    sheet="${CODEX_HOME:-$HOME/.codex}/pstack-models.md"\n'
     '    reader="${CLAUDE_PLUGIN_ROOT}/skills/setup-pstack/scripts/read-sheet.sh"\n    ;;\n', "", False),
    ("session-start.sh: Copilot branch", HOOK,
     '  copilot)\n    sheet="${COPILOT_HOME:-$HOME/.copilot}/pstack-models.md"\n'
     '    reader="${COPILOT_PLUGIN_ROOT}/skills/setup-pstack/scripts/read-sheet.sh"\n    ;;\n', "", False),
    ("session-start.sh: runtime list", HOOK, "(expected claude, codex, or copilot)", "(expected claude)", False),
    ("session-start.sh: Copilot JSON output", HOOK, r"(?s)# GitHub Copilot parses stdout .*?\n  exit 0\nfi\n\n", "",
     True),
    ("session-start.sh: found flag only Copilot read", HOOK,
     'found=0\nif [ -f "$sheet" ] && [ -r "$sheet" ] && normalized=$(sh "$reader" "$sheet"); then\n'
     '  found=1\nelse\n  normalized=\nfi\n',
     'if ! { [ -f "$sheet" ] && [ -r "$sheet" ] && normalized=$(sh "$reader" "$sheet"); }; then\n'
     '  normalized=\nfi\n', False),
]

# Text no imported file may still contain once the rules have run.
LEFTOVERS = [r"\bpstack:(?=[A-Za-z<])", r"(codex|copilot|pi)-tools", "#other-runtimes", "COPILOT_PLUGIN_ROOT",
             "CODEX_HOME", "models\\.json", "tools/generate\\.mjs"]


def fail(message):
    sys.exit(f"import_pstack: {message}")


def checkout_sha(src):
    git = src / ".git"
    if not git.is_dir():
        return None
    head = (git / "HEAD").read_text(encoding="utf-8").strip()
    if not head.startswith("ref: "):
        return head
    ref = head[len("ref: "):]
    if (git / ref).is_file():
        return (git / ref).read_text(encoding="utf-8").strip()
    if (git / "packed-refs").is_file():
        for line in (git / "packed-refs").read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) == 2 and parts[1] == ref:
                return parts[0]
    return None


def read(path):
    """Text comes back LF-normalized as str, so the output does not depend on the checkout's line endings."""
    data = path.read_bytes()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return data
    return data if "\0" in text else text.replace("\r\n", "\n")


def plan_files(src):
    plan, drops_hit = {}, set()
    for upstream, dest_dir, pattern in TREES:
        base = src / upstream
        if not base.is_dir():
            fail(f"{base} is missing")
        for f in sorted(base.glob(pattern)):
            if not f.is_file():
                continue
            dest = f"{dest_dir}/{f.relative_to(base).as_posix()}"
            hits = [d for d in DROP if dest == d or (d.endswith("/") and dest.startswith(d))]
            if hits:
                drops_hit.update(hits)
                continue
            if dest in plan:
                fail(f"two upstream files map to {dest}")
            plan[dest] = read(f)
    for name in HOOKS:
        plan[f"hooks/{name}"] = read(src / PLUGIN / "hooks" / name)
    for upstream, dest in LICENSES.items():
        plan[dest] = read(src / upstream)
    missed = [d for d in DROP if d not in drops_hit]
    if missed:
        fail(f"drop entries match no upstream file: {missed}")
    return plan


def rewrite(plan):
    for name, files, old, new, regex in RULES:
        count = 0
        for dest, content in plan.items():
            if not isinstance(content, str) or (files is not None and dest not in files):
                continue
            content, n = re.subn(old, new, content) if regex else (content.replace(old, new), content.count(old))
            plan[dest], count = content, count + n
        print(f"rule {count:4d}  {name}")
        if count == 0:
            fail(f"rule '{name}' matched nothing; upstream changed, so revisit the rule")


def leftovers(plan):
    """Prose and the hook only: worktree-audit.mjs and find-transcript.mjs also scan Codex and Pi transcripts."""
    return [f"{dest}: {m.group(0)}" for dest, text in sorted(plan.items())
            if isinstance(text, str) and (dest.endswith(".md") or dest.startswith("hooks/"))
            for pattern in LEFTOVERS for m in re.finditer(pattern, text)]


FENCE = re.compile(r"(?ms)^(```|~~~).*?^\1")
LINK = re.compile(r"\[[^\]]*\]\(<?([^)\s>]+)>?\)")


def anchors(text):
    return {re.sub(r"[^\w\- ]", "", h.strip().lower()).replace(" ", "-")
            for h in re.findall(r"(?m)^#{1,6}\s+(.*?)\s*$", FENCE.sub("", text))}


def broken_links(plan):
    """Relative Markdown links in imported files whose file, or heading anchor, exists neither in the import nor here."""
    def text_of(dest):
        if dest in plan:
            return plan[dest]
        return read(ROOT / dest) if (ROOT / dest).is_file() else None

    def exists(dest):
        return dest in plan or (ROOT / dest).exists() or any(key.startswith(dest + "/") for key in plan)

    checked, broken = 0, []
    for dest, text in sorted(plan.items()):
        if not dest.endswith(".md") or not isinstance(text, str):
            continue
        for target in LINK.findall(re.sub(r"`[^`\n]*`", "", FENCE.sub("", text))):
            if re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", target):
                continue
            checked += 1
            path, _, anchor = target.partition("#")
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(dest), path)) if path else dest
            target_text = text_of(resolved) if resolved.endswith(".md") else None
            if not exists(resolved) or (anchor and isinstance(target_text, str) and anchor not in anchors(target_text)):
                broken.append(f"{dest}: {target}")
    return checked, broken


def notice(src, sha):
    rows = [line for line in read(src / "NOTICE.md").splitlines() if line.startswith(f"| `{PLUGIN}/")]
    if not rows:
        fail("found no upstream source rows in NOTICE.md")
    rows = [row.replace(f"`{PLUGIN}/skills/", "`skills/").replace(f"`{PLUGIN}/agents/", "`agents/")
            .replace("[LICENSE](LICENSE)", "[LICENSE-pstack](LICENSE-pstack)") for row in rows]
    if any(f"`{PLUGIN}/" in row for row in rows):
        fail("a NOTICE row names an upstream path this import does not map")
    port = f"[michael-denyer/pstack-claude @ {sha[:7]}]({UPSTREAM_URL}/tree/{sha})"
    return "\n".join([
        "# NOTICE",
        "",
        f"This plugin includes pstack, imported from {port}. pstack is Lauren Tan's (poteto) agent methodology, and "
        "pstack-claude is Michael Denyer's port of it to Claude Code. Both are MIT-licensed. Their copyright notices "
        "and license terms are in [LICENSE-pstack](LICENSE-pstack), [LICENSE-cursor-team-kit](LICENSE-cursor-team-kit), "
        "and [LICENSE-thermos](LICENSE-thermos). The rest of this plugin is under [LICENSE](LICENSE).",
        "",
        "[`tools/import_pstack.py`](tools/import_pstack.py) does the import. It keeps the Claude Code plugin's "
        "skills, agents, and SessionStart hook, leaves out the files only Codex, GitHub Copilot, and Pi use, and "
        "lists every file it leaves out and every rewrite it makes. "
        "[`tools/pstack-import-manifest.txt`](tools/pstack-import-manifest.txt) lists every file it writes.",
        "",
        "## Upstream sources",
        "",
        "| Component | Upstream | Copyright | License | License file |",
        "| --- | --- | --- | --- | --- |",
        *rows,
        f"| Every other file the import writes under `skills/`, `agents/`, and `hooks/`, and the port's changes to "
        f"the rows above | {port} | (c) 2026 Michael Denyer | MIT | [LICENSE-pstack](LICENSE-pstack) |",
        "",
    ])


def owned_conflicts(plan, owned):
    """Paths this run would write that a previous run did not, where this repo already has a file."""
    clashes = [dest for dest in plan if dest not in owned and (ROOT / dest).exists()]
    for skill in sorted({dest.split("/")[1] for dest in plan if dest.startswith("skills/")}):
        clashes += [p.relative_to(ROOT).as_posix() for p in sorted((ROOT / "skills" / skill).rglob("*"))
                    if p.is_file() and p.relative_to(ROOT).as_posix() not in owned]
    return sorted(set(clashes))


def write(dest, content):
    path = ROOT / dest
    data = content.encode("utf-8") if isinstance(content, str) else content
    changed = not path.is_file() or path.read_bytes() != data
    if changed:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    if os.name != "nt":
        path.chmod(0o755 if data.startswith(b"#!") else 0o644)
    return changed


def main(argv):
    if len(argv) != 3:
        sys.exit(__doc__)
    src, sha = Path(argv[1]).resolve(), argv[2].lower()
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        fail(f"'{argv[2]}' is not a full 40-character commit sha")
    head = checkout_sha(src)
    if head is None:
        print(f"cannot read {src}'s HEAD; trusting {sha}")
    elif head != sha:
        fail(f"{src} is at {head}, not {sha}")

    plan = plan_files(src)
    rewrite(plan)
    plan["NOTICE.md"] = notice(src, sha)
    left = leftovers(plan)
    if left:
        fail("text the rules should have removed is still there:\n  " + "\n  ".join(left))
    checked, broken = broken_links(plan)
    print(f"links: {checked} relative links checked, {len(broken)} broken")
    if broken:
        fail("broken relative links:\n  " + "\n  ".join(broken))

    owned = set(MANIFEST.read_text(encoding="utf-8").split()) if MANIFEST.is_file() else set()
    clashes = owned_conflicts(plan, owned)
    if clashes:
        fail("these files belong to this repo, not to a previous import:\n  " + "\n  ".join(clashes))

    stale = sorted(owned - plan.keys())
    for dest in stale:
        path = ROOT / dest
        path.unlink(missing_ok=True)
        for parent in path.parents:
            if parent == ROOT or any(parent.iterdir()):
                break
            parent.rmdir()
    written = sum(write(dest, content) for dest, content in sorted(plan.items()))
    write(MANIFEST.relative_to(ROOT).as_posix(), "".join(f"{dest}\n" for dest in sorted(plan)))
    print(f"{len(plan)} files imported: {written} written, {len(plan) - written} unchanged, {len(stale)} deleted")


if __name__ == "__main__":
    main(sys.argv)
