"""Token and cost metrics from the Claude Code JSONL transcripts of one run.

Layout read (what Claude Code writes, copied per run by run.py):
  <dir>/<session>.jsonl                           main session
  <dir>/<session>/subagents/agent-<id>.jsonl      one per subagent, with agent-<id>.meta.json {agentType, description}

An API call is written as several lines (streaming), so calls are deduplicated by message id plus request
id, keeping the largest count of each token type, as ref/token-analysis.md does.
Usage: python metrics.py <transcript-dir>"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# USD per million tokens: input, output, 5-minute cache write, 1-hour cache write, cache read (list prices)
PRICES = {
    "opus": (5.0, 25.0, 6.25, 10.0, 0.50),
    "sonnet": (3.0, 15.0, 3.75, 6.0, 0.30),
    "haiku": (1.0, 5.0, 1.25, 2.0, 0.10),
}
ROLES = ["main", "poteto-agent", "verifier", "interrogate", "arena"]
# A run from before the poteto-mode flow dispatched these agent types; they stay so a baseline run is still attributed.
OLD_ROLES = ("implementer", "checker", "prover", "planner", "fixer")
PREFIXES = {"build:": "poteto-agent", "fix:": "poteto-agent", "verify:": "verifier"}
TEST_RE = re.compile(r"\b(dotnet\s+test|run-tests\.mjs|bun\s+(run\s+)?test|vitest|npm\s+(run\s+)?test|pytest|cargo\s+test|go\s+test)\b")


def family(model):
    for name in PRICES:
        if name in (model or "").lower():
            return name
    return None


def call_cost(model, call):
    prices = PRICES[family(model) or "sonnet"]  # an unknown model is priced as Sonnet and listed in unpriced_models
    amounts = (call["input"], call["output"], call["cache_write_5m"], call["cache_write_1h"], call["cache_read"])
    return sum(n * p for n, p in zip(amounts, prices)) / 1e6


def role_of(agent_type, description=""):
    """The role an implement run dispatched, from the subagent's type and the description the driving session gave it."""
    kind = (agent_type or "unknown").split(":")[-1]
    text = description.lower().strip()
    for prefix, role in PREFIXES.items():
        if text.startswith(prefix):
            return role
    if kind.startswith("poteto-agent"):
        return "poteto-agent"
    if kind in OLD_ROLES:
        return kind
    if "reviewer" in text or "interrogate" in text:
        return "interrogate"
    if "runner" in text or "arena" in text or "candidate" in text:
        return "arena"
    if kind == "general-purpose" and "fix" in text:
        return "fixer"
    return kind


def _lines(path):
    bad = 0
    with open(path, encoding="utf-8") as f:
        for raw in f:
            try:
                yield json.loads(raw)
            except ValueError:
                bad += 1
    if bad:
        yield {"type": "_bad_lines", "count": bad}


def _time(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()


def extract(directory):
    directory = Path(directory)
    files = [(p, "main", "") for p in sorted(directory.glob("*.jsonl"))]
    for p in sorted(directory.glob("*/subagents/agent-*.jsonl")):
        meta_path = p.with_suffix(".meta.json")
        meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        files.append((p, role_of(meta.get("agentType"), meta.get("description", "")), p.stem))

    calls, times = {}, []
    out = {"api_errors": 0, "tool_errors": 0, "test_commands": 0, "bad_lines": 0}
    for path, role, agent in files:
        for o in _lines(path):
            if o.get("type") == "_bad_lines":
                out["bad_lines"] += o["count"]
                continue
            ts = _time(o["timestamp"]) if o.get("timestamp") else None
            if ts:
                times.append(ts)
            message = o.get("message") if isinstance(o.get("message"), dict) else {}
            if o.get("type") == "assistant":
                if o.get("isApiErrorMessage") or o.get("error"):
                    out["api_errors"] += 1
                usage = message.get("usage")
                if usage and message.get("model") != "<synthetic>":
                    _add_call(calls, o, message, usage, role, agent)
            content = message.get("content")
            for block in content if isinstance(content, list) else []:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "tool_result" and block.get("is_error"):
                    out["tool_errors"] += 1
                if block.get("type") == "tool_use" and block.get("name") in ("Bash", "PowerShell"):
                    if TEST_RE.search(str(block.get("input", {}).get("command", ""))):
                        out["test_commands"] += 1
    return _summarise(out, calls.values(), files, times)


def _add_call(calls, o, message, usage, role, agent):
    key = (message.get("id"), o.get("requestId")) if message.get("id") else (o.get("uuid"),)
    created = usage.get("cache_creation") or {}
    write_5m = created.get("ephemeral_5m_input_tokens", usage.get("cache_creation_input_tokens", 0) or 0)
    write_1h = created.get("ephemeral_1h_input_tokens", 0) or 0
    new = {"model": message.get("model", "unknown"), "role": role, "agent": agent,
           "input": usage.get("input_tokens", 0) or 0, "output": usage.get("output_tokens", 0) or 0,
           "cache_write_5m": write_5m, "cache_write_1h": write_1h,
           "cache_read": usage.get("cache_read_input_tokens", 0) or 0}
    old = calls.get(key)
    if old:
        new = {k: max(v, old[k]) if isinstance(v, int) else v for k, v in new.items()}
    calls[key] = new


def _summarise(out, calls, files, times):
    totals = {"input": 0, "cache_write": 0, "cache_read": 0, "output": 0, "cost_usd": 0.0, "max_context": 0, "calls": 0}
    by_model, by_role = {}, {}
    for c in calls:
        cost = call_cost(c["model"], c)
        write = c["cache_write_5m"] + c["cache_write_1h"]
        context = c["input"] + write + c["cache_read"]
        for bucket in (totals, by_model.setdefault(c["model"], _blank()), by_role.setdefault(c["role"], _blank())):
            bucket["input"] += c["input"]
            bucket["cache_write"] += write
            bucket["cache_read"] += c["cache_read"]
            bucket["output"] += c["output"]
            bucket["cost_usd"] += cost
            bucket["max_context"] = max(bucket["max_context"], context)
            bucket["calls"] += 1
        by_role[c["role"]].setdefault("agents", set()).add(c["agent"])
    for role in by_role.values():
        role["agents"] = len(role["agents"])
    out.update(totals)
    out.update(by_model=by_model, by_role=by_role,
               subagents=sum(1 for _, role, _ in files if role != "main"),
               wall_s=round(max(times) - min(times), 1) if times else 0.0,
               unpriced_models=sorted(m for m in by_model if not family(m)))
    return out


def _blank():
    return {"input": 0, "cache_write": 0, "cache_read": 0, "output": 0, "cost_usd": 0.0, "max_context": 0, "calls": 0}


if __name__ == "__main__":
    print(json.dumps(extract(sys.argv[1]), indent=2, sort_keys=True))
