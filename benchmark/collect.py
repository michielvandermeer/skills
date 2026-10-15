"""One CSV row per run, one CSV per skills commit: benchmark/results/<sha12>.csv.

The CSV is rebuilt from benchmark/runs/*/ (meta.json, score.json, transcripts), so it never holds more than
the runs hold. Usage: python collect.py rebuild <skills-sha-prefix>"""
import csv
import json
import sys
from pathlib import Path

import metrics

HERE = Path(__file__).resolve().parent
ROLE_COLUMNS = metrics.ROLES + list(metrics.PRE_POTETO_ROLES) + ["other"]
COLUMNS = (
    ["run_id", "skills_sha", "spec", "index", "model", "effort", "spec_hash", "claim", "started",
     "valid", "invalid_reasons", "flags", "failed",
     "cost_usd", "tokens_total", "input", "cache_write", "cache_read", "output", "calls", "subagents",
     "wall_s", "max_context", "api_errors", "tool_errors"]
    + [f"cost_{r}" for r in ROLE_COLUMNS] + [f"tokens_{r}" for r in ROLE_COLUMNS]
    + ["landed", "landing_lines", "diff_ratio", "build_ok", "tests_ok", "tests_run",
       "forbidden_html", "forbidden_text", "blocked_writes", "noop_writes", "checks_done"]
)


def row_for(run_dir):
    run_dir = Path(run_dir)
    meta = json.loads((run_dir / "meta.json").read_text(encoding="utf-8"))
    s = json.loads((run_dir / "score.json").read_text(encoding="utf-8"))
    m = metrics.extract(run_dir / "transcripts")
    row = {k: meta.get(k) for k in ("run_id", "skills_sha", "spec", "index", "model", "effort", "spec_hash", "claim", "started")}
    row.update({k: s[k] for k in COLUMNS if k in s})
    row["invalid_reasons"] = "; ".join(s["invalid_reasons"])
    row["flags"] = "; ".join(s["flags"])
    row["failed"] = bool(meta.get("timed_out") or meta.get("exit_code") not in (0, None) or meta.get("result_is_error"))
    tokens = m["input"] + m["cache_write"] + m["cache_read"] + m["output"]
    row.update(cost_usd=round(m["cost_usd"], 4), tokens_total=tokens, calls=m["calls"], subagents=m["subagents"],
               wall_s=m["wall_s"], max_context=m["max_context"], api_errors=m["api_errors"],
               tool_errors=m["tool_errors"], input=m["input"], cache_write=m["cache_write"],
               cache_read=m["cache_read"], output=m["output"])
    for column in ROLE_COLUMNS:
        row[f"cost_{column}"] = row[f"tokens_{column}"] = 0
    for role, b in m["by_role"].items():
        key = role if role in ROLE_COLUMNS else "other"
        row[f"cost_{key}"] = round(row[f"cost_{key}"] + b["cost_usd"], 4)
        row[f"tokens_{key}"] += b["input"] + b["cache_write"] + b["cache_read"] + b["output"]
    return row


def rebuild(skills_sha, runs=None, results=None):
    runs, results = Path(runs or HERE / "runs"), Path(results or HERE / "results")
    rows = []
    for meta_path in sorted(runs.glob("*/meta.json")):
        if json.loads(meta_path.read_text(encoding="utf-8")).get("skills_sha", "").startswith(skills_sha) \
                and (meta_path.parent / "score.json").exists():
            rows.append(row_for(meta_path.parent))
    path = results / f"{skills_sha[:12]}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return path, len(rows)


if __name__ == "__main__" and sys.argv[1:2] == ["rebuild"]:
    print("%s: %d run(s)" % rebuild(sys.argv[2]))
