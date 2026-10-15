"""Import pstack from pstack-claude into this plugin: a one-way copy at a pinned commit.

  python tools/import_pstack.py <pstack-claude clone> <commit sha> [--force]

Reads plugins/pstack/ and the licenses from the clone's git objects at the commit, so the clone's working tree and
branch do not matter and nothing in the clone is run. Every upstream file is imported, owned here (OWNED), dropped
with a reason (DROP), or outside plugins/pstack/; a file none of those claims stops the run. The imported files are
rewritten for this plugin and Claude Code, and NOTICE-pstack.md credits their sources.

The imported files are this repo's to edit (docs/adr/0070). tools/pstack-import-manifest.txt records the git blob id
of every file the import wrote. A rerun stops before it overwrites or deletes one whose content has changed since,
and names it; --force writes over those edits. It also stops before it writes over a file this repo has that no
import wrote. Rerunning over the same commit changes nothing, and a run that crashed can be rerun. Written files are
staged with the file modes upstream's tree records. Python 3 standard library only."""
import argparse
import fnmatch
import hashlib
import json
import os
import posixpath
import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "tools/pstack-import-manifest.txt"
NOTICE = "NOTICE-pstack.md"
UPSTREAM_URL = "https://github.com/michael-denyer/pstack-claude"
PLUGIN = "plugins/pstack/"

COPY = {"skills/": "skills/", "agents/": "agents/", "effort-agents/": "agents/"}
LICENSES = {"LICENSE": "LICENSE-pstack", "LICENSE-cursor-team-kit": "LICENSE-cursor-team-kit",
            "LICENSE-thermos": "LICENSE-thermos"}
OWNED = ["hooks/hooks.json", "hooks/session-start.sh", "hooks/session-start-context.md", "skills/poteto-help/SKILL.md",
         "skills/setup-pstack/SKILL.md", "skills/setup-pstack/scripts/read-sheet.sh"]
# fnmatch's * also matches /.
DROP = {
    ".claude-plugin/plugin.json": "pstack-claude's manifest. check_plugin_json reads it; this repo has its own",
    ".claude-plugin/icon.png": "pstack-claude's plugin icon",
    ".codex-plugin/*": "Codex only",
    ".github/*": "GitHub Copilot only",
    "pi/*": "the Pi extension",
    "assets/*": "pstack-claude's icon and the prompt that drew it",
    "README.md": "pstack-claude's install guide; this repo's README covers pstack",
    "models.json": "the source upstream's generator stamps into each Models section; the stamped sections come in",
    "hooks/codex-hooks.json": "Codex only",
    "hooks/session-start.ps1": "Codex's Windows entry point",
    "hooks/copilot-*": "GitHub Copilot only",
    "hooks/session-start-copilot*.md": "GitHub Copilot only",
    "hooks/json.awk": "GitHub Copilot only: session-start.sh's Copilot branch",
    "hooks/pre-tool-use.*": "GitHub Copilot only: copilot-hooks.json runs it",
    "hooks/script-contracts.awk": "GitHub Copilot only: pre-tool-use.awk reads it",
    "skills/poteto-mode/references/codex-tools.md": "Codex only",
    "skills/poteto-mode/references/copilot-tools.md": "GitHub Copilot only",
    "skills/poteto-mode/references/pi-tools.md": "Pi only",
    "skills/poteto-mode/references/agents/*": "the skills-only copy of agents/comment-sicko.md",
    "skills/poteto-mode/references/licenses/*": "the skills-only NOTICE; NOTICE-pstack.md and LICENSE-* replace it",
    "skills/setup-pstack/copilot.md": "GitHub Copilot only",
    "skills/setup-pstack/scripts/*sheet.awk": "GitHub Copilot only: check-sheet.sh runs them",
    "skills/setup-pstack/scripts/check-sheet.sh": "GitHub Copilot only: it checks Copilot's sheet",
    "*.test.ts": "upstream's tests",
    "*.test-helper.ts": "upstream's tests",
    "skills/poteto-mode/scripts/watch-pr/live-merge-safety.mjs": "an opt-in live test that no imported file runs",
}

PLUGIN_JSON_KEYS = {"name", "displayName", "version", "description", "author", "homepage", "repository", "license",
                    "keywords", "agents"}

EFFORT = ("architect", "arena", "how", "interrogate", "poteto-mode", "reflect", "swarm", "why")

class Rule(NamedTuple):
    name: str
    files: dict | None
    old: str
    new: str
    regex: bool


RULES = [
    Rule("namespace pstack: becomes skills:", None, r"\bpstack:(?=[A-Za-z<])", "skills:", True),
    Rule("Codex platform-mapping line", None,
     "On Codex, read the [platform mapping](../poteto-mode/references/codex-tools.md), including its per-skill notes, "
     "before following this skill.\n\n", "", False),
    Rule("Copilot platform-mapping line", None,
     "On GitHub Copilot, read the [platform mapping](../poteto-mode/references/copilot-tools.md), including its "
     "per-skill notes, before following this skill.\n\n", "", False),
    Rule("poteto-mode: Platform Adaptation folds into the opening paragraph", {"skills/poteto-mode/SKILL.md": 1},
     "\n\n## Platform Adaptation\n\nThese skills use Claude Code tool names (the `Skill` tool, the `Agent` tool, "
     "`AskUserQuestion`) and the Claude model names the `Agent` tool accepts, as each Models section lists them. On "
     "Claude Code they work as written. On Codex, read [`references/codex-tools.md`](references/codex-tools.md) for "
     "the Codex equivalent of a Claude tool, model, or skill named by these workflows. On Pi, read "
     "[`references/pi-tools.md`](references/pi-tools.md) instead. On GitHub Copilot, CLI or app, read "
     "[`references/copilot-tools.md`](references/copilot-tools.md) instead. Other runtimes can discover the same "
     "Agent Skills tree, but they must use their own tool, model, and configuration equivalents. No one of these "
     "mappings is a cross-runtime map.",
     " These skills use Claude Code tool names (the `Skill` tool, the `Agent` tool, `AskUserQuestion`) and the Claude "
     "model names the `Agent` tool accepts, as each Models section lists them.", False),
    Rule("Reasoning effort: Codex sentence", {f"skills/{s}/SKILL.md": 1 for s in EFFORT},
     " On Codex, pass the level as `spawn_agent`'s `reasoning_effort` and keep the usual instructions.", "", False),
    Rule("Models: upstream generator and per-runtime path", {f"skills/{s}/SKILL.md": 1 for s in EFFORT if s != "interrogate"},
     "Role defaults, stamped from `plugins/pstack/models.json` (edit there, rerun `tools/generate.mjs`). A matching "
     "role line in the `pstack-models.md` override sheet overrides each at runtime; `/setup-pstack` writes it and "
     "lists its path per runtime.",
     "Role defaults. A matching role line in the `pstack-models.md` override sheet overrides each at runtime; "
     "`/setup-pstack` writes it.", False),
    Rule("resume-storage: one runtime", {"skills/poteto-mode/references/resume-storage.md": 1},
     "Claude Code, Codex, and other runtimes use this same command and location. Runtime-specific home directories "
     "and transcript encodings do not affect lookup.",
     "The lookup does not depend on Claude Code's config directory or transcript encoding.", False),
]

LEFTOVERS = [r"\bpstack:(?=[A-Za-z<])", r"(codex|copilot|pi)-tools", "#other-runtimes", "COPILOT_PLUGIN_ROOT",
             "CODEX_HOME", r"models\.json", r"tools/generate\.mjs", r"\b(Codex|Copilot|spawn_agent)\b|\bOn Pi\b"]
LEFTOVERS_ALLOWED = {
    "skills/reflect/scripts/find-transcript.mjs":
        "tells Claude Code, Pi, and Copilot transcripts apart, and refuses a Codex rollout by name",
    "skills/poteto-mode/scripts/worktree-audit.mjs":
        "scans Claude Code's, Codex's, and Pi's session stores for the last chat that used each worktree",
}


def fail(message):
    sys.exit(f"import_pstack: {message}")


def run(argv, cwd, data=None):
    r = subprocess.run(argv, cwd=cwd, input=data, capture_output=True)
    if r.returncode:
        fail(f"{' '.join(argv)} failed: {r.stderr.decode('utf-8', 'replace').strip()}")
    return r.stdout


def matches(path, glob):
    return fnmatch.fnmatchcase(path, glob)


def dest_of(rel):
    return next((COPY[d] + rel[len(d):] for d in COPY if rel.startswith(d)), None)


def as_text(data):
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return None
    return None if "\0" in text else text


class UpstreamFile(NamedTuple):
    mode: str
    data: bytes


def blob_id(data):
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def read_upstream(src, sha):
    if subprocess.run(["git", "-C", str(src), "cat-file", "-e", f"{sha}^{{commit}}"], capture_output=True).returncode:
        fail(f"{src} has no commit {sha}")
    entries = {}
    for entry in run(["git", "-C", str(src), "ls-tree", "-r", "-z", sha], ROOT).split(b"\0"):
        if not entry:
            continue
        meta, path = entry.split(b"\t", 1)
        mode, kind, blob = meta.decode().split()
        if kind != "blob" or mode not in ("100644", "100755"):
            fail(f"upstream {path.decode()} is a {kind} with mode {mode}; the import copies regular files only")
        entries[path.decode("utf-8")] = (mode, blob)
    blobs = sorted({blob for _, blob in entries.values()})
    out, pos, data = run(["git", "-C", str(src), "cat-file", "--batch"], ROOT, "".join(f"{b}\n" for b in blobs).encode()), 0, {}
    for blob in blobs:
        header_end = out.index(b"\n", pos)
        size = int(out[pos:header_end].split()[2])
        data[blob] = out[header_end + 1:header_end + 1 + size]
        pos = header_end + 2 + size
    return {path: UpstreamFile(mode, data[blob]) for path, (mode, blob) in entries.items()}


def classify(upstream):
    plan, executables, hits = {}, set(), set()
    counts = {"imported": 0, "owned here": 0, "dropped": 0, "outside plugins/pstack/": 0}
    for path, file in sorted(upstream.items()):
        if path in LICENSES:
            dest = LICENSES[path]
        elif not path.startswith(PLUGIN):
            counts["outside plugins/pstack/"] += 1
            continue
        else:
            rel = path[len(PLUGIN):]
            if rel in OWNED:
                hits.add(rel)
                counts["owned here"] += 1
                continue
            drop = next((glob for glob in DROP if matches(rel, glob)), None)
            if drop:
                hits.add(drop)
                counts["dropped"] += 1
                continue
            dest = dest_of(rel)
            if dest is None:
                fail(f"upstream {path} is not imported, owned, or dropped; add it to COPY, OWNED, or DROP")
        if dest in plan:
            fail(f"two upstream files map to {dest}")
        plan[dest] = file.data
        if file.mode == "100755":
            executables.add(dest)
        counts["imported"] += 1
    unused = [entry for entry in [*OWNED, *DROP] if entry not in hits]
    if unused:
        fail(f"OWNED or DROP entries match no upstream file: {unused}")
    return plan, executables, counts


def check_plugin_json(data, plan):
    meta = json.loads(data)
    unknown = sorted(set(meta) - PLUGIN_JSON_KEYS)
    if unknown:
        fail(f"upstream plugin.json has keys the import does not handle: {unknown}")
    listed = set()
    for agent in meta.get("agents", []):
        rel = agent.removeprefix("./")
        if not rel.endswith(".md") or "/" in rel.partition("/")[2] or dest_of(rel) not in plan:
            fail(f"upstream plugin.json lists agent {agent}, which the import does not bring in")
        listed.add(dest_of(rel))
    copied = {dest for dest in plan if dest.startswith("agents/")}
    if listed != copied:
        fail(f"agents copied but not in upstream plugin.json: {sorted(copied - listed)}; "
             f"listed but not copied: {sorted(listed - copied)}")


def rewrite(plan):
    licenses = set(LICENSES.values())
    for rule in RULES:
        counts = {}
        for dest in rule.files or sorted(plan):
            content = as_text(plan[dest]) if dest in plan else None
            if content is None or dest in licenses:
                continue
            if rule.regex:
                content, n = re.subn(rule.old, rule.new, content)
            else:
                content, n = content.replace(rule.old, rule.new), content.count(rule.old)
            plan[dest] = content.encode("utf-8")
            if n:
                counts[dest] = n
        print(f"rule {sum(counts.values()):4d}  {rule.name}")
        if rule.files is None and not counts:
            fail(f"rule '{rule.name}' matched nothing; upstream changed, so revisit the rule")
        if rule.files is not None and counts != rule.files:
            fail(f"rule '{rule.name}' matched {counts}, expected {rule.files}; upstream changed, so revisit the rule")


def check_licenses(plan, upstream):
    for path, dest in LICENSES.items():
        if plan[dest] != upstream[path].data:
            fail(f"{dest} differs from upstream {path}")


def leftovers(plan):
    missing = [dest for dest in LEFTOVERS_ALLOWED if dest not in plan]
    if missing:
        fail(f"LEFTOVERS_ALLOWED names files the import does not write: {missing}")
    texts = {dest: as_text(data) for dest, data in sorted(plan.items()) if dest not in LEFTOVERS_ALLOWED}
    return [f"{dest}: {m.group(0)}" for dest, text in texts.items() if text is not None
            for pattern in LEFTOVERS for m in re.finditer(pattern, text)]


FENCE = re.compile(r"(?ms)^(```|~~~).*?^\1")
LINK = re.compile(r"\[[^\]]*\]\(<?([^)\s>]+)>?\)")


def anchors(text):
    return {re.sub(r"[^\w\- ]", "", h.strip().lower()).replace(" ", "-")
            for h in re.findall(r"(?m)^#{1,6}\s+(.*?)\s*$", FENCE.sub("", text))}


def broken_links(plan):
    def text_of(dest):
        if dest in plan:
            return as_text(plan[dest])
        return as_text((ROOT / dest).read_bytes()) if (ROOT / dest).is_file() else None

    def exists(dest):
        return dest in plan or (ROOT / dest).exists() or any(key.startswith(dest + "/") for key in plan)

    checked, broken = 0, []
    for dest in sorted({*plan, *OWNED}):
        text = text_of(dest)
        if not dest.endswith(".md") or text is None:
            continue
        for target in LINK.findall(re.sub(r"`[^`\n]*`", "", FENCE.sub("", text))):
            if re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", target):
                continue
            checked += 1
            path, _, anchor = target.partition("#")
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(dest), path)) if path else dest
            target_text = text_of(resolved) if resolved.endswith(".md") else None
            if not exists(resolved) or (anchor and target_text is not None and anchor not in anchors(target_text)):
                broken.append(f"{dest}: {target}")
    return checked, broken


def expand_braces(path):
    m = re.search(r"\{([^}]*)\}", path)
    return [p for alt in m.group(1).split(",") for p in expand_braces(path[:m.start()] + alt + path[m.end():])] \
        if m else [path]


def notice_row(row, here):
    cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
    if len(cells) != 5:
        fail(f"upstream NOTICE row does not have 5 cells: {row}")
    component, source, holder, kind, license_file = cells
    for path in re.findall(r"`([^`]+)`", component):
        dest = dest_of(path.removeprefix(PLUGIN)) if path.startswith(PLUGIN) else None
        globs = [p + "*" if p.endswith("/") else p for p in expand_braces(dest or "")]
        if dest is None or not all(any(matches(h, g) for h in here) for g in globs):
            fail(f"upstream NOTICE names {path}, which the import does not bring in")
        component = component.replace(f"`{path}`", f"`{dest}`")
    link = re.fullmatch(r"\[([^\]]+)\]\(([^)]+)\)", license_file)
    if not link or link.group(1) != link.group(2) or link.group(2) not in LICENSES:
        fail(f"upstream NOTICE row's license file is not one the import copies: {license_file}")
    license_file = f"[{LICENSES[link.group(2)]}]({LICENSES[link.group(2)]})"
    return f"| {component} | {source} | {holder} | {kind} | {license_file} |"


def notice(upstream_notice, sha, plan):
    lines = upstream_notice.splitlines()
    if "## Upstream sources" not in lines:
        fail("upstream NOTICE.md has no '## Upstream sources' section")
    table = []
    for line in lines[lines.index("## Upstream sources") + 1:]:
        if line.startswith("#"):
            break
        if line.startswith("|"):
            table.append(line)
    if len(table) < 3 or not table[0].startswith("| Component |") or not set(table[1]) <= set("|- "):
        fail("upstream NOTICE.md's Upstream sources table changed shape")
    here = {*plan, *OWNED}
    rows = [notice_row(row, here) for row in table[2:]]
    port = f"[michael-denyer/pstack-claude @ {sha[:7]}]({UPSTREAM_URL}/tree/{sha})"
    return "\n".join([
        "# NOTICE: pstack",
        "",
        f"This plugin includes pstack, imported from {port}. pstack is Lauren Tan's (poteto) agent methodology, and "
        "pstack-claude is Michael Denyer's port of it to Claude Code. Both are MIT-licensed. Their copyright notices "
        "and license terms are in [LICENSE-pstack](LICENSE-pstack), [LICENSE-cursor-team-kit](LICENSE-cursor-team-kit), "
        "and [LICENSE-thermos](LICENSE-thermos).",
        "",
        "[`tools/import_pstack.py`](tools/import_pstack.py) wrote this file and every file listed in "
        "[`tools/pstack-import-manifest.txt`](tools/pstack-import-manifest.txt). These began as pstack-claude's files "
        "and are now this repo's own: " + ", ".join(f"`{path}`" for path in OWNED) + ".",
        "",
        "## Upstream sources",
        "",
        table[0],
        table[1],
        *rows,
        f"| Every other file under `skills/` and `agents/` that the import writes, the upstream versions of this repo's "
        f"own files named above, and the port's changes to the rows above | {port} | (c) 2026 Michael Denyer | MIT | "
        f"[LICENSE-pstack](LICENSE-pstack) |",
        "",
    ])


def read_manifest():
    path = ROOT / MANIFEST
    if not path.is_file():
        return {}
    return {dest: blob for blob, dest in (line.split(None, 1) for line in path.read_text(encoding="utf-8").splitlines())}


def local_ids(paths):
    present = sorted(p for p in paths if (ROOT / p).is_file())
    out = run(["git", "hash-object", "--stdin-paths"], ROOT, "".join(f"{p}\n" for p in present).encode())
    return dict(zip(present, out.decode().split()))


def git_paths(argv, paths):
    if paths:
        run(["git", *argv, "--pathspec-from-file=-", "--pathspec-file-nul"], ROOT,
            "".join(f"{p}\0" for p in sorted(paths)).encode())


def differs_from_last_import_and_this_one(previous, here, planned):
    return sorted(p for p, blob in previous.items() if p not in OWNED and here.get(p) not in (blob, planned.get(p)))


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("src", type=Path, help="a pstack-claude clone; only its git objects are read")
    parser.add_argument("sha", help="the full 40-character commit to import")
    parser.add_argument("--force", action="store_true", help="write over imported files edited since the last import")
    a = parser.parse_args(argv[1:])
    sha = a.sha.lower()
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        fail(f"'{a.sha}' is not a full 40-character commit sha")

    upstream = read_upstream(a.src.resolve(), sha)
    plan, executables, counts = classify(upstream)
    print("upstream: " + ", ".join(f"{n} {kind}" for kind, n in counts.items()))
    check_plugin_json(upstream[f"{PLUGIN}.claude-plugin/plugin.json"].data, plan)
    rewrite(plan)
    check_licenses(plan, upstream)
    left = leftovers(plan)
    if left:
        fail("text the rules should have removed is still there:\n  " + "\n  ".join(left))
    if "NOTICE.md" not in upstream:
        fail("upstream has no NOTICE.md")
    plan[NOTICE] = notice(upstream["NOTICE.md"].data.decode("utf-8"), sha, plan).encode("utf-8")
    checked, broken = broken_links(plan)
    print(f"links: {checked} relative links checked, {len(broken)} broken")
    if broken:
        fail("broken relative links:\n  " + "\n  ".join(broken))

    previous = read_manifest()
    planned = {dest: blob_id(content) for dest, content in plan.items()}
    here = local_ids({*previous, *plan})
    edited = differs_from_last_import_and_this_one(previous, here, planned)
    if edited and not a.force:
        fail("edited since import, so not overwritten or deleted; rerun with --force to write over them:\n  "
             + "\n  ".join(edited))
    tracked = set(run(["git", "ls-files", "-z"], ROOT).decode("utf-8").split("\0"))
    skills = {dest.split("/")[1] for dest in plan if dest.startswith("skills/")}
    clashes = sorted({*(d for d in plan if d not in previous and d in here and here[d] != planned[d]),
                      *(p for p in tracked if p.startswith("skills/") and p.split("/")[1] in skills
                        and p not in previous and p not in plan and p not in OWNED)})
    if clashes:
        fail("these files belong to this repo, not to an import:\n  " + "\n  ".join(clashes))

    stale = sorted(p for p in previous if p not in plan and p not in OWNED)
    for dest in stale:
        path = ROOT / dest
        path.unlink(missing_ok=True)
        for parent in path.parents:
            if parent == ROOT or any(parent.iterdir()):
                break
            parent.rmdir()
    written = 0
    for dest, content in sorted(plan.items()):
        path = ROOT / dest
        if here.get(dest) != planned[dest]:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            written += 1
        path.chmod(0o755 if dest in executables else 0o644)
    manifest = ROOT / MANIFEST
    manifest.with_suffix(".tmp").write_text("".join(f"{planned[d]}  {d}\n" for d in sorted(plan)), encoding="utf-8",
                                            newline="\n")
    os.replace(manifest.with_suffix(".tmp"), manifest)
    git_paths(["rm", "--quiet", "--cached", "--ignore-unmatch"], stale)
    git_paths(["add", "--chmod=+x"], executables)
    git_paths(["add", "--chmod=-x"], [*(set(plan) - executables), MANIFEST])
    print(f"{len(plan)} files imported: {written} written, {len(plan) - written} unchanged, {len(stale)} deleted"
          + (f", {len(edited)} edits overwritten" if edited else ""))


if __name__ == "__main__":
    main(sys.argv)
