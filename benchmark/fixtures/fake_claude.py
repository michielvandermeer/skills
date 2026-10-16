"""Stands in for `claude -p '/implement #N'` in the runner test; never talks to a model.

It does what a run in benchmark mode does (commit a change, bench-log a no-op push), then what a run that
ignored the mode would do (gh write, git push), so the test can see the guards refuse. It then writes a
synthetic transcript where Claude Code would and prints the stream-json events the runner reads."""
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

Path("a.txt").write_text("one\ntwo\nthree\n")
git("add", ".")
git("commit", "-q", "-m", f"Change a (#{issue})")
subprocess.run([shutil.which("bench-log"), "step 4: git push origin main:main"])
subprocess.run([shutil.which("gh"), "issue", "close", issue], capture_output=True)
git("push", "origin", "HEAD")
git("push", os.environ["FAKE_PUSH_TARGET"], "HEAD:refs/heads/leak")

source = Path(__file__).parent / "transcripts"
projects = Path(os.environ["CLAUDE_CONFIG_DIR"]) / "projects" / "p1"
shutil.copytree(source / "sess1", projects / session)
shutil.copy2(source / "sess1.jsonl", projects / f"{session}.jsonl")
print(json.dumps({"type": "system", "subtype": "init", "plugins": [{"name": "skills", "path": plugin}]}))
print(json.dumps({"type": "result", "subtype": "success", "is_error": False}))
