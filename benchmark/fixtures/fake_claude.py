"""Stands in for `claude -p '/implement #N'` in the runner test; never talks to a model.

It does what a run in benchmark mode does (commit a change, bench-log a no-op push), then what a run that
ignored the mode would do (gh write, git push), so the test can see the guards refuse. It then writes a
synthetic transcript where Claude Code would and prints the stream-json events the runner reads.

It also runs the commands its --settings file names, as Claude Code would: the status line command with two
weekly-limit readings, and, when the settings carry a PreToolUse hook (a recorded run), the hook before each of
two Agent calls, with a sub-agent transcript written for each."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

args = sys.argv[1:]
value = lambda flag: args[args.index(flag) + 1]
session, plugin, issue = value("--session-id"), value("--plugin-dir"), value("-p").split("#")[1]
git = lambda *a: subprocess.run(["git", "-c", "user.name=fake", "-c", "user.email=f@f", *a], capture_output=True, text=True)
settings = json.loads(Path(value("--settings")).read_text(encoding="utf-8"))
sh = lambda command, data: subprocess.run(["sh", "-c", command], input=json.dumps(data), text=True, capture_output=True)
status_line = lambda percent: sh(settings["statusLine"]["command"], {"rate_limits": {"seven_day": {"used_percentage": percent}}})
hook = lambda prompt, agent: sh(settings["hooks"]["PreToolUse"][0]["hooks"][0]["command"],
                                {"cwd": os.getcwd(), "tool_name": "Agent", "tool_input": {"subagent_type": agent, "prompt": prompt}})
usage = lambda t: {"input_tokens": t[0], "output_tokens": t[1], "cache_read_input_tokens": t[4], "cache_creation_input_tokens": t[2] + t[3],
                   "cache_creation": {"ephemeral_5m_input_tokens": t[2], "ephemeral_1h_input_tokens": t[3]}}
recording = "hooks" in settings

status_line(40)
if recording:
    hook("Build step 01", "skills:implementer")
Path("a.txt").write_text("one\ntwo\nthree\n")
Path("tests").mkdir(exist_ok=True)
Path("tests/names.txt").write_text("test_a\n")  # the test the run adds, which fixtures/seed_check.py runs
git("add", ".")
git("commit", "-q", "-m", f"Change a (#{issue})")
if recording:
    hook("Verify the run", "skills:verifier")
status_line(43)
subprocess.run([shutil.which("bench-log"), "step 4: git push origin main:main"])
subprocess.run([shutil.which("gh"), "issue", "close", issue], capture_output=True)
git("push", "origin", "HEAD")
git("push", os.environ["FAKE_PUSH_TARGET"], "HEAD:refs/heads/leak")

source = Path(__file__).parent / "transcripts"
projects = Path(os.environ["CLAUDE_CONFIG_DIR"]) / "projects" / "p1"
shutil.copytree(source / "sess1", projects / session)
shutil.copy2(source / "sess1.jsonl", projects / f"{session}.jsonl")
if recording:  # (file, agent type, prompt, model, tokens: input, output, 5-minute write, 1-hour write, read, start, report)
    for name, agent, prompt, model, tokens, start, report in (
            ("rec1", "skills:implementer", "Build step 01", "claude-sonnet-5", (100, 200, 1000, 2000, 5000), "2026-01-01T10:06:00Z",
             "status: done\ndeclined: none\ndeviations: none"),
            ("rec2", "skills:verifier", "Verify the run", "claude-opus-5", (10, 20, 0, 0, 100), "2026-01-01T10:07:00Z",
             "status: failed\ndeviations: none\nfindings:\n- Spec line 2 is missing: no --foo flag\n- test `a` fails: expected 1, got 2\nstop: none")):
        lines = [{"type": "user", "timestamp": start, "uuid": f"{name}u", "message": {"role": "user", "content": prompt}},
                 {"type": "assistant", "timestamp": start, "requestId": f"req_{name}", "uuid": f"{name}a",
                  "message": {"id": f"msg_{name}", "model": model, "role": "assistant", "content": [{"type": "text", "text": report}],
                              "usage": usage(tokens)}}]
        sub = projects / session / "subagents"
        (sub / f"agent-{name}.jsonl").write_text("\n".join(json.dumps(line) for line in lines) + "\n", encoding="utf-8")
        (sub / f"agent-{name}.meta.json").write_text(json.dumps({"agentType": agent, "description": name}), encoding="utf-8")
print(json.dumps({"type": "system", "subtype": "init", "plugins": [{"name": "skills", "path": plugin}]}))
print(json.dumps({"type": "result", "subtype": "success", "is_error": False}))
