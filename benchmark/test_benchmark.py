"""Tests for the benchmark tooling, on synthetic data only: python benchmark/test_benchmark.py"""
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import collect  # noqa: E402
import compare  # noqa: E402
import guards  # noqa: E402
import metrics  # noqa: E402
import plugin_windows  # noqa: E402
import recount  # noqa: E402
import recount_startup  # noqa: E402
import run  # noqa: E402
import score  # noqa: E402


class GhGuardTests(unittest.TestCase):
    def test_reads_pass(self):
        for args in (
            "issue view 394 --json title,body",
            "-R owner/repo issue view 394",
            "issue list --state open",
            "api user --jq .login",
            "api repos/o/r/issues/1/dependencies/blocked_by",
            "api -X GET repos/o/r/issues -f state=open",
            "search commits foo",
            "auth status",
            "pr view 3",
        ):
            self.assertTrue(guards.gh_is_read_only(args.split()), args)

    def test_writes_are_refused(self):
        for args in (
            "issue edit 394 --add-assignee @me",
            "issue comment 394 --body x",
            "issue close 394",
            "issue create --title t",
            "pr create",
            "pr merge 3",
            "release create v1",
            "api --method POST repos/o/r/issues/1/comments",
            "api --method=PATCH repos/o/r/issues/1",
            "api -XDELETE repos/o/r/issues/1",
            "api repos/o/r/issues/1/comments -f body=x",
            "api repos/o/r/issues/1 --input body.json",
            "api graphql -f query=x",
            "auth login",
            "alias set a b",
        ):
            self.assertFalse(guards.gh_is_read_only(args.split()), args)


class GuardProcessTests(unittest.TestCase):
    def run_guard(self, *argv):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "bench.log"
            env = {**os.environ, "SKILLS_BENCHMARK_LOG": str(log)}
            code = subprocess.run([sys.executable, str(HERE / "guards.py"), *argv], env=env,
                                  capture_output=True, text=True).returncode
            return code, log.read_text(encoding="utf-8") if log.exists() else ""

    def test_blocked_gh_write_exits_1_and_logs(self):
        code, log = self.run_guard("gh", "issue", "close", "5")
        self.assertEqual(code, 1)
        self.assertIn("BLOCKED gh issue close 5", log)

    def test_push_is_refused_and_logged(self):
        code, log = self.run_guard("prepush", "origin", "git@example.com:o/r.git")
        self.assertEqual(code, 1)
        self.assertIn("BLOCKED git push origin", log)

    def test_bench_log_appends_a_noop_line(self):
        code, log = self.run_guard("log", "step 4: git push origin master:master")
        self.assertEqual(code, 0)
        self.assertIn("NOOP step 4: git push origin master:master", log)

    def test_install_writes_shims_hook_and_env(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = guards.install(Path(tmp) / "g", Path(tmp) / "bench.log")
            for name in ("bin/gh", "bin/gh.cmd", "bin/bench-log", "hooks/pre-push"):
                self.assertTrue((Path(tmp) / "g" / name).exists(), name)
            self.assertEqual(env["SKILLS_BENCHMARK"], "1")
            self.assertTrue(env["PATH"].startswith(str(Path(tmp).resolve() / "g" / "bin")))
            self.assertNotIn(b"\r\n", (Path(tmp) / "g" / "bin" / "gh").read_bytes())


class MetricsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = metrics.extract(HERE / "fixtures" / "transcripts")

    def test_token_totals_dedupe_the_streamed_call(self):
        m = self.m
        self.assertEqual((m["input"], m["cache_write"], m["cache_read"], m["output"]), (137, 3500, 5100, 661))
        self.assertEqual(m["calls"], 6)

    def test_cost_uses_list_prices_per_model(self):
        # sonnet: 5280+1065+16260+183 µ$, opus: 11125, unknown model priced as sonnet: 18
        self.assertAlmostEqual(self.m["cost_usd"], 0.033931, places=6)
        self.assertAlmostEqual(self.m["by_model"]["claude-opus-5"]["cost_usd"], 0.011125, places=6)
        self.assertEqual(self.m["unpriced_models"], ["claude-fable-5-1"])

    def test_roles_come_from_the_subagent_meta(self):
        roles = self.m["by_role"]
        self.assertEqual(sorted(roles), ["general-purpose", "implementer", "main", "reviewer", "verifier"])
        self.assertNotIn("general-purpose", metrics.ROLES)  # collect.py files it under "other"
        self.assertAlmostEqual(roles["implementer"]["cost_usd"], 0.01626, places=6)
        self.assertEqual(roles["main"]["calls"], 2)
        self.assertEqual(self.m["subagents"], 4)

    def test_a_prover_that_held_counts_as_a_passed_verify(self):
        with tempfile.TemporaryDirectory() as tmp:
            sub = Path(tmp) / "s" / "subagents"
            sub.mkdir(parents=True)
            (sub / "agent-p.meta.json").write_text('{"agentType": "skills:prover"}', encoding="utf-8")
            line = {"type": "assistant", "timestamp": "2026-10-16T10:00:00Z",
                    "message": {"model": "<synthetic>", "content": [{"type": "text", "text": "status: held\nfailed: none"}]}}
            (sub / "agent-p.jsonl").write_text(json.dumps(line) + "\n", encoding="utf-8")
            self.assertEqual(metrics.extract(Path(tmp))["verifier_status"], "passed")

    def test_context_wall_time_and_checks(self):
        self.assertEqual(self.m["max_context"], 6020)
        self.assertEqual(self.m["wall_s"], 330.0)
        self.assertEqual(self.m["tool_errors"], 1)
        self.assertEqual(self.m["test_commands"], 1)
        self.assertEqual(self.m["verifier_status"], "passed")


DIFF = """\
diff --git a/Commonplace/test/X/ChangelogWebTests.cs b/Commonplace/test/X/ChangelogWebTests.cs
+++ b/Commonplace/test/X/ChangelogWebTests.cs
+        Assert.Equal(1, changelog.Controls.Count);
+        Assert.Contains("<div class=\\"changelog-entry\\">", html);
+        Assert.Equal("Fixed the date picker", entry.TextContent);
+        Assert.True(page.QuerySelectorAll("[data-changelog-control]").Length == 1);
+        // Assert.Contains("<b>", html);
diff --git a/Commonplace/src/Web/Page.cshtml b/Commonplace/src/Web/Page.cshtml
+++ b/Commonplace/src/Web/Page.cshtml
+<div class="changelog-entry">Fixed the date picker</div>
"""


class ScoreTests(unittest.TestCase):
    def test_test_counts_from_each_runner_format(self):
        self.assertEqual(score.parse_test_counts("Passed!  - Failed:     0, Passed:    12, Skipped:     1, Total:    13"), (12, 0))
        self.assertEqual(score.parse_test_counts("Failed!  - Failed: 2, Passed: 3, Skipped: 0, Total: 5\nFailed: 0, Passed: 4, Skipped: 0, Total: 4"), (9, 2))
        self.assertEqual(score.parse_test_counts("Test run summary: Passed!\r\n  total: 7\r\n  failed: 0\r\n  succeeded: 7\r\n  skipped: 0"), (7, 0))
        self.assertEqual(score.parse_test_counts("Total: 6, Errors: 0, Failed: 1, Skipped: 2, Not Run: 0"), (4, 1))
        self.assertIsNone(score.parse_test_counts("Build succeeded."))
        self.assertEqual(score.parse_test_counts("No test matches the given testcase filter\nPassed!  - Failed: 0, Passed: 0, Skipped: 0, Total: 0"), (0, 0))

    def test_forbidden_assertions_are_found_in_added_test_lines_only(self):
        hits = score.find_forbidden(DIFF)
        self.assertEqual([k for k, _ in hits], ["html", "text"])
        self.assertIn("changelog-entry", hits[0][1])

    def judged(self, **over):
        meta = {"exit_code": 0, "plugin_verified": True}
        s = {"landed": True, "checks_done": True, "tests_run": 3, "blocked_writes": 0}
        m = {"subagents": 5, "test_commands": 4, "unpriced_models": []}
        for key, value in over.items():
            {"exit_code": meta, "landed": s, "tests_run": s, "subagents": m, "test_commands": m, "blocked_writes": s,
             "plugin_verified": meta, "timed_out": meta}[key][key] = value
        return score.judge(meta, {}, s, m)

    def test_a_run_that_did_the_work_is_valid(self):
        self.assertEqual(self.judged(), (True, [], []))

    def test_early_exits_and_failures_are_invalid(self):
        for over, text in (({"exit_code": 1}, "claude failed"), ({"timed_out": True}, "timed out"),
                           ({"landed": False}, "no commit landed"), ({"subagents": 0}, "no subagent"),
                           ({"test_commands": 0}, "no test command"), ({"tests_run": 0}, "ran no tests"),
                           ({"plugin_verified": False}, "not the only plugin")):
            valid, reasons, _ = self.judged(**over)
            self.assertFalse(valid, over)
            self.assertIn(text, " ".join(reasons))

    def test_a_tripped_guard_flags_but_does_not_invalidate(self):
        valid, _, flags = self.judged(blocked_writes=1)
        self.assertTrue(valid)
        self.assertIn("guard trip", flags[0])

    def test_score_run_on_a_real_git_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, run = Path(tmp) / "repo", Path(tmp) / "run"
            repo.mkdir()
            run.mkdir()
            git = lambda *a: subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=repo,
                                            capture_output=True, text=True, check=True).stdout.strip()
            git("init", "-q")
            (repo / "a.txt").write_text("one\n")
            git("add", "."), git("commit", "-q", "-m", "base")
            base = git("rev-parse", "HEAD")
            (repo / "a.txt").write_text("one\ntwo\nthree\n")
            (repo / ".agents" / "runs" / "add-lines").mkdir(parents=True)
            (repo / ".agents" / "runs" / "add-lines" / "notes.md").write_text("note\n" * 50)
            git("add", "."), git("commit", "-q", "-m", "Add lines (#7)")
            (run / "bench.log").write_text("2026-01-01T00:00:00 NOOP step 4: git push\n")
            ok = f'"{sys.executable}" -c "print(\'Passed!  - Failed: 0, Passed: 2, Skipped: 0, Total: 2\')"'
            spec = {"base": base, "issue": 7, "landing_lines": 4, "build": [ok], "tests": [ok]}
            meta = {"worktree": str(repo), "exit_code": 0, "plugin_verified": True}
            m = {"subagents": 3, "test_commands": 2, "unpriced_models": [], "verifier_status": "passed"}
            s = score.score_run(run, meta, spec, m)
            self.assertEqual((s["landed"], s["commits"], s["landing_lines"], s["diff_ratio"]), (True, 1, 2, 0.5))
            self.assertEqual((s["build_ok"], s["tests_ok"], s["tests_run"], s["noop_writes"], s["verify"]), (True, True, 2, 1, "passed"))
            self.assertTrue(s["valid"], s["invalid_reasons"])


def make_rows(base_costs, cand_costs, **cand_over):
    """Synthetic CSV rows, alternating baseline and candidate in time, per Spec: {spec: [cost, ...]}."""
    rows = {"base": [], "cand": []}
    clock = iter(range(1000))

    def row(side, spec, cost, over):
        r = {"run_id": "r", "skills_sha": side * 12, "spec": spec, "index": "1", "model": "sonnet", "effort": "high",
             "spec_hash": "h", "claim": "the change cuts cost", "started": f"2026-01-01T10:{next(clock):04d}",
             "valid": "True", "invalid_reasons": "", "flags": "", "failed": "False", "cost_usd": str(cost),
             "tokens_total": str(cost * 1e5), "subagents": "6", "wall_s": "600", "max_context": "90000",
             "api_errors": "0", "tool_errors": "3", "landed": "True", "diff_ratio": "1.0", "build_ok": "True",
             "tests_ok": "True", "tests_run": "5", "verify": "passed", "forbidden_html": "0", "forbidden_text": "0",
             "blocked_writes": "0", "noop_writes": "2", "checks_done": "True"}
        r.update({f"cost_{role}": str(cost * share) for role, share in
                  zip(compare.ROLES, (0.1, 0.5, 0.2, 0.15, 0.0, 0.05))})
        r.update(over)
        return r

    for spec in base_costs:
        for b, c in zip(base_costs[spec], cand_costs[spec]):
            rows["base"].append(row("b", spec, b, {}))
            rows["cand"].append(row("c", spec, c, cand_over))
    return rows["base"], rows["cand"]


class CompareTests(unittest.TestCase):
    A_BASE, A_CAND = [10, 10.5, 11, 10.2, 10.8], [7, 7.2, 7.5, 7.1, 7.4]
    B_BASE, B_CAND = [20, 21, 20.5, 19.8, 20.2], [14, 14.5, 15, 14.2, 14.8]

    def text(self, base, cand):
        return compare.report(base, cand, "the change cuts cost", ("bbbbbbbbbbbb", "cccccccccccc"))

    def test_rows_load_from_a_csv_path_or_a_sha_prefix(self):
        base, _ = make_rows({"a": self.A_BASE}, {"a": self.A_CAND})
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bbbbbbbbbbbb.csv"
            with open(path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, list(base[0]))
                writer.writeheader()
                writer.writerows(base)
            self.assertEqual(compare.load_rows(str(path)), base)
            self.assertEqual(compare.load_rows("bbbb", results=tmp), base)
            with self.assertRaises(SystemExit):
                compare.load_rows("zzzz", results=tmp)

    def test_rank_sum_p_is_exact(self):
        self.assertAlmostEqual(compare.rank_sum_p([1, 2, 3], [4, 5, 6]), 0.1)
        self.assertAlmostEqual(compare.rank_sum_p([1, 2, 3], [1, 2, 3]), 1.0)
        self.assertAlmostEqual(compare.rank_sum_p([1, 2], [3, 4]), 1 / 3)
        self.assertEqual(compare.decide([5, 5, 5], [5, 5, 5])[0], "no measurable difference")

    def test_a_clear_gap_is_cheaper_and_leads_with_the_claim_and_verdict(self):
        text, verdict = self.text(*make_rows({"a": self.A_BASE, "b": self.B_BASE}, {"a": self.A_CAND, "b": self.B_CAND}))
        self.assertEqual(verdict, "cheaper")
        lines = text.splitlines()
        self.assertEqual(lines[0], "Claim: the change cuts cost")
        self.assertTrue(lines[2].startswith("VERDICT: cheaper (-3"), lines[2])
        self.assertIn("Limiter: the implementer role is 50% of baseline cost", text)
        self.assertIn("Runs alternated baseline and candidate", text)
        self.assertIn("Quality regressions: none flagged.", text)

    def test_a_gap_inside_the_spread_is_no_measurable_difference(self):
        text, verdict = self.text(*make_rows({"a": [10, 12, 9, 13, 11]}, {"a": [10.5, 11.5, 9.5, 12, 10]}))
        self.assertEqual(verdict, "no measurable difference")

    def test_too_few_runs_is_inconclusive_with_the_reason(self):
        text, verdict = self.text(*make_rows({"a": [10, 11]}, {"a": [7, 7.5]}))
        self.assertEqual(verdict, "inconclusive")
        self.assertIn("rank-sum p is 0.333", text)
        self.assertIn("fewer than 5 valid runs per side on a", text)

    def test_mismatched_settings_are_refused_with_no_table(self):
        text, verdict = self.text(*make_rows({"a": self.A_BASE}, {"a": self.A_CAND}, effort="medium"))
        self.assertEqual(verdict, "inconclusive")
        self.assertIn("different settings", text)
        self.assertNotIn("Quality", text)

    def test_unscored_work_makes_it_inconclusive(self):
        text, verdict = self.text(*make_rows({"a": self.A_BASE}, {"a": self.A_CAND}, checks_done="False"))
        self.assertEqual(verdict, "inconclusive")
        self.assertIn("could not be done", text)

    def test_a_changed_issue_makes_it_inconclusive(self):
        text, verdict = self.text(*make_rows({"a": self.A_BASE}, {"a": self.A_CAND}, spec_hash="other"))
        self.assertEqual(verdict, "inconclusive")
        self.assertIn("the Issue changed between runs", text)

    def test_invalid_runs_are_counted_and_left_out_of_the_medians(self):
        base, cand = make_rows({"a": self.A_BASE}, {"a": self.A_CAND})
        bad = dict(cand[0], valid="False", cost_usd="0.1", invalid_reasons="no commit landed", landed="False")
        text, verdict = self.text(base, cand + [bad])
        self.assertEqual(verdict, "cheaper")
        self.assertIn("Invalid candidate runs: 1x no commit landed", text)
        self.assertRegex(text, r"did not do the work \(invalid\)\s+0\s+1")
        self.assertIn("1 of 6 candidate runs did not do the work", text)

    def test_a_quality_regression_is_flagged_even_when_cheaper(self):
        base, cand = make_rows({"a": self.A_BASE}, {"a": self.A_CAND})
        for r in cand[:2]:
            r["tests_ok"] = "False"
        text, verdict = self.text(base, cand)
        self.assertEqual(verdict, "cheaper")
        self.assertIn("with quality regressions", text)
        self.assertIn("tests passed on 3 of 5 valid candidate runs, against 5 of 5", text)

    def test_a_failed_verifier_is_a_quality_regression(self):
        base, cand = make_rows({"a": self.A_BASE}, {"a": self.A_CAND})
        for r in cand[:2]:
            r["verify"] = "failed"
        cand[2]["verify"] = "skipped"
        text, _ = self.text(base, cand)
        self.assertIn("Verifier passed on 2 of 5 valid candidate runs, against 5 of 5", text)

    def test_an_old_csv_with_a_proof_column_still_compares(self):
        base, cand = make_rows({"a": self.A_BASE}, {"a": self.A_CAND})
        for r in cand:  # held was the Prover's pass, so it reads as the verifier's
            r["proof"] = r.pop("verify").replace("passed", "held")
        text, verdict = self.text(base, cand)
        self.assertEqual(verdict, "cheaper")
        self.assertIn("Quality regressions: none flagged.", text)

    def test_a_saving_past_the_biggest_role_share_is_called_out(self):
        text, _ = self.text(*make_rows({"a": [10, 10.5, 11, 10.2, 10.8]}, {"a": [3, 3.2, 3.1, 3.4, 3.3]}))
        self.assertIn("something else is being measured", text)


class RunnerTests(unittest.TestCase):
    def test_argv_pins_settings_and_ends_with_the_variadic_flag(self):
        settings = run.Settings("sonnet", "high", "claim", claude_cmd=["claude"])
        argv = run.build_argv(settings, {"issue": 394}, "/skills", "sid", "/mcp.json", "/settings.json")
        self.assertEqual(argv[:3], ["claude", "-p", "/implement #394"])
        for pair in (["--model", "sonnet"], ["--effort", "high"], ["--plugin-dir", "/skills"], ["--session-id", "sid"],
                     ["--settings", "/settings.json"]):
            self.assertEqual(argv[argv.index(pair[0]) + 1], pair[1])
        self.assertIn("--strict-mcp-config", argv)
        self.assertEqual(argv[argv.index("--disallowedTools") + 1:], guards.DENIED_TOOLS)

    def test_the_plugin_under_test_must_be_the_one_that_loaded(self):
        init = {"plugins": [{"name": "skills", "path": "/a/skills"}]}
        self.assertTrue(run.plugin_verified(init, "/a/skills"))
        self.assertFalse(run.plugin_verified(init, "/b/skills"))
        self.assertIsNone(run.plugin_verified({}, "/a/skills"))
        both = {"plugins": [{"name": "skills", "path": "/a/skills"}, {"name": "pstack", "path": "/installed"}]}
        self.assertFalse(run.plugin_verified(both, "/a/skills"))
        builtin = {"plugins": [{"name": "skills", "path": "/a/skills"}, {"name": "cc-plugin-telemetry", "path": "builtin"}]}
        self.assertTrue(run.plugin_verified(builtin, "/a/skills"))

    def test_every_plugin_the_user_or_target_enables_is_turned_off(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "cfg").mkdir(), (tmp / "w" / ".claude").mkdir(parents=True)
            (tmp / "cfg" / "settings.json").write_text('{"enabledPlugins": {"pstack@p": true, "skills@m": true}}', encoding="utf-8")
            (tmp / "w" / ".claude" / "settings.json").write_text('{"enabledPlugins": {"tool@t": true}}', encoding="utf-8")
            old = os.environ.get("CLAUDE_CONFIG_DIR")
            os.environ["CLAUDE_CONFIG_DIR"] = str(tmp / "cfg")
            try:
                off = run.other_plugins_off(tmp / "w")
            finally:
                os.environ.pop("CLAUDE_CONFIG_DIR") if old is None else os.environ.__setitem__("CLAUDE_CONFIG_DIR", old)
            self.assertEqual(off, {"enabledPlugins": {"pstack@p": False, "skills@m": False, "tool@t": False}})

    def test_a_spec_with_a_todo_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "specs.yaml"
            path.write_text("defaults:\n  repo: o/r\nspecs:\n  - id: a\n    base: TODO\n", encoding="utf-8")
            with self.assertRaises(SystemExit):
                run.load_specs(path=path)
        self.assertEqual(len(run.load_specs()), 4)

    def test_a_skills_commit_without_benchmark_mode_is_refused(self):
        with self.assertRaises(SystemExit):
            run.skills_checkout("f4f9239")

    def test_run_one_end_to_end_against_a_fake_claude(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            git = lambda cwd, *a: subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=cwd,
                                                 capture_output=True, text=True, check=True).stdout.strip()
            origin, clone = tmp / "origin.git", tmp / "clone"
            git(tmp, "init", "-q", "--bare", str(origin))
            clone.mkdir()
            git(clone, "init", "-q", "-b", "main")
            (clone / "a.txt").write_text("one\n")
            git(clone, "add", "."), git(clone, "commit", "-q", "-m", "base")
            git(clone, "remote", "add", "origin", str(origin))
            base = git(clone, "rev-parse", "HEAD")
            ok = f'"{sys.executable}" -c "print(\'Passed!  - Failed: 0, Passed: 2, Skipped: 0, Total: 2\')"'
            spec = {"id": "s", "repo": "o/r", "issue": 7, "base": base, "landing_lines": 4, "build": [ok], "tests": [ok]}
            settings = run.Settings("sonnet", "high", "cheaper", claude_cmd=[sys.executable, str(HERE / "fixtures" / "fake_claude.py")],
                                    timeout=120, clone=clone)
            (tmp / "plugin").mkdir()
            old = {k: os.environ.get(k) for k in ("CLAUDE_CONFIG_DIR", "FAKE_PUSH_TARGET")}
            os.environ.update(CLAUDE_CONFIG_DIR=str(tmp / "cfg"), FAKE_PUSH_TARGET=str(origin))
            saved = (run.HERE, collect.HERE, run.spec_hash)
            run.HERE = collect.HERE = tmp / "bench"
            run.spec_hash = lambda spec: "hash"
            try:
                s = run.run_one("baseline", "a" * 40, tmp / "plugin", spec, 1, settings)
            finally:
                run.HERE, collect.HERE, run.spec_hash = saved
                for k, v in old.items():
                    os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
            self.assertTrue(s["valid"], s["invalid_reasons"])
            self.assertEqual((s["landed"], s["tests_run"], s["noop_writes"]), (True, 2, 1))
            self.assertEqual(s["blocked_writes"], 2)  # the gh write and the explicit-URL push
            self.assertEqual(git(origin, "for-each-ref"), "")  # nothing ever reached the remote
            self.assertEqual(git(clone, "branch", "--format=%(refname:short)"), "main")  # throwaway branch and worktree gone
            with open(tmp / "bench" / "results" / ("a" * 12 + ".csv"), encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 1)
            self.assertEqual((rows[0]["valid"], rows[0]["model"], rows[0]["effort"], rows[0]["subagents"]), ("True", "sonnet", "high", "4"))
            self.assertAlmostEqual(float(rows[0]["cost_usd"]), 0.0339, places=4)
            self.assertAlmostEqual(float(rows[0]["cost_reviewer"]), 0.0111, places=4)


class RecountTests(unittest.TestCase):
    """Hand-counted from fixtures/recount/: 8 sessions, 16 Implementers, one reviewer that must not count."""
    FIXTURES = HERE / "fixtures" / "recount"

    def test_count_applies_every_rule(self):
        self.assertEqual(recount.count(recount.read_sessions(self.FIXTURES)), {
            "sessions": 8, "reached_2": 4, "reached_3": 1,
            "hard_violation": 2, "hard_cites_standards": 1,
            "first_standards": 6, "first_standards_whole": 3, "first_standards_parts": 3,
            "first_principles": 2, "first_principles_whole": 1, "first_principles_parts": 1,
            "first_names_standards": 2, "first_names_principles": 1,
            "reached_2_with_reader": 2, "reached_2_without_reader": 2, "cites_with_reader": 1,
        })

    def test_prompt_iteration_numbers(self):
        agents = {a["first_ts"]: a["n"] for sessions in recount.read_sessions(self.FIXTURES).values() for a in sessions}
        ts = metrics._time
        self.assertEqual(agents[ts("2026-11-01T10:00:00.000Z")], 0)  # unnumbered prompt
        self.assertEqual(agents[ts("2026-11-01T10:05:00.000Z")], 1)  # "Iteration 1 ... Iteration 2": the first wins

    def test_triage_selects_by_mtime_and_first_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "logs"
            shutil.copytree(self.FIXTURES, root)
            old = recount.TRIAGE_MTIME - 86400
            for path in (root / "sess-h").rglob("*.jsonl"):
                os.utime(path, (old, old))  # sess-h: mtime before 2026-10-16
            # sess-f starts after the #56 scan time; sess-g starts exactly at it and stays in
            out = subprocess.run([sys.executable, str(HERE / "recount.py"), "--triage", str(root)],
                                 capture_output=True, text=True, check=True).stdout
        self.assertEqual(out, "sessions 6\nimplementers 14\n")

    def test_an_unknown_mode_prints_usage_and_fails(self):
        result = subprocess.run([sys.executable, str(HERE / "recount.py"), "--bogus"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Usage: python benchmark/recount.py [log-root]", result.stderr)


class RecountWindowTests(unittest.TestCase):
    """Hand-counted from fixtures/recount-windows/: 11 sessions, each with one or two Implementers.
    aaaaaaaaaaaa is a plugin cache commit without 0f8254c, bbbbbbbbbbbb one with it, cccccccccccc one git cannot resolve."""
    FIXTURES = HERE / "fixtures" / "recount-windows"
    SCAN = metrics._time("2026-11-10T00:00:00Z")  # fixture-local; the module constant is only the CLI default

    @staticmethod
    def contains(sha):
        return {"aaaaaaaaaaaa": False, "bbbbbbbbbbbb": True}.get(sha)

    def split(self, scan=SCAN):
        windows, unresolved = recount.split_windows(recount.read_windowed(self.FIXTURES, scan), self.contains)
        return {name: sorted(sessions) for name, sessions in windows.items()}, unresolved, windows

    def test_each_session_goes_into_its_window(self):
        ids, unresolved, _ = self.split()
        self.assertEqual(ids["before"], ["w-late", "w-noise", "w-nosha-early", "w-old", "w-sub", "w-unres-old"])
        self.assertEqual(ids["after"], ["w-new", "w-nosha-late", "w-prompt", "w-unres"])
        self.assertEqual(ids["mixed"], ["w-both"])
        self.assertEqual(unresolved, {"cccccccccccc"})

    def test_counts_per_window(self):
        _, _, windows = self.split()
        counts = {name: recount.count(sessions) for name, sessions in windows.items()}
        self.assertEqual({name: (c["sessions"], c["reached_2"]) for name, c in counts.items()},
                         {"before": (6, 1), "after": (4, 1), "mixed": (1, 1)})

    def test_records_after_the_scan_time_change_no_count(self):
        # w-late has a record naming bbbbbbbbbbbb and an n == 2 Implementer, both stamped 2027-01-01
        ids, _, windows = self.split()
        self.assertIn("w-late", ids["before"])
        self.assertEqual(recount.count({"w-late": windows["before"]["w-late"]})["reached_2"], 0)
        later, _, windows = self.split(metrics._time("2027-02-01T00:00:00Z"))
        self.assertIn("w-late", later["mixed"])
        self.assertEqual(recount.count({"w-late": windows["mixed"]["w-late"]})["reached_2"], 1)

    def test_a_rerun_gives_the_same_counts(self):
        self.assertEqual(self.split()[:2], self.split()[:2])

    def test_report_for_the_fixture(self):
        report = recount.window_report(self.FIXTURES, self.SCAN, self.contains).splitlines()
        self.assertIn("all end at scan time 2026-11-10T00:00:00Z; unresolved SHAs 1", report[0])
        self.assertEqual(report[1].split(), ["count", "before", "after", "mixed"])
        self.assertEqual(report[2].split(), ["sessions", "6", "4", "1"])
        self.assertEqual(report[-2], "reached Iteration 2: before 1/6 (16.7%), after 1/4 (25.0%), p = 0.7469")
        self.assertEqual(report[-1], "verdict: not dropped")

    def test_containment_of_real_commits(self):
        self.assertIs(recount.contains_fix("0f8254c795f6"), True)  # 0f8254c itself
        self.assertIs(recount.contains_fix("045d8e2ae201"), False)  # its parent
        self.assertIsNone(recount.contains_fix("000000000000"))  # git cannot resolve it


class NoiseCommitTests(unittest.TestCase):
    """Commits in a throwaway git repo with fixed dates; the span is 2026-11-04T08:11:29Z to 2026-11-22T05:44:11Z."""
    AFTER = metrics._time("2026-11-04T08:11:29Z")
    UNTIL = metrics._time("2026-11-22T05:44:11Z")
    PATHS = ["skills/implement/", "agents/planner.md"]

    def commit(self, repo, path, subject, when):
        target = Path(repo) / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(subject, encoding="utf-8")
        env = {**os.environ, "GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when}
        for args in (["add", "."], ["-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-q", "-m", subject]):
            subprocess.run(["git", *args], cwd=repo, env=env, check=True, capture_output=True)

    def repo(self, tmp):
        subprocess.run(["git", "init", "-q"], cwd=tmp, check=True, capture_output=True)
        self.commit(tmp, "skills/implement/SKILL.md", "before the span", "2026-11-04T08:00:00Z")
        self.commit(tmp, "skills/implement/SKILL.md", "inside, listed folder", "2026-11-05T10:00:00Z")
        self.commit(tmp, "README.md", "inside, unlisted path", "2026-11-06T10:00:00Z")
        self.commit(tmp, "agents/planner.md", "inside, listed file", "2026-11-22T05:44:11Z")
        self.commit(tmp, "agents/planner.md", "after the scan time", "2026-11-22T05:44:12Z")
        return tmp

    def test_lists_only_listed_commits_inside_the_span_newest_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            lines = recount.commits_in_span(self.repo(tmp), self.AFTER, self.UNTIL, self.PATHS)
        self.assertEqual([line.split(" ", 1)[1] for line in lines],
                         ["2026-11-22 inside, listed file", "2026-11-05 inside, listed folder"])
        self.assertTrue(all(len(line.split(" ", 1)[0]) >= 7 for line in lines))

    def test_an_empty_span_lists_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(recount.commits_in_span(self.repo(tmp), self.UNTIL + 100, self.UNTIL + 200, self.PATHS), [])

    def test_a_missing_repo_is_none(self):
        self.assertIsNone(recount.commits_in_span("/nonexistent/repo", self.AFTER, self.UNTIL, self.PATHS))

    def test_report_prints_each_part_and_survives_a_missing_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.repo(tmp)
            out = recount.noise_report(repo, "/nonexistent/suite", self.AFTER, self.UNTIL)
        lines = out.splitlines()
        self.assertEqual(lines[0], "skills commits touching the implement, code-review or agent files, "
                                   "2026-11-04T08:11:29Z to 2026-11-22T05:44:11Z:")
        self.assertEqual(lines[3], "called out: 69406f0: " + recount.RESUME_NOTE)
        self.assertEqual(lines[4], "mvdmio-suite commits touching coding-standards files, "
                                   "2026-11-04T08:11:29Z to 2026-11-22T05:44:11Z: could not be read")
        self.assertEqual(len(lines), 5)


class TwoProportionTests(unittest.TestCase):
    def test_worked_example(self):
        # 30/100 against 45/100: pooled 0.375, z = 0.15 / sqrt(0.375 * 0.625 * 0.02) = 2.19, p = 0.0285
        # (checked outside the code with statistics.NormalDist: 2 * (1 - cdf(2.1909)) = 0.02846)
        self.assertAlmostEqual(recount.two_proportion_p(30, 100, 45, 100), 0.028, places=3)

    def test_a_lower_after_rate_at_p_below_005_is_dropped(self):
        p, dropped = recount.compare_rates(45, 100, 30, 100)
        self.assertAlmostEqual(p, 0.028, places=3)
        self.assertTrue(dropped)

    def test_a_higher_after_rate_at_p_below_005_is_not_dropped(self):
        p, dropped = recount.compare_rates(30, 100, 45, 100)
        self.assertAlmostEqual(p, 0.028, places=3)
        self.assertFalse(dropped)

    def test_a_lower_after_rate_at_p_above_005_is_not_dropped(self):
        p, dropped = recount.compare_rates(5, 10, 3, 10)
        self.assertGreater(p, 0.05)
        self.assertFalse(dropped)

    def test_an_empty_window_is_not_dropped(self):
        self.assertEqual(recount.compare_rates(5, 10, 0, 0), (1.0, False))

    def test_equal_rates_give_p_one(self):
        self.assertEqual(recount.two_proportion_p(10, 50, 10, 50), 1.0)

    def test_an_empty_window_gives_p_one(self):
        self.assertEqual(recount.two_proportion_p(0, 0, 5, 10), 1.0)
        self.assertEqual(recount.two_proportion_p(5, 10, 0, 0), 1.0)

    def test_a_zero_pooled_error_gives_p_one(self):
        self.assertEqual(recount.two_proportion_p(0, 10, 0, 10), 1.0)
        self.assertEqual(recount.two_proportion_p(10, 10, 10, 10), 1.0)


class PercentileTests(unittest.TestCase):
    def test_odd_count_median_is_the_middle_value(self):
        self.assertEqual(recount_startup.percentile([5, 1, 3], 0.5), 3)

    def test_even_count_median_is_between_the_middle_values(self):
        self.assertEqual(recount_startup.percentile([4, 1, 3, 2], 0.5), 2.5)

    def test_a_percentile_interpolates_between_closest_ranks(self):
        self.assertAlmostEqual(recount_startup.percentile([1, 3, 5], 0.1), 1.4)  # rank 0.2 of 0..2
        self.assertAlmostEqual(recount_startup.percentile([4, 1, 3, 2], 0.9), 3.7)  # rank 2.7 of 0..3

    def test_a_single_value_is_its_own_percentile(self):
        self.assertEqual([recount_startup.percentile([7], q) for q in (0.1, 0.5, 0.9)], [7, 7, 7])

    def test_an_empty_list_has_no_percentile(self):
        self.assertIsNone(recount_startup.percentile([], 0.5))


class RecountStartupTests(unittest.TestCase):
    """Hand-counted from fixtures/recount-startup/: 11 sessions over two projects.
    aaaaaaaaaaaa is a plugin cache commit without 6bd7016, bbbbbbbbbbbb one with it. With the scan at 2026-11-20:
    before = s-old, s-nosha-early; after = s-new, s-nosha-late, s-late; mixed = s-both. s-too-early (aaaa) and
    s-nosha-prestart start before 2026-10-31 and are in no column; s-explorer-only holds only an explorer."""
    FIXTURES = HERE / "fixtures" / "recount-startup"
    SCAN = metrics._time("2026-11-20T00:00:00Z")  # fixture-local; the module constant is only the CLI default

    @staticmethod
    def contains(sha):
        return {"aaaaaaaaaaaa": False, "bbbbbbbbbbbb": True}.get(sha)

    def windows(self, scan=SCAN):
        windows, unresolved = recount_startup.windowed_sessions(self.FIXTURES, scan, self.contains)
        return windows, unresolved

    def test_each_session_goes_into_its_window(self):
        windows, unresolved = self.windows()
        self.assertEqual({name: sorted(sessions) for name, sessions in windows.items()}, {
            "before": [("proj-a", "s-nosha-early"), ("proj-a", "s-old")],
            "after": [("proj-a", "s-late"), ("proj-b", "s-new"), ("proj-b", "s-nosha-late")],
            "mixed": [("proj-a", "s-both")]})
        self.assertEqual(unresolved, set())

    def test_the_table_counts_each_row(self):
        table = dict(recount_startup.build_table(self.windows()[0]))
        self.assertEqual({name: table[name] for name in (
            "sessions all", "sessions implementer", "sub-agents all", "sub-agents planner", "sub-agents implementer",
            "sub-agents reviewer", "sub-agents verifier",
            "skills listing all", "skills listing planner", "skills listing verifier",
            "tools with Skill all", "tools with Skill implementer", "tools with Skill verifier",
            "tools with Agent all", "tools with Agent reviewer", "tools with Agent implementer",
            "sub-agents without a shape")}, {
            "sessions all": ["2", "3", "1"],
            "sessions implementer": ["1", "1", "1"],
            "sub-agents all": ["4", "5", "1"],
            "sub-agents planner": ["1", "1", "0"],
            "sub-agents implementer": ["1", "1", "1"],
            "sub-agents reviewer": ["1", "2", "0"],
            "sub-agents verifier": ["1", "1", "0"],
            "skills listing all": ["1/4 (25.0%)", "0/5 (0.0%)", "0/1 (0.0%)"],
            "skills listing planner": ["1/1 (100.0%)", "0/1 (0.0%)", "0/0"],
            "skills listing verifier": ["0/1 (0.0%)", "0/1 (0.0%)", "0/0"],
            "tools with Skill all": ["2/3 (66.7%)", "0/5 (0.0%)", "0/1 (0.0%)"],
            "tools with Skill implementer": ["1/1 (100.0%)", "0/1 (0.0%)", "0/1 (0.0%)"],
            "tools with Skill verifier": ["0/0", "0/1 (0.0%)", "0/0"],
            "tools with Agent all": ["1/3 (33.3%)", "2/5 (40.0%)", "0/1 (0.0%)"],
            "tools with Agent reviewer": ["0/1 (0.0%)", "1/2 (50.0%)", "0/0"],
            "tools with Agent implementer": ["0/1 (0.0%)", "1/1 (100.0%)", "0/1 (0.0%)"],
            "sub-agents without a shape": ["1", "0", "0"]})

    def test_the_first_request_percentiles_per_role(self):
        # s-old's implementer: one request over two lines (3+9000+0, 3+9000+2000, each type's largest: 11003), and a
        # later request that must not count; its planner: 10+20000+5000, later request ignored
        table = dict(recount_startup.build_table(self.windows()[0]))
        self.assertEqual({name: cells for name, cells in table.items() if name.startswith("first request")}, {
            "first request p50 planner": ["25010", "6000", "-"],
            "first request p10 planner": ["25010", "6000", "-"],
            "first request p90 planner": ["25010", "6000", "-"],
            "first request p50 implementer": ["11003", "9000", "4000"],
            "first request p10 implementer": ["11003", "9000", "4000"],
            "first request p90 implementer": ["11003", "9000", "4000"],
            "first request p50 reviewer": ["3000", "8000", "-"],  # after: 7000 and 9000
            "first request p10 reviewer": ["3000", "7200", "-"],
            "first request p90 reviewer": ["3000", "8800", "-"],
            "first request p50 verifier": ["8000", "5000", "-"],
            "first request p10 verifier": ["8000", "5000", "-"],
            "first request p90 verifier": ["8000", "5000", "-"]})

    def test_one_sub_agent_log_reduces_to_its_startup_facts(self):
        subagents = self.FIXTURES / "proj-a" / "s-old" / "subagents"
        implementer = recount_startup.read_subagent(subagents / "agent-i1.jsonl", "implementer", self.SCAN)
        self.assertEqual((implementer["first_request"], implementer["model"], implementer["listing"], implementer["tools"]),
                         (11003, "claude-sonnet-4-6", False, {"Read", "Skill"}))  # a later request is Opus
        planner = recount_startup.read_subagent(subagents / "agent-p1.jsonl", "planner", self.SCAN)
        self.assertEqual((planner["model"], planner["listing"], planner["tools"]), ("claude-opus-4-7", True, {"Read", "Skill", "Agent"}))
        verifier = recount_startup.read_subagent(subagents / "agent-v1.jsonl", "verifier", self.SCAN)
        self.assertEqual((verifier["listing"], verifier["tools"]), (False, None))  # a listing after the first request is not at start

    def test_an_explorer_and_a_session_with_only_an_explorer_do_not_count(self):
        sessions = recount_startup.read_agents(self.FIXTURES, self.SCAN)
        self.assertNotIn(("proj-a", "s-explorer-only"), sessions)
        self.assertEqual(sorted(a["role"] for a in sessions[("proj-a", "s-old")]), ["implementer", "planner", "verifier"])

    def test_a_before_session_earlier_than_the_start_is_in_no_column(self):
        windows, _ = self.windows()
        named = {session for sessions in windows.values() for _, session in sessions}
        self.assertNotIn("s-too-early", named)  # names the old SHA only
        self.assertNotIn("s-nosha-prestart", named)  # names no SHA

    def test_records_after_the_scan_time_do_not_count(self):
        # s-late has a record naming aaaa and a Reviewer, both stamped 2026-11-25
        later, _ = self.windows(metrics._time("2026-12-01T00:00:00Z"))
        self.assertEqual(sorted(later["mixed"]), [("proj-a", "s-both"), ("proj-a", "s-late")])
        self.assertEqual(sorted(a["role"] for a in later["mixed"][("proj-a", "s-late")]["agents"]), ["implementer", "reviewer"])
        self.assertEqual(sorted(later["after"]), [("proj-b", "s-new"), ("proj-b", "s-nosha-late")])

    def test_a_rerun_gives_the_same_counts(self):
        first, second = (recount_startup.build_table(self.windows()[0]) for _ in range(2))
        self.assertEqual(first, second)

    def test_report_names_the_bounds_the_method_and_the_columns(self):
        report = recount_startup.window_report(*self.windows(), self.SCAN).splitlines()
        self.assertIn("first record before 2026-11-07T01:47:33Z", report[0])
        self.assertIn("all end at scan time 2026-11-20T00:00:00Z; unresolved SHAs 0", report[0])
        self.assertIn("percentiles by linear interpolation between closest ranks", report[1])
        self.assertEqual(report[2].split(), ["count", "before", "after", "mixed"])
        self.assertEqual(report[3].split(), ["sessions", "all", "2", "3", "1"])

    def test_containment_of_real_commits(self):
        self.assertIs(plugin_windows.contains(recount_startup.FIX_SHA, "6bd70161a905"), True)  # 6bd7016 itself
        self.assertIs(plugin_windows.contains(recount_startup.FIX_SHA, "2d84926da062"), False)  # its parent

    def test_baseline_selects_by_file_mtime_and_record_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "logs"
            shutil.copytree(self.FIXTURES, root)
            for path in root.rglob("agent-*.jsonl"):
                stamp = recount_startup.BEFORE_START + (-86400 if "s-too-early" in path.parts else 86400)
                os.utime(path, (stamp, stamp))
            out = subprocess.run([sys.executable, str(HERE / "recount_startup.py"), "--baseline", str(root)],
                                 capture_output=True, text=True, check=True).stdout
        # the logs from 2026-11-10 on are written after the cut-off; s-too-early's log is older than the start
        # kept: s-old (planner, implementer, verifier), s-both, s-nosha-early, s-nosha-prestart
        # cost: every turn of those four sessions, the explorer's too. Hand-worked from PRICES, in millionths of a dollar:
        # sonnet 1605 (explorer) + 5205 + 9105 + 10314 (implementer, largest of its two lines) + 6105 + 12105,
        # opus 41475 + 50224.5 (planner) + 50189.5 (implementer's later request) = 186328
        self.assertEqual(out.splitlines()[1:], ["sessions 4", "sub-agents 6", "median first request 6000", "total cost $0.19"])

    def test_an_unknown_mode_prints_usage_and_fails(self):
        result = subprocess.run([sys.executable, str(HERE / "recount_startup.py"), "--bogus"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Usage: python benchmark/recount_startup.py [log-root]", result.stderr)


class RecountStartupPassesTests(unittest.TestCase):
    """Hand-counted from fixtures/recount-startup-passes/proj-p/: before = s-b1, s-b2 (aaaa); after = s-a1, s-a2 (bbbb);
    mixed holds no session. Costs, in dollars from PRICES (sonnet 3/15/3.75/0.30, opus 5/25/6.25/10 1h/0.50 per million):
    s-b1 4.50 (driving turn) + 6.75 (one turn over two lines, 2M in and 50k out, priced once; the <synthetic> turn and
    the turn after the scan time do not count) + 1.80 + 1.35 + 2.25 (the Reviewers) + 6.50 (the explorer) = 23.15;
    s-b2 0.85 (opus 100k in, 14k out); s-a1 0.75; s-a2 27.25 (opus: 0.50 in, 6.25 5-minute write, 20.00 1-hour write, 0.50 out)."""
    FIXTURES = HERE / "fixtures" / "recount-startup-passes"
    SCAN = metrics._time("2026-11-20T00:00:00Z")

    @staticmethod
    def contains(sha):
        return {"aaaaaaaaaaaa": False, "bbbbbbbbbbbb": True}.get(sha)

    def windows(self):
        return recount_startup.windowed_sessions(self.FIXTURES, self.SCAN, self.contains)[0]

    def test_the_table_counts_cost_passes_findings_send_backs_and_lost_tools(self):
        table = dict(recount_startup.build_table(self.windows()))
        self.assertEqual({name: table[name] for name in (
            "session cost mean", "session cost total", "sessions with >1 reviewer", "sessions with >1 verifier",
            "Hard violations total", "Hard violations per session", "Judgement calls total", "Judgement calls per session",
            "send-backs total", "send-backs per session", "lost-tool attempts")}, {
            "session cost mean": ["$12.00", "$14.00", "-"],
            "session cost total": ["$24.00", "$28.00", "$0.00"],
            "sessions with >1 reviewer": ["1/2 (50.0%)", "0/2 (0.0%)", "0/0"],  # s-b1 has two; s-a1 has one Reviewer and one Verifier
            "sessions with >1 verifier": ["1/2 (50.0%)", "0/2 (0.0%)", "0/0"],  # s-b2 has two
            "Hard violations total": ["5", "1", "0"],  # before 3 + 1 + 1; after 1
            "Hard violations per session": ["2.50", "0.50", "-"],
            "Judgement calls total": ["6", "2", "0"],  # before 4 + 1 + 1; after 2
            "Judgement calls per session": ["3.00", "1.00", "-"],
            "send-backs total": ["0", "2", "0"],  # Iteration 1 is not one; "Iteration 2 ... Iteration 1" and "Iteration 2" are
            "send-backs per session": ["0.00", "1.00", "-"],
            "lost-tool attempts": ["2", "2", "0"]})

    def test_a_reviewer_reports_through_its_last_handback_else_its_last_message(self):
        subagents = self.FIXTURES / "proj-p"
        def reviewer(session, name):
            agent = recount_startup.read_subagent(subagents / session / "subagents" / name, "reviewer", self.SCAN)
            return agent["handback"], agent["findings"]
        # handback only: six counted lines (list markers, bold, indent), two lines that mention a finding mid-line are not
        self.assertEqual(reviewer("s-b1", "agent-r1.jsonl"), (True, {"Hard violation": 3, "Judgement call": 4}))
        # plain text only: the last message id, over two lines; an earlier message does not count
        self.assertEqual(reviewer("s-b1", "agent-r2.jsonl"), (False, {"Hard violation": 1, "Judgement call": 1}))
        # plain text, then a handback call: the handback wins
        self.assertEqual(reviewer("s-b2", "agent-r1.jsonl"), (True, {"Hard violation": 1, "Judgement call": 1}))
        # a handback call, then more text: the handback wins
        self.assertEqual(reviewer("s-a1", "agent-r1.jsonl"), (True, {"Hard violation": 1, "Judgement call": 2}))

    def test_a_send_back_is_the_first_iteration_number_of_two_or_more(self):
        def send_back(session, name):
            return recount_startup.read_subagent(self.FIXTURES / "proj-p" / session / "subagents" / name, "implementer", self.SCAN)["send_back"]
        self.assertEqual([send_back("s-b2", "agent-i1.jsonl"), send_back("s-a1", "agent-i1.jsonl"),
                          send_back("s-a2", "agent-i1.jsonl"), send_back("s-a2", "agent-i2.jsonl")],
                         [False, True, True, False])  # Iteration 1; Iteration 2 ... Iteration 1; Iteration 2; no number

    def test_each_lost_tool_attempt_prints_its_window_role_tool_and_next_call(self):
        self.assertEqual(recount_startup.attempt_lines(self.windows()), [
            "before implementer Skill next Read", "before verifier Agent next none",
            "after implementer Skill next Agent", "after reviewer Skill next Read"])
        # not attempts: Skill in a Reviewer that has it, Skill and Agent in an Implementer that has both, Agent in an
        # Implementer with no shape record, Skill in a Verifier with no shape record; the is_error result is no second one

    def test_the_report_ends_with_the_attempt_lines(self):
        report = recount_startup.window_report(*recount_startup.windowed_sessions(self.FIXTURES, self.SCAN, self.contains), self.SCAN).splitlines()
        self.assertEqual(report[-5:], ["lost-tool attempts (window, role, tool, next tool call):",
                                       "before implementer Skill next Read", "before verifier Agent next none",
                                       "after implementer Skill next Agent", "after reviewer Skill next Read"])

    def test_a_window_with_no_sessions_prints_means_and_shares_without_error(self):
        table = dict(recount_startup.build_table({"empty": {}}))
        self.assertEqual({name: table[name] for name in (
            "session cost mean", "session cost total", "sessions with >1 reviewer", "Hard violations per session",
            "send-backs per session", "lost-tool attempts")},
            {"session cost mean": ["-"], "session cost total": ["$0.00"], "sessions with >1 reviewer": ["0/0"],
             "Hard violations per session": ["-"], "send-backs per session": ["-"], "lost-tool attempts": ["0"]})


class RecountStartupVerdictTests(unittest.TestCase):
    """The verdict over the grilling preview of 2026-11-22 (Spec, Verdict): each role's after p90 against its before p10."""
    BEFORE = {"planner": 25293, "implementer": 29453, "reviewer": 25120, "verifier": 26793}
    AFTER = {"planner": 20929, "implementer": 24652, "reviewer": 19770, "verifier": 22616}

    def test_dropped_when_every_role_separates(self):
        self.assertEqual(recount_startup.verdict(self.BEFORE, self.AFTER, 0), "dropped")

    def test_a_tie_is_not_dropped_and_one_below_it_is(self):
        self.assertEqual(recount_startup.verdict(self.BEFORE, {**self.AFTER, "reviewer": 25120}, 0), "not dropped")
        self.assertEqual(recount_startup.verdict(self.BEFORE, {**self.AFTER, "reviewer": 25119}, 0), "dropped")

    def test_one_overlapping_role_is_not_dropped(self):
        self.assertEqual(recount_startup.verdict(self.BEFORE, {**self.AFTER, "verifier": 30000}, 0), "not dropped")

    def test_a_role_missing_from_a_window_is_not_dropped(self):
        self.assertEqual(recount_startup.verdict(self.BEFORE, {**self.AFTER, "planner": None}, 0), "not dropped")
        self.assertEqual(recount_startup.verdict({**self.BEFORE, "implementer": None}, self.AFTER, 0), "not dropped")
        self.assertEqual(recount_startup.verdict({}, {}, 0), "not dropped")

    def test_a_lost_tool_attempt_fails_whatever_the_percentiles_say(self):
        self.assertEqual(recount_startup.verdict(self.BEFORE, self.AFTER, 1), "failed")
        self.assertEqual(recount_startup.verdict(self.BEFORE, {**self.AFTER, "verifier": 30000}, 3), "failed")

    @staticmethod
    def window(requests, lost=()):
        """One session whose sub-agents have the given first requests per role, the first one with the lost-tool attempts."""
        agents = [{"role": role, "first_request": n, "lost": []} for role, ns in requests.items() for n in ns]
        agents[0]["lost"] = list(lost)
        return {("proj", "s"): {"agents": agents, "cost": 0.0}}

    def test_report_prints_the_verdict_beside_the_percentiles_it_judged(self):
        # before p10 of [100, 200] is 110 (linear interpolation); after p90 of [90, 100] is 99
        before = self.window({role: [100, 200] for role in recount_startup.ROLES})
        after = self.window({role: [90, 100] for role in recount_startup.ROLES})
        self.assertEqual(recount_startup.verdict_report({"before": before, "after": after, "mixed": {}}).splitlines(), [
            "verdict: dropped", "planner: before p10 110, after p90 99", "implementer: before p10 110, after p90 99",
            "reviewer: before p10 110, after p90 99", "verifier: before p10 110, after p90 99",
            "lost-tool attempts in the after window: 0"])

    def test_report_fails_on_an_after_attempt_and_ignores_the_mixed_window(self):
        before = self.window({role: [100, 200] for role in recount_startup.ROLES})
        after = self.window({role: [90, 100] for role in recount_startup.ROLES}, lost=[("Skill", None), ("Agent", "Read")])
        mixed = self.window({"planner": [500]}, lost=[("Skill", None)])
        report = recount_startup.verdict_report({"before": before, "after": after, "mixed": mixed}).splitlines()
        self.assertEqual((report[0], report[-1]), ("verdict: failed", "lost-tool attempts in the after window: 2"))
        report = recount_startup.verdict_report({"before": before, "after": self.window({"planner": [90]}), "mixed": mixed}).splitlines()
        self.assertEqual((report[0], report[2], report[-1]), (
            "verdict: not dropped", "implementer: before p10 110, after p90 -", "lost-tool attempts in the after window: 0"))


class RecountStartupNoiseTests(unittest.TestCase):
    """The noise list over throwaway git repos with fixed dates; the span is 2026-11-07T01:47:33Z to 2026-11-20T00:00:00Z,
    the suite's from the before window's start. Reviewers, hand-counted from the fixtures. recount-startup-passes, before:
    b1's r1 (claude-sonnet-4-6, handback), b1's r2 (claude-sonnet-4-6, plain text), b2's r1 (no model on its records,
    handback); after: one claude-sonnet-4-6 with a handback; no mixed Reviewer. recount-startup: one plain-text
    claude-sonnet-4-6 before, two after (s-new's; the one in s-late is stamped after the scan), no mixed Reviewer."""
    commit = NoiseCommitTests.commit
    SCAN = metrics._time("2026-11-20T00:00:00Z")
    PASSES = HERE / "fixtures" / "recount-startup-passes"
    STARTUP = HERE / "fixtures" / "recount-startup"

    @staticmethod
    def contains(sha):
        return {"aaaaaaaaaaaa": False, "bbbbbbbbbbbb": True}.get(sha)

    def head(self, repo):
        return subprocess.run(["git", "log", "-1", "--format=%h"], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()

    def repos(self, tmp):
        """A skills repo and a suite repo; returns both paths and the short SHAs of the commits the lists must name."""
        repo, suite = Path(tmp) / "skills", Path(tmp) / "suite"
        for path in (repo, suite):
            path.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=path, check=True, capture_output=True)
        self.commit(repo, "agents/implementer.md", "before the push", "2026-11-07T01:00:00Z")
        self.commit(repo, "skills/implement/SKILL.md", "inside, listed folder", "2026-11-08T10:00:00Z")
        self.commit(repo, "README.md", "inside, unlisted path", "2026-11-09T10:00:00Z")
        self.commit(repo, "agents/reviewer.md", "inside, listed file", "2026-11-10T10:00:00Z")
        listed = self.head(repo)
        self.commit(repo, "agents/verifier.md", "after the scan time", "2026-11-20T00:00:01Z")
        self.commit(suite, ".agents/refs/models.md", "before the before window", "2026-10-20T10:00:00Z")
        self.commit(suite, ".agents/refs/models.md", "trial on Sonnet", "2026-11-06T20:06:44Z")
        trial = self.head(suite)
        self.commit(suite, "README.md", "inside, unlisted path", "2026-11-07T10:00:00Z")
        self.commit(suite, ".agents/refs/models.md", "after the scan time", "2026-11-21T10:00:00Z")
        return repo, suite, listed, trial

    def windows(self, root):
        return recount_startup.windowed_sessions(root, self.SCAN, self.contains)[0]

    def test_lists_each_part_and_names_the_commits_it_calls_out(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, suite, listed, trial = self.repos(tmp)
            with unittest.mock.patch.dict(recount_startup.CALLED_OUT, clear=True, values={listed: "the first note", "0000000": "the missing one"}), \
                    unittest.mock.patch.object(recount_startup, "TRIAL_SHA", trial):
                lines = recount_startup.noise_report(self.windows(self.PASSES), repo, suite, self.SCAN).splitlines()
        self.assertEqual(lines[:4], [
            "skills commits touching the implement, code-review or agent files, 2026-11-07T01:47:33Z to 2026-11-20T00:00:00Z:",
            f"{listed} 2026-11-10 inside, listed file", f"{lines[2].split()[0]} 2026-11-08 inside, listed folder",
            f"called out: {listed} 2026-11-10 inside, listed file: the first note"])
        self.assertEqual(lines[4], "called out: 0000000 (not found): the missing one")
        self.assertTrue(lines[5].startswith("mvdmio-suite commits touching the models ref, 20"))
        self.assertTrue(lines[5].endswith(" to 2026-11-20T00:00:00Z:"))
        self.assertEqual(lines[6:], [
            f"{trial} 2026-11-06 trial on Sonnet",
            f"called out: {trial} 2026-11-06 trial on Sonnet: {recount_startup.TRIAL_NOTE}",
            "reviewer models before: claude-sonnet-4-6 2, unknown 1", "reviewer models after: claude-sonnet-4-6 1",
            "reviewer models mixed: none",
            "reviewers ending with SubagentHandback before: 2/3 (66.7%)", "reviewers ending with SubagentHandback after: 1/1 (100.0%)",
            "reviewers ending with SubagentHandback mixed: 0/0",
            "the Reviewer handback share fell without any commit here; its cause is unknown"])

    def test_an_unreadable_suite_and_an_empty_span_say_so(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.repos(tmp)[0]
            lines = recount_startup.noise_report(self.windows(self.PASSES), repo, Path(tmp) / "missing", self.SCAN - 20 * 86400).splitlines()
        called = len(recount_startup.CALLED_OUT)  # the two named commits are not in the throwaway repo
        self.assertEqual(lines[0], "skills commits touching the implement, code-review or agent files, "
                                   "2026-11-07T01:47:33Z to 2026-10-31T00:00:00Z:")
        self.assertEqual(lines[1], "none")
        self.assertTrue(lines[2 + called].startswith("mvdmio-suite commits touching the models ref, "))
        self.assertTrue(lines[2 + called].endswith(": could not be read"))
        self.assertEqual(lines[3 + called], f"called out: {recount_startup.TRIAL_SHA} (not found): {recount_startup.TRIAL_NOTE}")

    def test_reviewer_models_and_handbacks_over_the_other_fixture_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            lines = recount_startup.noise_report(self.windows(self.STARTUP), Path(tmp) / "a", Path(tmp) / "b", self.SCAN).splitlines()
        self.assertEqual(lines[-7:-1], [
            "reviewer models before: claude-sonnet-4-6 1", "reviewer models after: claude-sonnet-4-6 2", "reviewer models mixed: none",
            "reviewers ending with SubagentHandback before: 0/1 (0.0%)", "reviewers ending with SubagentHandback after: 0/2 (0.0%)",
            "reviewers ending with SubagentHandback mixed: 0/0"])


if __name__ == "__main__":
    unittest.main()
