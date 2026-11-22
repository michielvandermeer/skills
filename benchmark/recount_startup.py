"""Count how /implement sub-agents start (Planner, Implementer, Reviewer, Verifier) in the Claude Code logs, before and
after the skills commit 6bd7016 (#60) reached the plugin cache.

No argument: one column each for before, after and mixed, with the first-request size, the skills listing and the tools
of each sub-agent, the session cost, the sessions with more than one Reviewer or Verifier, the Reviewer findings, the
send-backs, and the Skill or Agent calls a sub-agent made without having the tool. Then a one-line verdict (dropped,
not dropped or failed) and a noise list of the other changes that could have moved the numbers. --baseline: the original #62 selection
(sub-agent logs written from 2026-10-31 local, records up to 2026-11-07 local), with no window logic, and its total cost.
A Reviewer's report is the message of its last SubagentHandback call, else the text of its last assistant message; a
finding is a report line that starts with Hard violation or Judgement call. A send-back is an Implementer whose first
prompt names Iteration 2 or later.
Reads <root>/*/<session>.jsonl and <root>/*/<session>/subagents/agent-*.meta.json with the agent-*.jsonl next to them,
for every project directory. Prints counts, dates, SHAs, model names, tool names and roles, never log text.
Usage: python benchmark/recount_startup.py [log-root]
       python benchmark/recount_startup.py --baseline [log-root]"""
import collections
import functools
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path

from metrics import _add_call, _lines, _time, call_cost, role_of
from plugin_windows import REPO_ROOT, _before, _iso, commits_in_span, contains, listing, named_commit, read_shas, session_logs, split_windows
from recount import ITERATION_RE, REPO_NOISE_PATHS, SUITE_ROOT, _prompt

DEFAULT_ROOT = Path.home() / ".claude" / "projects"
FIX_SHA = "6bd7016"
FIX_PUSHED = _time("2026-11-07T01:47:33Z")  # the push of 6bd7016, from this checkout's origin/master reflog
BEFORE_START = datetime(2026, 10, 31).timestamp()  # local midnight; the baseline's own start
BASELINE_END = datetime(2026, 11, 7).timestamp()  # local midnight; stands in for the original scripts' run time
SCAN_TIME_ISO = "2026-11-22T07:52:10Z"  # the UTC moment of the first run on the real logs; every window ends here, never changed
SCAN_TIME = _time(SCAN_TIME_ISO)

ROLES = ["planner", "implementer", "reviewer", "verifier"]
COUNTED_TYPES = {f"skills:{role}" for role in ROLES}
TOKEN_FIELDS = ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")
LOST_TOOLS = ("Skill", "Agent")
# a report line that opens a finding: after whitespace, a list marker (-, * or 1.) and bold markers
FINDING_RE = re.compile(r"^\s*(?:(?:[-*]|\d+\.)\s+)?(?:\*\*)?(Hard violation|Judgement call)")
SUITE_MODELS_PATHS = [".agents/refs/models.md"]
CALLED_OUT = {  # commit in this repo -> why the noise list names it
    "9356c58": "#61 sets the Implementer's compaction window to 200k",
    "0f8254c": "#56, which landed 2026-11-04; the before window spans it"}
TRIAL_SHA = "3ebdf582a"  # in mvdmio-suite
TRIAL_NOTE = "the Sonnet Reviewer trial, 2026-11-06"
PERCENTILE_METHOD = "linear interpolation between closest ranks"


def _report_findings(report):
    """{"Hard violation": n, "Judgement call": m}: the report lines that open a finding."""
    found = collections.Counter(m.group(1) for m in map(FINDING_RE.match, report.splitlines()) if m)
    return {"Hard violation": found["Hard violation"], "Judgement call": found["Judgement call"]}


def _lost_attempts(calls, tools):
    """[(tool, name of the next tool call or None)] for each Skill or Agent call that the tools lack."""
    if tools is None:
        return []
    return [(name, calls[i + 1] if i + 1 < len(calls) else None)
            for i, name in enumerate(calls) if name in LOST_TOOLS and name not in tools]


def read_subagent(path, role, until):
    """One sub-agent log reduced to the facts the counts need; no message, prompt or tool text is kept.
    Records stamped after until are dropped. first_request is None when the log has no assistant record.
    findings counts the Hard violation and Judgement call lines of its report; handback says whether it called
    SubagentHandback; send_back is True when its first prompt names Iteration 2 or later; lost holds one
    (tool, next tool call) per Skill or Agent call that its tools lack."""
    agent = {"role": role, "first_ts": None, "first_request": None, "model": None, "listing": False, "tools": None,
             "findings": None, "handback": False, "send_back": False, "lost": []}
    request, request_id, closed = {}, None, False  # request: the largest count of each token type over the lines of the first request
    prompted, last_id, last_text, handback_message, calls = False, None, [], None, []  # last_text: the text blocks of the last message id
    for record in (r for r in _lines(path) if _before(r, until)):
        if agent["first_ts"] is None and record.get("timestamp"):
            agent["first_ts"] = _time(record["timestamp"])
        kind = record.get("type")
        message = record.get("message") or {}
        if kind == "user" and not prompted:
            prompted = True
            first = ITERATION_RE.search(_prompt(record))
            agent["send_back"] = bool(first) and int(first.group(1)) >= 2
        elif kind == "attachment" and not request and (record.get("attachment") or {}).get("type") == "skill_listing":
            agent["listing"] = True
        elif kind == "api-request-shape" and agent["tools"] is None:
            agent["tools"] = {tool.get("name") for tool in (record.get("shape") or {}).get("tools", [])}
        elif kind == "assistant" and not closed:
            if not request:
                request_id, agent["model"] = message.get("id"), message.get("model")
            elif message.get("id") is None or message.get("id") != request_id:
                closed = True
            if not closed:
                usage = message.get("usage") or {}
                request = {field: max(request.get(field, 0), usage.get(field) or 0) for field in TOKEN_FIELDS}
        if kind == "assistant":
            if message.get("id") is None or message.get("id") != last_id:
                last_id, last_text = message.get("id"), []
            for block in message.get("content") if isinstance(message.get("content"), list) else []:
                if block.get("type") == "text":
                    last_text.append(block.get("text") or "")
                elif block.get("type") == "tool_use":
                    calls.append(block.get("name"))
                    if block.get("name") == "SubagentHandback":
                        handback_message = (block.get("input") or {}).get("message") or ""
    if request:
        agent["first_request"] = sum(request.values())
    agent["handback"] = handback_message is not None
    agent["findings"] = _report_findings("\n".join(last_text) if handback_message is None else handback_message)
    agent["lost"] = _lost_attempts(calls, agent["tools"])
    return agent


def session_cost(project_dir, session, until):
    """USD for every assistant turn in a session's logs, the driving session and each sub-agent of any type,
    records up to until. Turns are deduplicated and priced as metrics.py does; <synthetic> turns are skipped."""
    calls = {}
    for log in filter(Path.exists, session_logs(project_dir, session)):
        for record in (r for r in _lines(log) if _before(r, until)):
            message = record.get("message") if isinstance(record.get("message"), dict) else {}
            if record.get("type") == "assistant" and message.get("usage") and message.get("model") != "<synthetic>":
                _add_call(calls, record, message, message["usage"], None, None)
    return sum(call_cost(call["model"], call) for call in calls.values())


def read_agents(root, until, keep=lambda log: True):
    """{(project, session id): [sub-agent]} for every counted sub-agent log under root that keep() accepts and
    that holds a record up to until. A session with no such sub-agent is not in the result."""
    sessions = {}
    for meta_path in sorted(Path(root).glob("*/*/subagents/agent-*.meta.json")):
        agent_type = json.loads(meta_path.read_text(encoding="utf-8")).get("agentType")
        log = meta_path.with_name(meta_path.name.removesuffix(".meta.json") + ".jsonl")
        if agent_type not in COUNTED_TYPES or not keep(log):
            continue
        agent = read_subagent(log, role_of(agent_type), until)
        if agent["first_ts"] is not None:
            sessions.setdefault(tuple(meta_path.parts[-4:-2]), []).append(agent)
    return sessions


def read_windowed(root, until):
    """{(project, session): ({"agents": [sub-agent], "cost": USD}, cache SHAs, earliest record time)}, records up to until."""
    return {(project, session): ({"agents": agents, "cost": session_cost(Path(root) / project, session, until)},
                                 *read_shas(Path(root) / project, session, until))
            for (project, session), agents in read_agents(root, until).items()}


contains_fix = functools.partial(contains, FIX_SHA)


def percentile(values, q):
    """The q-th (0 to 1) percentile by linear interpolation between closest ranks; None for an empty list."""
    if not values:
        return None
    ordered = sorted(values)
    position = q * (len(ordered) - 1)
    low = math.floor(position)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def _agents(window, role):
    return [a for session in window.values() for a in session["agents"] if role is None or a["role"] == role]


def _share(hits, total):
    return f"{hits}/{total} ({hits / total:.1%})" if total else f"{hits}/{total}"


def _sessions(window, role):
    return str(sum(any(a["role"] == role for a in session["agents"]) for session in window.values()) if role else len(window))


def _subagents(window, role):
    return str(len(_agents(window, role)))


def _quantile(window, role, q):
    return percentile([a["first_request"] for a in _agents(window, role) if a["first_request"] is not None], q)


def _first_request(window, role, q):
    value = _quantile(window, role, q)
    return "-" if value is None else f"{value:.0f}"


def _listing(window, role):
    agents = _agents(window, role)
    return _share(sum(a["listing"] for a in agents), len(agents))


def _has_tool(window, role, tool):
    known = [a for a in _agents(window, role) if a["tools"] is not None]
    return _share(sum(tool in a["tools"] for a in known), len(known))


def _no_shape(window, role):
    return str(sum(a["tools"] is None for a in _agents(window, role)))


def _money(amount):
    return f"${amount:,.2f}"


def _per_session(window, total):
    return "-" if not window else f"{total / len(window):.2f}"


def _cost_mean(window):
    return "-" if not window else _money(sum(s["cost"] for s in window.values()) / len(window))


def _cost_total(window):
    return _money(sum(s["cost"] for s in window.values()))


def _several(window, role):
    return _share(sum(sum(a["role"] == role for a in s["agents"]) > 1 for s in window.values()), len(window))


def _findings(window, kind):
    return sum(a["findings"][kind] for a in _agents(window, "reviewer"))


def _send_backs(window):
    return sum(a["send_back"] for a in _agents(window, "implementer"))


def _lost(window):
    return str(sum(len(a["lost"]) for a in _agents(window, None)))


SCOPES = [("all", None), *((role, role) for role in ROLES)]
# (row name, function of (window) -> cell); a later Step adds rows here
ROWS = [(f"{name} {scope}", functools.partial(fn, role=role))
        for name, fn in (("sessions", _sessions), ("sub-agents", _subagents), ("skills listing", _listing),
                         ("tools with Skill", functools.partial(_has_tool, tool="Skill")),
                         ("tools with Agent", functools.partial(_has_tool, tool="Agent")))
        for scope, role in SCOPES]
ROWS += [(f"first request {label} {role}", functools.partial(_first_request, role=role, q=q))
         for role in ROLES for label, q in (("p50", 0.5), ("p10", 0.1), ("p90", 0.9))]
ROWS.append(("sub-agents without a shape", functools.partial(_no_shape, role=None)))
ROWS += [("session cost mean", _cost_mean), ("session cost total", _cost_total),
         ("sessions with >1 reviewer", functools.partial(_several, role="reviewer")),
         ("sessions with >1 verifier", functools.partial(_several, role="verifier"))]
for finding in ("Hard violation", "Judgement call"):
    ROWS += [(f"{finding}s total", lambda window, finding=finding: str(_findings(window, finding))),
             (f"{finding}s per session", lambda window, finding=finding: _per_session(window, _findings(window, finding)))]
ROWS += [("send-backs total", lambda window: str(_send_backs(window))),
         ("send-backs per session", lambda window: _per_session(window, _send_backs(window))),
         ("lost-tool attempts", _lost)]


def build_table(windows):
    """[(row name, [cell per window])] for {window name: {session: {"agents": [sub-agent], "cost": USD}}}."""
    return [(name, [fn(window) for window in windows.values()]) for name, fn in ROWS]


def attempt_lines(windows):
    """One line per lost-tool attempt: window, role, tool, next tool call; names only."""
    return [f"{name} {a['role']} {tool} next {following or 'none'}"
            for name, window in windows.items() for a in _agents(window, None) for tool, following in a["lost"]]


def windowed_sessions(root, scan, contains):
    """({window: {(project, session): {"agents": [sub-agent], "cost": USD}}}, unresolved SHAs), records up to scan."""
    return split_windows(read_windowed(root, scan), contains, FIX_PUSHED, BEFORE_START)


def window_report(windows, unresolved, scan=SCAN_TIME):
    """The window bounds, the before, after and mixed table, and the lost-tool attempts, as text."""
    lines = [f"windows: before = SHAs without {FIX_SHA}, or none and first record before {_iso(FIX_PUSHED)}, "
             f"first record from {_iso(BEFORE_START)}; after = SHAs with {FIX_SHA}, or none and first record from "
             f"then; mixed = both; all end at scan time {_iso(scan)}; unresolved SHAs {len(unresolved)}",
             f"first request = input + cache read + cache creation tokens of the first API request; "
             f"percentiles by {PERCENTILE_METHOD}; shares of tools leave out sub-agents with no api-request-shape; "
             f"cost = every assistant turn of the session and its sub-agents of any type, priced with metrics.PRICES; "
             f"findings = report lines that start with Hard violation or Judgement call; per session = over the window's sessions",
             f"{'count':<34}" + "".join(f"{name:>22}" for name in windows)]
    lines += [f"{name:<34}" + "".join(f"{cell:>22}" for cell in cells) for name, cells in build_table(windows)]
    lines += ["lost-tool attempts (window, role, tool, next tool call):", *attempt_lines(windows)]
    return "\n".join(lines)


def verdict(before_p10, after_p90, lost_attempts):
    """failed when an after sub-agent made a lost-tool attempt; dropped when, for every role, the after 90th percentile
    of first-request tokens is below the before 10th percentile; not dropped otherwise, a role missing from a window
    (None) and a tie included. before_p10 and after_p90 map each role to its percentile."""
    if lost_attempts:
        return "failed"
    dropped = all(before_p10.get(role) is not None and after_p90.get(role) is not None and after_p90[role] < before_p10[role]
                  for role in ROLES)
    return "dropped" if dropped else "not dropped"


def verdict_report(windows):
    """The verdict line, the before 10th and after 90th percentile per role, and the lost-tool attempt count of the after window."""
    before, after = windows["before"], windows["after"]
    lost = sum(len(a["lost"]) for a in _agents(after, None))
    verdict_word = verdict({role: _quantile(before, role, 0.1) for role in ROLES},
                           {role: _quantile(after, role, 0.9) for role in ROLES}, lost)
    return "\n".join([f"verdict: {verdict_word}",
                      *(f"{role}: before p10 {_first_request(before, role, 0.1)}, after p90 {_first_request(after, role, 0.9)}"
                        for role in ROLES),
                      f"lost-tool attempts in the after window: {lost}"])


def _named(repo, sha, note):
    return f"called out: {named_commit(repo, sha) or sha + ' (not found)'}: {note}"


def noise_report(windows, repo=REPO_ROOT, suite=SUITE_ROOT, scan=SCAN_TIME):
    """The other changes that could have moved the numbers, as text: commits, the Reviewer models and the handback share."""
    models = [f"reviewer models {name}: " + (", ".join(f"{model} {count}" for model, count in sorted(
        collections.Counter(a["model"] or "unknown" for a in _agents(window, "reviewer")).items())) or "none")
        for name, window in windows.items()]
    handbacks = [f"reviewers ending with SubagentHandback {name}: " + _share(sum(a["handback"] for a in _agents(window, "reviewer")),
                                                                              len(_agents(window, "reviewer")))
                 for name, window in windows.items()]
    return "\n".join([
        *listing(f"skills commits touching the implement, code-review or agent files, {_iso(FIX_PUSHED)} to {_iso(scan)}",
                 commits_in_span(repo, FIX_PUSHED, scan, REPO_NOISE_PATHS)),
        *(_named(repo, sha, note) for sha, note in CALLED_OUT.items()),
        *listing(f"mvdmio-suite commits touching the models ref, {_iso(BEFORE_START)} to {_iso(scan)}",
                 commits_in_span(suite, BEFORE_START, scan, SUITE_MODELS_PATHS)),
        _named(suite, TRIAL_SHA, TRIAL_NOTE),
        *models, *handbacks,
        "the Reviewer handback share fell without any commit here; its cause is unknown"])


def baseline_report(root, start=BEFORE_START, end=BASELINE_END):
    """The sessions and sub-agents of the original #62 selection, the median first request, and the cost of every turn over them."""
    sessions = read_agents(root, end, keep=lambda log: log.stat().st_mtime >= start)
    window = {key: {"agents": agents} for key, agents in sessions.items()}
    cost = sum(session_cost(Path(root) / project, session, end) for project, session in sessions)
    return "\n".join([f"baseline: sub-agent logs written from {_iso(start)}, records up to {_iso(end)}",
                      f"sessions {len(sessions)}", f"sub-agents {_subagents(window, None)}",
                      f"median first request {_first_request(window, None, 0.5)}", f"total cost {_money(cost)}"])


def main(argv):
    flags = [a for a in argv if a.startswith("--")]
    args = [a for a in argv if not a.startswith("--")]
    if len(args) > 1 or flags not in ([], ["--baseline"]):
        sys.exit(__doc__)
    root = args[0] if args else DEFAULT_ROOT
    if flags:
        print(baseline_report(root))
        return
    windows, unresolved = windowed_sessions(root, SCAN_TIME, contains_fix)
    print(window_report(windows, unresolved))
    print(verdict_report(windows))
    print(noise_report(windows))


if __name__ == "__main__":
    main(sys.argv[1:])
