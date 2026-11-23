"""Stands in for `claude -p` in the Replay tests; never talks to a model.

A call with --agent is a Replay's session: it echoes its argv, working folder, HEAD and guard environment into the
file FAKE_ARGV_FILE, runs the status line command its --settings names, writes a main transcript where Claude Code
would, and prints stream-json whose init event names the agent and whose result is the report in FAKE_REPORT.
Any other call is the judge: it prints a json result whose text is FAKE_JUDGE_REPLY and whose total_cost_usd is 0.02."""
import json
import os
import subprocess
import sys
from pathlib import Path

args = sys.argv[1:]
value = lambda flag: args[args.index(flag) + 1]

if "--agent" not in args:
    print(json.dumps({"type": "result", "subtype": "success", "is_error": False, "result": os.environ["FAKE_JUDGE_REPLY"],
                      "total_cost_usd": 0.02}))
    sys.exit(0)

session, plugin = value("--session-id"), value("--plugin-dir")
head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
guards = {k: os.environ.get(k) for k in ("SKILLS_BENCHMARK", "BENCH_GUARD_BIN", "GIT_CONFIG_COUNT")}
Path(os.environ["FAKE_ARGV_FILE"]).write_text(json.dumps({"argv": args, "cwd": os.getcwd(), "head": head, "env": guards}), encoding="utf-8")

settings = json.loads(Path(value("--settings")).read_text(encoding="utf-8"))
command = settings["statusLine"]["command"]
for percent in (50, 52):
    subprocess.run(["sh", "-c", command], input=json.dumps({"rate_limits": {"seven_day": {"used_percentage": percent}}}),
                   text=True, capture_output=True)

report = os.environ["FAKE_REPORT"]
usage = {"input_tokens": 100, "output_tokens": 200, "cache_read_input_tokens": 5000, "cache_creation_input_tokens": 3000,
         "cache_creation": {"ephemeral_5m_input_tokens": 1000, "ephemeral_1h_input_tokens": 2000}}
lines = [{"type": "user", "timestamp": "2026-01-01T10:00:00Z", "uuid": "u0", "message": {"role": "user", "content": value("-p")}},
         {"type": "assistant", "timestamp": "2026-01-01T10:00:05Z", "requestId": "req_1", "uuid": "a1",
          "message": {"id": "msg_1", "model": "claude-sonnet-5", "role": "assistant", "content": [{"type": "text", "text": report}],
                      "usage": usage}}]
projects = Path(os.environ["CLAUDE_CONFIG_DIR"]) / "projects" / "p1"
projects.mkdir(parents=True, exist_ok=True)
(projects / f"{session}.jsonl").write_text("\n".join(json.dumps(line) for line in lines) + "\n", encoding="utf-8")
print(json.dumps({"type": "system", "subtype": "init", "agent": value("--agent"), "plugins": [{"name": "skills", "path": plugin}]}))
print(json.dumps({"type": "result", "subtype": "success", "is_error": False, "result": report}))
