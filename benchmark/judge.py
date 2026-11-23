"""The judge of a Replay (ADR-0086): did the replayed report raise each finding the recorded dispatch raised?

Findings are prose, so a headless `claude -p` call on Sonnet at medium effort compares them and answers one line per
recorded finding. reached() holds the pass rule: the status must equal the recorded one and every recorded finding
must be raised. Extra findings in the Replay do not fail it. A seeded dispatch has no recorded findings; see
seeded_reached()."""
import json
import re
import subprocess

import guards

TIMED_OUT = "the judge timed out"  # the reply text ask() gives when no reply came
LINE_RE = re.compile(r"^\s*(\d+)\s*[:.)\-]\s*(yes|no)\b", re.I | re.M)


def build_prompt(findings, report):
    listed = "\n".join(f"{i}. {f}" for i, f in enumerate(findings, 1))
    return ("A reviewer or verifier reported the findings below on a change. A second run of the same agent wrote the report "
            "below. For each finding, decide whether the second report raises it: the same problem, in any words, at the "
            "same place. A finding the report only mentions in passing as fine, or leaves out, is not raised.\n\n"
            f"Findings:\n{listed}\n\nReport:\n{report}\n\n"
            f"Answer with exactly {len(findings)} line(s), one per finding, in order, each `<number>: yes` or `<number>: no`, "
            "and nothing else.")


def parse_reply(reply, count):
    """[bool] per finding, in order; None unless the reply holds exactly one yes-or-no line for each of 1..count."""
    found = LINE_RE.findall(reply or "")
    if sorted(int(n) for n, _ in found) != list(range(1, count + 1)):
        return None
    answers = {int(n): word.lower() == "yes" for n, word in found}
    return [answers[i] for i in range(1, count + 1)]


def ask(findings, report, claude_cmd, cwd, env, timeout=600):
    """Call the judge: ([raised per finding] or None when the reply is unreadable or never came, cost in USD, the reply text)."""
    argv = [*claude_cmd, "-p", build_prompt(findings, report), "--model", "sonnet", "--effort", "medium",
            "--output-format", "json", "--no-session-persistence", "--strict-mcp-config", "--disallowedTools", *guards.DENIED_TOOLS]
    try:
        r = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired:  # no reply, so no cost is known (a Sonnet session ran up to `timeout`, and left no
        return None, 0.0, TIMED_OUT  # transcript): the Replay fails as one with an unreadable reply, and says the cost is missing
    try:
        event = json.loads(r.stdout)
    except ValueError:
        return None, 0.0, r.stdout
    reply = event.get("result") if isinstance(event, dict) else None
    cost = event.get("total_cost_usd") or 0.0 if isinstance(event, dict) else 0.0
    return parse_reply(reply, len(findings)), cost, reply or ""


def reached(recorded, got, raised):
    """None when the Replay reached the recorded verdict, else why not. raised is the judge's answer per recorded finding
    (None for an unreadable reply), and is read only when there are recorded findings."""
    if got["status"] != recorded["status"]:
        return f"status mismatch: recorded {recorded['status']}, replay {got['status']}"
    if not recorded["findings"]:
        return None
    if raised is None:
        return "the judge's reply was unreadable"
    missed = [f for f, yes in zip(recorded["findings"], raised) if not yes]
    return "missed findings: " + " | ".join(missed) if missed else None


def seeded_reached(got):
    """None when a Replay of the seeded dispatch caught the break: a status other than passed and at least one finding."""
    if got["status"] == "passed":
        return "status passed on the seeded dispatch"
    if not got["findings"]:
        return "no finding on the seeded dispatch"
    return None
