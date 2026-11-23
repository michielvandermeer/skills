"""Seeds a broken Verify dispatch for a Recorded run (ADR-0086): the run's landed change with one needed hunk reverted.

A correct Verifier must reject the seeded commit. The hunk is the first one in a non-test file whose revert makes a
test fail that the run itself added. The commit is kept under refs/recorded/<run id>/seeded in the benchmark's clone.
Seeding can be run again after it stopped partway: it replaces a leftover ref and worktree."""
import re
import shutil
import subprocess
from pathlib import Path

import score

TIMEOUT = 3600
FILE_RE = re.compile(r"^diff --git a/.* b/(.*)$")
FAILED_RE = re.compile(r"^[ \t]*(?:Failed|FAILED|FAIL)\b:?[ \t]+(\S+)", re.M)


class Refused(Exception):
    """The run cannot be seeded: no hunk qualifies, or it has no Verify dispatch."""


def _git(cwd, *args, input=None, check=True):
    r = subprocess.run(["git", "-c", "core.quotepath=false", *args], cwd=cwd, capture_output=True,
                       input=input.encode("utf-8", "surrogateescape") if input is not None else None)
    if check and r.returncode:
        raise SystemExit(f"git {' '.join(args)} failed in {cwd}: {r.stderr.decode('utf-8', 'replace').strip()}")
    return r.stdout.decode("utf-8", "surrogateescape").strip("\r\n") if r.returncode == 0 else None


def landing_diff(clone, base, landed):
    keep = [f":(exclude){p}" for p in score.BOOKKEEPING]
    return _git(clone, "diff", "--no-renames", "--no-ext-diff", "--no-color", "--src-prefix=a/", "--dst-prefix=b/",
                base, landed, "--", ".", *keep) + "\n"


def split_hunks(diff):
    """[{path, test, patch, added}]: one entry per hunk, its patch being the file header and that hunk alone; `added` is
    the added lines of the hunk. A file with no hunk (binary, mode change) has none."""
    hunks, header, path, hunk = [], [], None, None
    for line in diff.splitlines(keepends=True):
        file = FILE_RE.match(line.rstrip("\r\n"))
        if file:
            path, header, hunk = file.group(1), [line], None
        elif line.startswith("@@ ") and path:
            hunk = {"path": path, "test": bool(score.TEST_FILE_RE.search(path)), "head": "".join(header), "lines": [line]}
            hunks.append(hunk)
        elif hunk:
            hunk["lines"].append(line)
        elif path:
            header.append(line)
    return [{"path": h["path"], "test": h["test"], "patch": h["head"] + "".join(h["lines"]),
             "added": "".join(l[1:] for l in h["lines"] if l.startswith("+"))} for h in hunks]


def failing_tests(output):
    """The names after a line that starts with Failed, FAILED or FAIL, in the order they appear."""
    return FAILED_RE.findall(output)


def _added(name, added_text):
    """A failing test counts as added when its name, down to the last `.` or `::`, appears in the added test lines."""
    short = re.split(r"::|\.", re.split(r"[\[(]", name)[0])[-1]
    return bool(short) and re.search(rf"\b{re.escape(short)}\b", added_text) is not None


def _fresh_worktree(clone, path, commit):
    _git(clone, "worktree", "remove", "--force", str(path), check=False)
    shutil.rmtree(path, ignore_errors=True)
    _git(clone, "worktree", "prune")
    _git(clone, "-c", "core.longpaths=true", "worktree", "add", "-q", "--detach", str(path), commit)


def seed(clone, run_id, base, landed, tests, work_dir, log_path):
    """{commit, hunk, failing_test} of the first qualifying hunk, with refs/recorded/<run id>/seeded on its commit."""
    ref = f"refs/recorded/{run_id}/seeded"
    _git(clone, "update-ref", "-d", ref, check=False)
    hunks = split_hunks(landing_diff(clone, base, landed))
    added_tests = "".join(h["added"] for h in hunks if h["test"])
    candidates = [h for h in hunks if not h["test"]]
    if not candidates:
        raise Refused("no hunk of a non-test file landed, so none can be reverted")
    work = Path(work_dir)
    _fresh_worktree(clone, work, landed)
    try:
        for hunk in candidates:
            _git(work, "reset", "-q", "--hard", landed)
            _git(work, "clean", "-q", "-fdx")
            if _git(work, "apply", "-R", "--whitespace=nowarn", "-", input=hunk["patch"], check=False) is None:
                continue  # a hunk that does not revert on its own cannot be the seeded one
            _git(work, "add", "-A")
            _git(work, "-c", "user.name=benchmark", "-c", "user.email=benchmark@localhost", "-c", "commit.gpgsign=false",
                 "commit", "-q", "--no-verify", "-m", f"seed: revert a hunk of {hunk['path']}")
            score.run_commands(tests, work, log_path, TIMEOUT)
            output = Path(log_path).read_text(encoding="utf-8", errors="replace")
            name = next((n for n in failing_tests(output) if _added(n, added_tests)), None)
            if name:
                commit = _git(work, "rev-parse", "HEAD")
                _git(clone, "update-ref", ref, commit)
                return {"commit": commit, "hunk": {"path": hunk["path"], "patch": hunk["patch"]}, "failing_test": name}
    finally:
        _git(clone, "worktree", "remove", "--force", str(work), check=False)
        shutil.rmtree(work, ignore_errors=True)
        _git(clone, "worktree", "prune")
    raise Refused(f"reverting any one of {len(candidates)} non-test hunk(s) fails no test the run added")
