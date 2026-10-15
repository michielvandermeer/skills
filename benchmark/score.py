import json
import re
import subprocess
from pathlib import Path

BOOKKEEPING = (".agents/runs/", ".agents/worktrees/")
TEST_FILE_RE = re.compile(r"(^|/)(tests?|__tests__)/|\.(test|spec)\.[jt]sx?$|Tests?\.cs$", re.I)
ASSERT_RE = re.compile(r"\b(Assert\.\w+|Should\w*|Contain\w*|Equal\w*|Matches|expect\(|toBe\w*|toEqual|toContain\w*|toHave\w+|\.Be\()")
MARKUP_RES = [
    re.compile(r"<\/?[A-Za-z][\w:-]*(\s[^<>]*)?\/?>"),
    re.compile(r"\bclass\s*=\s*\\?[\"']"),
    re.compile(r"\b(OuterHtml|InnerHtml|outerHTML|innerHTML|GetAttribute|getAttribute|ClassList|classList|ClassName|className)\b"),
    re.compile(r"\btoHaveClass\b|\btoHaveAttribute\b"),
]
TEXT_SOURCE_RE = re.compile(r"TextContent|InnerText|innerText|textContent|\.Text\b|toHaveText|toContainText|Html\b|\bContent\b|\bBody\b", re.I)
WORDS_LITERAL_RE = re.compile(r"\"[^\"\n]*[A-Za-z]{2,}\s+[A-Za-z]{2,}[^\"\n]*\"")
COUNT_RES = [  # (pattern, groups -> (executed, failed))
    (re.compile(r"Failed:\s*(\d+),\s*Passed:\s*(\d+),\s*Skipped:\s*(\d+),\s*Total:\s*(\d+)"), lambda g: (int(g[0]) + int(g[1]), int(g[0]))),
    (re.compile(r"^\s*total:\s*(\d+)\s*\n\s*failed:\s*(\d+)\s*\n\s*succeeded:\s*(\d+)\s*\n\s*skipped:\s*(\d+)", re.M | re.I), lambda g: (int(g[1]) + int(g[2]), int(g[1]))),
    (re.compile(r"Total:\s*(\d+),\s*Errors:\s*(\d+),\s*Failed:\s*(\d+),\s*Skipped:\s*(\d+)"), lambda g: (int(g[0]) - int(g[3]), int(g[1]) + int(g[2]))),
]


def parse_test_counts(output):
    """(tests executed, tests failed) summed over every summary in a test command's output, or None."""
    executed = failed = matched = 0
    for pattern, counts in COUNT_RES:
        for m in pattern.finditer(output):
            e, f = counts(m.groups())
            executed, failed, matched = executed + e, failed + f, matched + 1
        if matched:
            return executed, failed
    return None


def find_forbidden(diff):
    """Added test lines that assert exact markup or exact content text, as (kind, 'path: line') pairs."""
    hits, path = [], None
    for line in diff.splitlines():
        if line.startswith("+++ "):
            path = line[6:] if line.startswith("+++ b/") else None
        elif path and TEST_FILE_RE.search(path) and line.startswith("+") and ASSERT_RE.search(line):
            code = line[1:].strip()
            if code.startswith(("//", "*", "/*")):
                continue
            if any(r.search(code) for r in MARKUP_RES):
                hits.append(("html", f"{path}: {code[:160]}"))
            elif TEXT_SOURCE_RE.search(code) and WORDS_LITERAL_RE.search(code):
                hits.append(("text", f"{path}: {code[:160]}"))
    return hits


def judge(meta, spec, s, m):
    """(valid, reasons it is invalid, flags that do not invalidate)."""
    reasons, flags = [], []
    if meta.get("timed_out"):
        reasons.append("timed out")
    elif meta.get("exit_code") not in (0, None) or meta.get("result_is_error"):
        reasons.append(f"claude failed (exit {meta.get('exit_code')})")
    if meta.get("plugin_verified") is False:
        reasons.append("the skills under test were not the plugin that loaded")
    if meta.get("plugin_verified") is None:
        flags.append("plugin source unverified")
    if s["landed"] is None:
        reasons.append("worktree gone: landing could not be checked")
    elif not s["landed"]:
        reasons.append("no commit landed")
    if m["subagents"] == 0:
        reasons.append("no subagent ran")
    if m["test_commands"] == 0:
        reasons.append("no test command in the transcript")
    if s["checks_done"] and not s["tests_run"]:
        reasons.append("the Spec's tests ran no tests")
    if not s["checks_done"]:
        flags.append("build and tests not scored")
    if s["blocked_writes"]:
        flags.append(f"{s['blocked_writes']} guard trip(s): the run tried an outward write")
    if m["unpriced_models"]:
        flags.append("priced as Sonnet: " + ", ".join(m["unpriced_models"]))
    return not reasons, reasons, flags


def _git(cwd, *args):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout


def landing_commit(cwd, base, issue):
    """The first commit after base that names the Issue (else the first), and how many commits follow base."""
    log = _git(cwd, "log", "--reverse", "--format=%H%x1f%B%x1e", f"{base}..HEAD")
    commits = [c.strip().split("\x1f") for c in log.split("\x1e") if c.strip()]
    for sha, message in commits:
        if re.search(rf"#{issue}\b", message):
            return sha, len(commits)
    return (commits[0][0] if commits else None), len(commits)


def diff_lines(cwd, base, landing):
    total = 0
    for row in _git(cwd, "diff", "--numstat", base, landing).splitlines():
        added, deleted, path = row.split("\t", 2)
        if not path.startswith(BOOKKEEPING) and added != "-":
            total += int(added) + int(deleted)
    return total


def run_commands(commands, cwd, log_path, timeout):
    """Run each command, keep going after a failure; (every exit code was 0, test counts or None)."""
    ok, outputs = True, []
    with open(log_path, "w", encoding="utf-8") as log:
        for command in commands:
            try:
                r = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", timeout=timeout)
                code, out = r.returncode, r.stdout + r.stderr
            except subprocess.TimeoutExpired:
                code, out = -1, "timed out"
            log.write(f"$ {command}\nexit {code}\n{out}\n")
            ok, outputs = ok and code == 0, outputs + [out]
    return ok, parse_test_counts("\n".join(outputs))


def score_run(run_dir, meta, spec, m, run_checks=True, timeout=3600):
    run_dir, cwd = Path(run_dir), meta.get("worktree")
    s = {"landed": None, "commits": 0, "landing_lines": None, "diff_ratio": None, "build_ok": None, "tests_ok": None,
         "tests_run": None, "tests_failed": None, "forbidden_html": None, "forbidden_text": None,
         "forbidden_samples": [], "checks_done": False}
    if cwd and Path(cwd).exists():
        landing, s["commits"] = landing_commit(cwd, spec["base"], spec["issue"])
        s["landed"] = landing is not None
        if landing:
            s["landing_lines"] = diff_lines(cwd, spec["base"], landing)
            s["diff_ratio"] = round(s["landing_lines"] / spec["landing_lines"], 2)
            hits = find_forbidden(_git(cwd, "diff", "-U0", spec["base"], landing))
            s["forbidden_html"] = sum(k == "html" for k, _ in hits)
            s["forbidden_text"] = sum(k == "text" for k, _ in hits)
            s["forbidden_samples"] = [h for _, h in hits[:5]]
            if run_checks:
                s["build_ok"], _ = run_commands(spec["build"], cwd, run_dir / "score-build.log", timeout)
                s["tests_ok"], counts = run_commands(spec["tests"], cwd, run_dir / "score-tests.log", timeout)
                s["tests_run"], s["tests_failed"] = counts if counts else (0, None)
                s["checks_done"] = True
    log = run_dir / "bench.log"
    text = log.read_text(encoding="utf-8") if log.exists() else ""
    s["blocked_writes"], s["noop_writes"] = text.count(" BLOCKED "), text.count(" NOOP ")
    s["valid"], s["invalid_reasons"], s["flags"] = judge(meta, spec, s, m)
    (run_dir / "score.json").write_text(json.dumps(s, indent=2), encoding="utf-8")
    return s
