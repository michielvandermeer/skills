"""Read the Claude Code logs under a root into /implement runs, for recount_compaction.py: the turns of each Implementer,
Reviewer and Verifier, their Step and Iteration numbers, their compactions, their findings and status as counts, and
how each run ended. Reads <root>/*/<session>.jsonl and <root>/*/<session>/subagents/agent-*.jsonl with the
agent-*.meta.json next to them. read_log returns the prompt and the report text, for the functions that turn them into counts;
every other function returns counts only, never log text."""
import functools
import json
import re
import subprocess
from pathlib import Path

from metrics import _lines, _time, role_of
from plugin_windows import _before
from recount_startup import _report_findings

RUN_TYPES = {f"skills:{role}" for role in ("planner", "implementer", "reviewer", "verifier")}
KEPT_ROLES = {"implementer", "reviewer", "verifier"}  # the sub-agents whose turns a later count reads again
STEP_RE = re.compile(r"Step\s+(\d+)\s+of\s+(\d+)")
ITERATION_RE = re.compile(r"Iteration\s+(\d+)\s*(?:of|/)\s*(\d+)")
# USD per million tokens: input, output, cache read, 5-minute cache write, 1-hour cache write; the baseline's own table
PRICES = {"sonnet": (2, 10, 0.10, 2.50, 4), "opus": (4, 20, 0.20, 5, 8), "haiku": (0.10, 0.50, 0.01, 0.125, 0.20)}
USAGE_FIELDS = ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens",
                "ephemeral_5m_input_tokens", "ephemeral_1h_input_tokens")
LANDING_RE = re.compile(r"git commit")  # also matches git commit-tree
CLOSES_RE = re.compile(r"Closes #(\d+)")
RUN_SLUG_RE = re.compile(r"\.agents/runs/([^/]+)/")  # a run's slug, as a path of its logs names it
CHANGE_TOOLS = ("Edit", "Write", "MultiEdit")
STATUS_RE = re.compile(r"(?im)^\W*status\W*\s*[:=]\s*\W*([a-z_-]+)")


def _prices(model):
    """The PRICES row (input, output, cache read, 5-minute write, 1-hour write per million) of the family named in model;
    a model of no known family costs nothing."""
    return next((p for family, p in PRICES.items() if family in (model or "").lower()), (0,) * 5)


def _cost(model, turn):
    """USD of a turn, priced by its model."""
    prices = _prices(model)
    amounts = (turn["input"], turn["output"], turn["cache_read"], turn["cache_5m"], turn["cache_1h"])
    return sum(n * p for n, p in zip(amounts, prices)) / 1e6


def _turn(usage, model):
    cache_5m, cache_1h = usage["ephemeral_5m_input_tokens"], usage["ephemeral_1h_input_tokens"]
    if not cache_5m and not cache_1h:
        cache_5m = usage["cache_creation_input_tokens"]
    turn = {"model": model, "input": usage["input_tokens"], "output": usage["output_tokens"],
            "cache_read": usage["cache_read_input_tokens"], "cache_5m": cache_5m, "cache_1h": cache_1h}
    turn["context"] = turn["input"] + turn["cache_read"] + cache_5m + cache_1h
    turn["cost"] = _cost(model, turn)
    return turn


def _usage(raw):
    """The usage block flattened: the cache-creation breakdown beside the plain counts, every missing count 0."""
    flat = {**(raw.get("cache_creation") or {}), **raw}
    return {field: flat.get(field) or 0 for field in USAGE_FIELDS}


def _text(record):
    content = (record.get("message") or {}).get("content", "")
    if isinstance(content, str):
        return content
    return "\n".join(b.get("text") or "" for b in content if isinstance(b, dict) and b.get("type") == "text")


def _slug(path):
    """The run slug of the first .agents/runs/<slug>/ in path, else None."""
    found = RUN_SLUG_RE.search(path)
    return found.group(1) if found else None


def _tool_facts(block, facts):
    """Fold one tool_use block into facts: the last landing command's issue, a Halt record write, the last handback message,
    the run slug of the first path naming one, and the Reads each compaction still waiting for a change sees."""
    tool_input = block.get("input") or {}
    path = tool_input.get("file_path") or ""
    facts["slug"] = facts["slug"] or _slug(path)
    if block.get("name") == "Read":
        for compaction in facts["compactions"]:
            if compaction["open"]:
                compaction["reads"].append(Path(path).name)
    elif block.get("name") in CHANGE_TOOLS:
        for compaction in facts["compactions"]:
            compaction["open"] = False
    if block.get("name") == "Bash":
        command = tool_input.get("command") or ""
        closes = CLOSES_RE.findall(command)
        if LANDING_RE.search(command) and closes:
            facts["landed"] = int(closes[-1])
    elif block.get("name") in ("Write", "Edit"):
        facts["halt_record"] |= ".agents/runs/" in path and path.endswith("halt.md")
    elif block.get("name") == "SubagentHandback":
        facts["handback"] = tool_input.get("message") or ""


def read_log(path, until):
    """(turns in order, first prompt text, earliest record time, facts) of one log, records up to until.
    A turn is deduplicated by message id, else requestId, else uuid; duplicates keep the largest of each token
    field, and a <synthetic> record is skipped. facts holds cwd (the first one recorded), landed (the issue number of
    the last landing command, else None), halt_record (a Halt record was written) and report (the message of the last
    SubagentHandback call, else the text blocks of the last message id); the report is read here and only counted later.
    facts also holds slug (the run slug of the first path naming .agents/runs/<slug>/, else None) and compactions, one per
    compact_boundary record in order: before (its preTokens), place (the turns seen before it, so the first turn after it
    is turns[place]), files (basenames the host restored after it), reads (basenames Read before the next Edit, Write or
    MultiEdit) and open (no such change yet)."""
    seen, prompt, first = {}, None, None
    facts, last_id, last_text = {"cwd": None, "landed": None, "halt_record": False, "handback": None,
                                 "slug": None, "compactions": []}, None, []
    for record in (r for r in _lines(path) if _before(r, until)):
        if record.get("timestamp"):
            moment = _time(record["timestamp"])
            first = moment if first is None else min(first, moment)
        message = record.get("message") if isinstance(record.get("message"), dict) else {}
        facts["cwd"] = facts["cwd"] or record.get("cwd")
        if record.get("type") == "assistant":
            if message.get("id") is None or message.get("id") != last_id:
                last_id, last_text = message.get("id"), []
            for block in message.get("content") if isinstance(message.get("content"), list) else []:
                if block.get("type") == "text":
                    last_text.append(block.get("text") or "")
                elif block.get("type") == "tool_use":
                    _tool_facts(block, facts)
        attachment = record.get("attachment") or {}
        if record.get("type") == "system" and record.get("subtype") == "compact_boundary":
            facts["compactions"].append({"before": (record.get("compactMetadata") or {}).get("preTokens") or 0,
                                         "place": len(seen), "files": [], "reads": [], "open": True})
        elif record.get("type") == "attachment" and attachment.get("type") == "compact_file_reference" and facts["compactions"]:
            filename = attachment.get("filename") or ""
            facts["compactions"][-1]["files"].append(Path(filename).name)
            facts["slug"] = facts["slug"] or _slug(filename)
        if record.get("type") == "user" and prompt is None:
            prompt = _text(record)
        elif record.get("type") == "assistant" and message.get("usage") and message.get("model") != "<synthetic>":
            key = message.get("id") or record.get("requestId") or record.get("uuid")
            usage = _usage(message["usage"])
            if key in seen:
                usage = {field: max(usage[field], seen[key][0][field]) for field in USAGE_FIELDS}
            seen[key] = (usage, message.get("model"))
    handback = facts.pop("handback")
    facts["report"] = "\n".join(last_text) if handback is None else handback
    return [_turn(usage, model) for usage, model in seen.values()], prompt or "", first, facts


def _agent(log, agent_type, until):
    """One sub-agent: id, role, model, turns in order, Step (n, of the builder) and Iteration numbers, its report as counts
    and a status (findings, status, blocked), never the text; its run slug; its compactions; and its first record time."""
    turns, prompt, first, facts = read_log(log, until)
    step, iteration = STEP_RE.search(prompt), ITERATION_RE.search(prompt)
    agent = {"id": log.stem.removeprefix("agent-"), "role": role_of(agent_type), "model": turns[0]["model"] if turns else None,
             "turns": turns, "step": int(step.group(1)) if step else None, "steps": int(step.group(2)) if step else None,
             "iteration": int(iteration.group(1)) if iteration else None, "slug": facts["slug"],
             "compactions": _compactions(facts["compactions"], turns, int(step.group(1)) if step else None),
             **_report_facts(facts["report"])}
    return agent, first


def _compactions(raw, turns, step):
    """The compactions of one log as {before, place, after, restored, read_again}: after is the context of the first turn
    after it (None when no turn follows), restored that the host restored the Step file of builder step after it, and
    read_again that the builder Read that file before its next change. A fixer (step None) has neither."""
    step_file = re.compile(rf"0*{step}-.*\.md") if step is not None else None
    has = lambda names: step_file is not None and any(step_file.fullmatch(name) for name in names)
    return [{"before": c["before"], "place": c["place"], "after": turns[c["place"]]["context"] if c["place"] < len(turns) else None,
             "restored": has(c["files"]), "read_again": has(c["reads"])} for c in raw]


def _report_facts(report):
    """findings (Hard violation and Judgement call lines), status (the first status line's value, lowercase) and blocked
    (the first line is a status of blocked) of a report."""
    status, opening = STATUS_RE.search(report), STATUS_RE.match(report.lstrip().split("\n", 1)[0])
    return {"findings": _report_findings(report), "status": status.group(1).lower() if status else None,
            "blocked": bool(opening) and opening.group(1).lower() == "blocked"}


def _existing_ancestor(path):
    """path, or its nearest ancestor that exists: a run worktree is deleted after landing but sits under its repo checkout."""
    path = Path(path)
    while not path.exists() and path != path.parent:
        path = path.parent
    return path


@functools.lru_cache(maxsize=None)
def _commits(directory):
    """[(sha, message)] of every commit on all refs, children before parents, from a read-only git log run in directory;
    None when that is not a repo."""
    try:
        out = subprocess.run(["git", "log", "--all", "--topo-order", "--format=%H%x1f%B%x1e"], cwd=directory,
                             capture_output=True, text=True, errors="replace", check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return [tuple(chunk.strip("\n").split("\x1f", 1)) for chunk in out.split("\x1e") if chunk.strip()]


def landing_state(cwd, issue):
    """"reverted", "kept" or "unread" for the landing commit of Closes #issue in the repo holding cwd. unread: cwd
    was never recorded or no existing ancestor of it is a repo. The landing commit is the latest non-revert commit
    whose message carries Closes #issue as a whole number; a later commit names it in This reverts commit <sha> or
    carries the subject Revert "<its subject>"."""
    commits = _commits(str(_existing_ancestor(cwd))) if cwd else None
    if commits is None:
        return "unread"
    closes = re.compile(rf"Closes #{issue}(?!\d)")
    landing = next((i for i, (_, message) in enumerate(commits) if closes.search(message) and not message.startswith('Revert "')), None)
    if landing is None:
        return "kept"
    sha, message = commits[landing]
    subject = f'Revert "{message.split(chr(10), 1)[0]}"'
    reverted = any(f"This reverts commit {sha}" in other or (i < landing and other.split("\n", 1)[0] == subject)
                   for i, (_, other) in enumerate(commits))
    return "reverted" if reverted else "kept"


def read_run(project, session, log, until):
    """The run of one top-level session log, or None when it has no sub-agent of a run type or no record up to until.
    first is the earliest record over the logs; main_cost and subagent_cost cover every turn, every sub-agent type
    included; agents holds the Implementers, Reviewers and Verifiers. landed is the run's landing: the main session ran
    a landing command (an issue number), halted says it wrote a Halt record and did not land, landing is landing_state
    of a landed run, else None. slug is the first run slug (.agents/runs/<slug>/) a path of the main log, then of each
    sub-agent log in file order, names; a run whose logs name none has its session id."""
    turns, _, first, facts = read_log(log, until)
    times, agents, slugs, run_type, subagent_cost = [first], [], [facts["slug"]], False, 0.0
    for meta in sorted((log.parent / session / "subagents").glob("agent-*.meta.json")):
        agent_type = json.loads(meta.read_text(encoding="utf-8")).get("agentType")
        sub_log = meta.with_name(meta.name.removesuffix(".meta.json") + ".jsonl")
        if not sub_log.exists():
            continue
        agent, moment = _agent(sub_log, agent_type, until)
        times.append(moment)
        slugs.append(agent["slug"])
        subagent_cost += sum(t["cost"] for t in agent["turns"])
        run_type |= agent_type in RUN_TYPES
        if agent["role"] in KEPT_ROLES:
            agents.append(agent)
    times = [t for t in times if t is not None]
    if not run_type or not times:
        return None
    landed = facts["landed"] is not None
    return {"project": project, "session": session, "slug": next((s for s in slugs if s), session), "first": min(times), "main_cost": sum(t["cost"] for t in turns),
            "subagent_cost": subagent_cost, "agents": agents, "landed": landed, "halted": facts["halt_record"] and not landed,
            "landing": landing_state(facts["cwd"], facts["landed"]) if landed else None}


def read_runs(root, until, keep=lambda log: True):
    """Every run under root that keep() accepts by its top-level log path, records up to until, in path order. A log that
    another session deletes during the scan is skipped."""
    runs = []
    for log in sorted(Path(root).glob("*/*.jsonl")):
        try:
            run = read_run(log.parent.name, log.stem, log, until) if keep(log) else None
        except FileNotFoundError:
            continue
        if run:
            runs.append(run)
    return runs
