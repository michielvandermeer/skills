"""Tests for the benchmark tooling, on synthetic data only: python benchmark/test_benchmark.py"""
import csv
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import collect  # noqa: E402
import compare  # noqa: E402
import guards  # noqa: E402
import metrics  # noqa: E402
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


if __name__ == "__main__":
    unittest.main()
