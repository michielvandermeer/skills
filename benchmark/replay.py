"""Reruns one dispatch of a Recorded run under the skills in a checkout, and says what it cost and whether it reached the
recorded verdict (ADR-0086).

  python benchmark/replay.py <recorded-run> <dispatch> --skills <checkout>

<recorded-run> is a run id under benchmark/work/recorded/, or the path of its folder. <dispatch> is a dispatch's number
in recorded.json, or `seeded`. <checkout> is a skills directory and may hold uncommitted changes.

The Replay runs `claude -p` with the recorded prompt, as the dispatch's plugin agent, in a worktree of the benchmark
clone at the dispatch's recorded commit, under every guard a full run has (run.py). Its model and effort come from the
checkout's agents/<role>.md header. Exit code 0 when it passed, 1 when it failed, 2 when it could not run."""
import argparse
import json
import re
import shutil
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import judge
import metrics
import record
import run
import usage_share


def agent_header(checkout, role):
    """(model, effort) from the front matter of <checkout>/agents/<role>.md; SystemExit when the file or a value is missing."""
    path = Path(checkout) / "agents" / f"{role}.md"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        raise SystemExit(f"{path} does not exist: the Replay would run the {role} agent on an unknown model and effort")
    header = re.match(r"---\r?\n(.*?)\r?\n---", text, re.S)
    values = dict(re.findall(r"^(model|effort):[ \t]*(\S+)", header.group(1) if header else "", re.M))
    missing = [key for key in ("model", "effort") if key not in values]
    if missing:
        raise SystemExit(f"{path} has no {' or '.join(missing)} in its header: the Replay would not know what to run it on")
    return values["model"], values["effort"]


def load_dispatch(recorded_arg, dispatch_arg):
    """(recorded run folder, recorded.json, the dispatch row); SystemExit when the Replay has nothing recorded to compare with."""
    folder = Path(recorded_arg)
    if not (folder / "recorded.json").is_file():
        folder = run.HERE / "work" / "recorded" / recorded_arg
    try:
        recorded = json.loads((folder / "recorded.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise SystemExit(f"no recorded.json under {folder}")
    if dispatch_arg == "seeded":
        dispatch = recorded.get("seeded_dispatch")
    else:
        dispatch = next((d for d in recorded["dispatches"] if str(d["n"]) == dispatch_arg), None)
        if dispatch and dispatch["verdict"] is None:
            raise SystemExit(f"dispatch {dispatch_arg} of {recorded['run_id']} has no recorded verdict: no sub-agent transcript matched it")
    if not dispatch:
        raise SystemExit(f"{recorded['run_id']} has no dispatch {dispatch_arg}")
    return folder, recorded, dispatch


def session_cost(m):
    """The list-price cost of a session, by model and token kind as a recorded dispatch's is."""
    by_model = {}
    for models in m["by_agent"].values():
        for model, spent in models.items():
            total = by_model.setdefault(model, dict.fromkeys((*metrics.TOKEN_KINDS, "cost_usd"), 0))
            for key in total:
                total[key] += spent[key]
    return {"cost_usd": m["cost_usd"], "by_model": by_model}


def replay(recorded_arg, dispatch_arg, skills, claude_cmd, clone_override=None, timeout=3600, max_budget=20.0, on_spend=None):
    """Run the Replay; the result dict, also written to <replay folder>/result.json. SystemExit when it cannot run.
    on_spend(dollars) is called as soon as the session's cost and the judge's cost are known, so a Replay that fails
    after its session ran has still reported what it spent."""
    skills = Path(skills).resolve()
    if not skills.is_dir():
        raise SystemExit(f"--skills {skills} is not a directory")
    folder, recorded, dispatch = load_dispatch(recorded_arg, dispatch_arg)
    model, effort = agent_header(skills, dispatch["role"])  # before anything is spent
    spec = run.load_specs([recorded["spec"]])[0]
    clone = Path(clone_override) if clone_override else run.HERE / "work" / spec["repo"].split("/")[1]
    if not clone.is_dir():
        raise SystemExit(f"no benchmark clone at {clone}: record a run first")

    started = datetime.now(timezone.utc)
    session_id = str(uuid.uuid4())
    replay_id = f"replay-{started:%Y%m%dT%H%M%S}-{recorded['spec']}-{dispatch_arg}-{session_id[:4]}"
    run_dir, worktree = run.HERE / "runs" / replay_id, run.HERE / "work" / "replay-w"
    run.reset_clone(clone)  # a worktree an earlier Replay left behind
    shutil.rmtree(worktree, ignore_errors=True)  # a folder git no longer lists
    run.git(clone, "-c", "core.longpaths=true", "worktree", "add", "-q", "--detach", str(worktree), dispatch["start"])
    try:
        run_dir.mkdir(parents=True)
        (run_dir / "mcp.json").write_text(json.dumps(run.mcp_config(spec, worktree), indent=2), encoding="utf-8")
        (run_dir / "settings.json").write_text(json.dumps(run.run_settings(worktree, run_dir), indent=2), encoding="utf-8")
        env = run.guard_env(run_dir)
        settings = run.Settings(model, effort, "replay", claude_cmd=claude_cmd, timeout=timeout, max_budget=max_budget)
        argv = run.build_argv(settings, spec, skills, session_id, run_dir / "mcp.json", run_dir / "settings.json",
                              prompt=dispatch["prompt"], agent=dispatch["agent"])
        _, timed_out = run.run_session(argv, worktree, env, run_dir, timeout)
        init, result = run.read_stream(run_dir / "stream.jsonl")
        loaded = run.plugin_verified(init, skills)
        found = run.copy_transcripts(session_id, run_dir / "transcripts")
        report = (result or {}).get("result") or ""
        cost = session_cost(metrics.extract(run_dir / "transcripts")) if found else None
        if cost and on_spend:
            on_spend(cost["cost_usd"])
        problem = (f"timed out after {timeout}s" if timed_out else "claude exited with an error" if result is None or result.get("is_error")
                   else "no transcript was found for the session" if not found
                   else "the skills under test were not the plugin that loaded" if loaded is False else None)
        if problem:
            raise SystemExit(f"{replay_id} could not complete: {problem} (see {run_dir})")
        got = record.verdict(dispatch["role"], report)
        judge_cost, raised, judge_timed_out = 0.0, None, False
        if dispatch.get("seeded"):
            reason = judge.seeded_reached(got)
        else:
            if got["status"] == dispatch["verdict"]["status"] and dispatch["verdict"]["findings"]:
                raised, judge_cost, judge_reply = judge.ask(dispatch["verdict"]["findings"], report, claude_cmd, run_dir, env)
                judge_timed_out = judge_reply == judge.TIMED_OUT
                if on_spend:
                    on_spend(judge_cost)
            reason = judge.reached(dispatch["verdict"], got, raised)
        usage = run_dir / "usage.log"
        out = {"replay": replay_id, "run": recorded["run_id"], "dispatch": dispatch_arg, "role": dispatch["role"],
               "passed": reason is None, "reason": reason, "cost": cost,
               "recorded_cost": dispatch["cost"]["cost_usd"] if dispatch["cost"] else None, "judge_cost": judge_cost, "judge_timed_out": judge_timed_out,
               "limit_values": len(usage_share.read_values(usage)), "limit_share": usage_share.share([usage]),
               "agent": (init or {}).get("agent"), "model": model, "effort": effort, "verdict": got, "raised": raised, "report": report}
        (run_dir / "result.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
        return out
    finally:
        run.reset_clone(clone)


def result_line(r):
    recorded = f"${r['recorded_cost']:.4f}" if r["recorded_cost"] is not None else "n/a"
    share = f"{r['limit_share']:.1f}% of the weekly limit (upper bound)" if r["limit_share"] is not None else "no weekly-limit share"
    outcome = "passed" if r["passed"] else f"FAILED ({r['reason']})"
    judge_note = " (the judge timed out: a session ran and its cost is not counted)" if r.get("judge_timed_out") else ""
    return (f"{r['run']} dispatch {r['dispatch']} ({r['role']}): {outcome}; cost ${r['cost']['cost_usd']:.4f} (recorded {recorded}); "
            f"judge ${r['judge_cost']:.4f}{judge_note}; {r['limit_values']} weekly-limit value(s), {share}; agent {r['agent'] or 'not named'}")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("recorded_run", help="a run id under benchmark/work/recorded/, or the path of its folder")
    p.add_argument("dispatch", help="a dispatch's number from recorded.json, or `seeded`")
    p.add_argument("--skills", required=True, help="the skills checkout to replay under, which may hold uncommitted changes")
    p.add_argument("--target-clone", help="a clone of the target repo to use instead of benchmark/work/<name>")
    p.add_argument("--claude", help="path to claude (default: PATH)")
    p.add_argument("--timeout", type=int, default=3600, help="seconds for the Replay's session")
    p.add_argument("--max-budget", type=float, default=20.0, help="USD cap for the Replay's session, passed to claude")
    a = p.parse_args(argv)
    try:
        r = replay(a.recorded_run, a.dispatch, a.skills, [a.claude or shutil.which("claude") or "claude"], a.target_clone,
                   a.timeout, a.max_budget)
    except SystemExit as e:
        print(e.code, file=sys.stderr)
        return 2
    print(result_line(r))
    return 0 if r["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
