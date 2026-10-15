"""Import pstack from a pstack-claude checkout into this plugin.

  python tools/import_pstack.py <pstack-claude checkout> <upstream sha>

Copies the Claude Code plugin's skills, agents, and SessionStart hook, drops what only Codex, GitHub Copilot, or Pi
use, and writes NOTICE.md and the upstream licenses. The checkout is read as data: nothing in it is run.

Rerunning over the same upstream changes nothing. Every file this writes is listed in MANIFEST. A later run deletes
only listed files that upstream no longer has, and stops before writing over a file the manifest does not list.
Python 3 standard library only."""
import os
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

RULES = []


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
