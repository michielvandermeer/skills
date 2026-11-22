"""Sort Claude Code sessions into windows by the plugin cache commits their logs name.

Shared by recount.py and recount_startup.py. A session names a plugin cache commit in any path of the form
plugins/cache/mvdmio/skills/<sha12>/; a commit splits the sessions into those whose SHAs contain it (after) and those
whose SHAs do not (before). Reads <root>/<session>.jsonl and <root>/<session>/subagents/agent-*.jsonl.
Returns counts, dates and SHAs, never log text."""
import functools
import json
import math
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from metrics import _lines, _time

REPO_ROOT = Path(__file__).resolve().parent.parent
CACHE_SHA_RE = re.compile(r"plugins/cache/mvdmio/skills/([0-9a-f]{12})/")


def _before(record, until):
    """False for a record stamped after until; a record with no timestamp stays."""
    return not record.get("timestamp") or _time(record["timestamp"]) <= until


def _iso(moment):
    return datetime.fromtimestamp(moment, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def session_logs(root, session):
    """The top-level log of a session and every sub-agent log, whatever their agent type."""
    return [Path(root) / f"{session}.jsonl", *sorted((Path(root) / session / "subagents").glob("agent-*.jsonl"))]


def read_shas(root, session, until):
    """(plugin cache SHAs, earliest record time) over a session's logs, records up to until."""
    shas, times = set(), []
    for log in filter(Path.exists, session_logs(root, session)):
        for record in (r for r in _lines(log) if _before(r, until)):
            shas.update(CACHE_SHA_RE.findall(json.dumps(record)))
            if record.get("timestamp"):
                times.append(_time(record["timestamp"]))
    return shas, min(times)


@functools.cache
def contains(commit, sha):
    """True when the plugin cache commit sha contains commit, False when not, None when git cannot resolve it."""
    code = subprocess.run(["git", "merge-base", "--is-ancestor", commit, sha], cwd=REPO_ROOT, capture_output=True).returncode
    return {0: True, 1: False}.get(code)


def split_windows(seen, contains, pushed, not_before=-math.inf):
    """({window: {session: payload}}, unresolved SHAs) with window in before, after, mixed, from
    {session: (payload, SHAs, earliest record time)}. contains maps a SHA to True, False or None; an unresolved
    (None) SHA names nothing. A session with no SHA is before when its earliest record is earlier than pushed.
    A session that would be before but whose earliest record is earlier than not_before is in no window."""
    windows = {"before": {}, "after": {}, "mixed": {}}
    unresolved = set()
    for session, (payload, shas, earliest) in seen.items():
        found = {sha: contains(sha) for sha in shas}
        unresolved |= {sha for sha, answer in found.items() if answer is None}
        resolved = set(found.values()) - {None}
        if not resolved:
            name = "before" if earliest < pushed else "after"
        else:
            name = {frozenset({False}): "before", frozenset({True}): "after"}.get(frozenset(resolved), "mixed")
        if name != "before" or earliest >= not_before:
            windows[name][session] = payload
    return windows, unresolved


def commits_in_span(repo, after, until, pathspecs):
    """["sha date subject"] for commits in repo touching pathspecs, committed after `after` up to and including
    `until` (epoch seconds), newest first; None when git cannot read repo. Dates are UTC."""
    if not Path(repo).is_dir():
        return None
    done = subprocess.run(["git", "log", "--format=%h%x09%ct%x09%s", "--", *pathspecs], cwd=repo, capture_output=True, text=True)
    if done.returncode != 0:
        return None
    lines = []
    for row in done.stdout.splitlines():
        sha, stamp, subject = row.split("\t", 2)
        if after < int(stamp) <= until:
            lines.append(f"{sha} {_iso(int(stamp))[:10]} {subject}")
    return lines


def listing(title, lines):
    """The lines of one noise-list section: the title, then its commits, "none" for no commits, or a note that repo could not be read."""
    if lines is None:
        return [f"{title}: could not be read"]
    return [f"{title}:", *(lines or ["none"])]


def named_commit(repo, sha):
    """"sha date subject" of one commit, or None when repo cannot be read or has no such commit."""
    if not Path(repo).is_dir():
        return None
    done = subprocess.run(["git", "log", "-1", "--format=%h%x09%ct%x09%s", sha], cwd=repo, capture_output=True, text=True)
    if done.returncode != 0 or not done.stdout.strip():
        return None
    short, stamp, subject = done.stdout.rstrip("\n").split("\t", 2)
    return f"{short} {_iso(int(stamp))[:10]} {subject}"
