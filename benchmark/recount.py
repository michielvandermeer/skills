"""Count /implement Implementer sessions in the Claude Code logs of the mvdmio-suite checkout.

No argument: compare the sessions before and after the skills commit 0f8254c reached the plugin cache, with a
two-proportion test on "reached Iteration 2". --triage: the #56 selection, session and Implementer counts only.
Reads <root>/<session>.jsonl, <root>/<session>/subagents/agent-*.meta.json and the agent-*.jsonl next to them.
Prints counts, dates and SHAs, never log text.
Usage: python benchmark/recount.py [log-root]
       python benchmark/recount.py --triage [log-root]"""
import functools
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path

from metrics import _lines, _time
from plugin_windows import REPO_ROOT, _before, _iso, commits_in_span, contains, listing, named_commit, read_shas, split_windows

DEFAULT_ROOT = Path.home() / ".claude" / "projects" / "-home-mvdm-projects-mvdmio-mvdmio-suite"
TRIAGE_MTIME = datetime(2026, 10, 16).timestamp()  # local midnight
TRIAGE_SCAN = _time("2026-11-03T22:32:32Z")  # the #56 scan time
SUITE_ROOT = Path("/home/mvdm/projects/mvdmio/mvdmio-suite")
FIX_SHA = "0f8254c"
FIX_PUSHED = _time("2026-11-04T08:11:29Z")  # the push of 0f8254c; the commit is from 08:11:27Z
SCAN_TIME_ISO = "2026-11-22T05:44:11Z"  # the UTC moment of the first run on the real logs; every window ends here, never changed
SCAN_TIME = _time(SCAN_TIME_ISO)

REPO_NOISE_PATHS = ["skills/implement/", "skills/code-review/", "agents/implementer.md", "agents/planner.md",
                    "agents/reviewer.md", "agents/verifier.md"]
SUITE_NOISE_PATHS = [".agents/refs/coding-standards*.md"]
RESUME_SHA = "69406f0"
RESUME_NOTE = "a resume from a Halt record counts from Iteration 1 again, which moves the Iteration numbers in a prompt"

ITERATION_RE = re.compile(r"Iteration (\d+)")
CAT_RE = re.compile(r"\bcat\b")
CITATION_RE = re.compile(r"coding-standards[\w-]*\.md")


def _prompt(record):
    content = record.get("message", {}).get("content", "")
    return content if isinstance(content, str) else json.dumps(content)


def _touch(block, is_target):
    """None when the tool_use misses the file, else 'whole' or 'parts'."""
    if not is_target(json.dumps(block.get("input", {}))):
        return None
    tool_input = block.get("input", {})
    if block.get("name") == "Read" and "limit" not in tool_input and "offset" not in tool_input:
        return "whole"
    command = str(tool_input.get("command", ""))
    if block.get("name") == "Bash" and CAT_RE.search(command) and "grep" not in command:
        return "whole"
    return "parts"


def _is_standards(text):
    text = text.lower()
    return "coding-standards" in text or "coding_standards" in text


def _is_principles(text):
    return "PRINCIPLES" in text


def _strongest(old, new):
    return "whole" if "whole" in (old, new) else new or old


def read_agent(path, until=math.inf):
    """One Implementer log reduced to the facts the counts need: no prompt, message or tool text is kept.
    Records stamped after until are dropped."""
    prompt, first_ts, standards, principles = None, None, None, None
    for record in (r for r in _lines(path) if _before(r, until)):
        if first_ts is None and record.get("timestamp"):
            first_ts = _time(record["timestamp"])
        if prompt is None and record.get("type") == "user":
            prompt = _prompt(record)
        content = record.get("message", {}).get("content") if isinstance(record.get("message"), dict) else None
        if record.get("type") != "assistant" or not isinstance(content, list):
            continue
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                standards = _strongest(standards, _touch(block, _is_standards))
                principles = _strongest(principles, _touch(block, _is_principles))
    prompt = prompt or ""
    match = ITERATION_RE.search(prompt)
    return {"n": int(match.group(1)) if match else 0, "first_ts": first_ts,
            "names_standards": "coding" in prompt.lower() and "standards" in prompt.lower(),
            "names_principles": "PRINCIPLES" in prompt,
            "hard": "Hard violation" in prompt, "cites": bool(CITATION_RE.search(prompt)),
            "standards": standards, "principles": principles}


def read_sessions(root, keep=lambda path, agent: True, until=math.inf):
    """{session id: [agent record]} for every skills:implementer log under root that keep() accepts."""
    sessions = {}
    for meta_path in sorted(Path(root).glob("*/subagents/agent-*.meta.json")):
        if json.loads(meta_path.read_text(encoding="utf-8")).get("agentType") != "skills:implementer":
            continue
        log = meta_path.with_name(meta_path.name.removesuffix(".meta.json") + ".jsonl")
        agent = read_agent(log, until)
        if keep(log, agent):
            sessions.setdefault(meta_path.parts[-3], []).append(agent)
    return sessions


def count(sessions):
    """The counts for a {session: [agent record]} mapping; a pure function."""
    out = dict.fromkeys(("sessions", "reached_2", "reached_3", "hard_violation", "hard_cites_standards",
                         "first_standards", "first_standards_whole", "first_standards_parts",
                         "first_principles", "first_principles_whole", "first_principles_parts",
                         "first_names_standards", "first_names_principles",
                         "reached_2_with_reader", "reached_2_without_reader", "cites_with_reader"), 0)
    for agents in sessions.values():
        out["sessions"] += 1
        top = max(a["n"] for a in agents)
        out["reached_2"] += top >= 2
        out["reached_3"] += top >= 3
        firsts = [a for a in agents if a["n"] <= 1]
        for a in firsts:
            for kind in ("standards", "principles"):
                if a[kind]:
                    out[f"first_{kind}"] += 1
                    out[f"first_{kind}_{a[kind]}"] += 1
            out["first_names_standards"] += a["names_standards"]
            out["first_names_principles"] += a["names_principles"]
        reader = any(a["standards"] for a in firsts)
        if top >= 2:
            out["reached_2_with_reader" if reader else "reached_2_without_reader"] += 1
        seconds = [a for a in agents if a["n"] == 2]
        if seconds:
            second = max(seconds, key=lambda a: a["first_ts"] or 0)
            if second["hard"]:
                out["hard_violation"] += 1
                out["hard_cites_standards"] += second["cites"]
                out["cites_with_reader"] += second["cites"] and reader
    return out


def triage_sessions(root):
    """The #56 selection: logs with mtime on or after 2026-10-16 local and a first record at or before the #56 scan time."""
    def keep(path, agent):
        return path.stat().st_mtime >= TRIAGE_MTIME and agent["first_ts"] is not None and agent["first_ts"] <= TRIAGE_SCAN
    return read_sessions(root, keep)


def read_windowed(root, until):
    """{session: (agents, cache SHAs, earliest record time)} for sessions with an Implementer, records up to until."""
    sessions = read_sessions(root, lambda path, agent: agent["first_ts"] is not None, until)
    return {session: (agents, *read_shas(root, session, until)) for session, agents in sessions.items()}


contains_fix = functools.partial(contains, FIX_SHA)
split_windows = functools.partial(split_windows, pushed=FIX_PUSHED)


def two_proportion_p(x1, n1, x2, n2):
    """Two-sided p of a pooled two-proportion z-test; 1.0 where a window is empty or the pooled error is zero."""
    if not n1 or not n2:
        return 1.0
    pooled = (x1 + x2) / (n1 + n2)
    error = math.sqrt(pooled * (1 - pooled) * (1 / n1 + 1 / n2))
    if error == 0:
        return 1.0
    return math.erfc(abs(x2 / n2 - x1 / n1) / error / math.sqrt(2))


def compare_rates(x1, n1, x2, n2):
    """(p, dropped): dropped means the second rate is lower and p < 0.05."""
    p = two_proportion_p(x1, n1, x2, n2)
    return p, p < 0.05 and x2 * n1 < x1 * n2


def _rate(x, n):
    return f"{x}/{n} ({x / n:.1%})" if n else f"{x}/{n}"


def window_report(root, scan=SCAN_TIME, contains=contains_fix):
    """The before, after and mixed table, the test on "reached Iteration 2", and the verdict, as text."""
    windows, unresolved = split_windows(read_windowed(root, scan), contains)
    counts = {name: count(sessions) for name, sessions in windows.items()}
    before, after = counts["before"], counts["after"]
    p, dropped = compare_rates(before["reached_2"], before["sessions"], after["reached_2"], after["sessions"])
    lines = [f"windows: before = SHAs without {FIX_SHA}, or none and first record before {_iso(FIX_PUSHED)}; "
             f"after = SHAs with {FIX_SHA}, or none and first record from then; mixed = both; "
             f"all end at scan time {_iso(scan)}; unresolved SHAs {len(unresolved)}",
             f"{'count':<26}{'before':>8}{'after':>8}{'mixed':>8}"]
    lines += [f"{key:<26}" + "".join(f"{counts[name][key]:>8}" for name in windows) for key in before]
    lines += [f"reached Iteration 2: before {_rate(before['reached_2'], before['sessions'])}, "
              f"after {_rate(after['reached_2'], after['sessions'])}, p = {p:.4f}",
              f"verdict: {'dropped' if dropped else 'not dropped'}"]
    return "\n".join(lines)


def noise_report(repo=REPO_ROOT, suite=SUITE_ROOT, after=FIX_PUSHED, until=SCAN_TIME):
    """The other commits in the window that could have moved the Iteration numbers, as text."""
    resume = named_commit(repo, RESUME_SHA) or RESUME_SHA
    return "\n".join([*listing(f"skills commits touching the implement, code-review or agent files, {_iso(after)} to {_iso(until)}",
                               commits_in_span(repo, after, until, REPO_NOISE_PATHS)),
                      f"called out: {resume}: {RESUME_NOTE}",
                      *listing(f"mvdmio-suite commits touching coding-standards files, {_iso(after)} to {_iso(until)}",
                               commits_in_span(suite, after, until, SUITE_NOISE_PATHS))])


def main(argv):
    flags = [a for a in argv if a.startswith("--")]
    args = [a for a in argv if not a.startswith("--")]
    if len(args) > 1 or flags not in ([], ["--triage"]):
        sys.exit(__doc__)
    root = args[0] if args else DEFAULT_ROOT
    if not flags:
        print(window_report(root))
        print(noise_report())
        return
    sessions = triage_sessions(root)
    print(f"sessions {len(sessions)}")
    print(f"implementers {sum(len(a) for a in sessions.values())}")


if __name__ == "__main__":
    main(sys.argv[1:])
