"""Tests for the benchmark tooling, on synthetic data only: python benchmark/test_benchmark.py"""
import csv
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import collect  # noqa: E402
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
        code, log = self.run_guard("log", "step 6: git push origin master:master")
        self.assertEqual(code, 0)
        self.assertIn("NOOP step 6: git push origin master:master", log)

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
        self.assertEqual(sorted(roles), ["fixer", "implementer", "main", "prover", "reviewer"])
        self.assertAlmostEqual(roles["implementer"]["cost_usd"], 0.01626, places=6)
        self.assertEqual(roles["main"]["calls"], 2)
        self.assertEqual(self.m["subagents"], 4)

    def test_context_wall_time_and_checks(self):
        self.assertEqual(self.m["max_context"], 6020)
        self.assertEqual(self.m["wall_s"], 330.0)
        self.assertEqual(self.m["tool_errors"], 1)
        self.assertEqual(self.m["test_commands"], 1)
        self.assertEqual(self.m["prover_status"], "held")


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
                           ({"plugin_verified": False}, "not the plugin")):
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
            (repo / ".agents" / "steps").mkdir(parents=True)
            (repo / ".agents" / "steps" / "01.md").write_text("step\n" * 50)
            git("add", "."), git("commit", "-q", "-m", "Add lines (#7)")
            (run / "bench.log").write_text("2026-01-01T00:00:00 NOOP step 6: git push\n")
            ok = f'"{sys.executable}" -c "print(\'Passed!  - Failed: 0, Passed: 2, Skipped: 0, Total: 2\')"'
            spec = {"base": base, "issue": 7, "landing_lines": 4, "build": [ok], "tests": [ok]}
            meta = {"worktree": str(repo), "exit_code": 0, "plugin_verified": True}
            m = {"subagents": 3, "test_commands": 2, "unpriced_models": [], "prover_status": "held"}
            s = score.score_run(run, meta, spec, m)
            self.assertEqual((s["landed"], s["commits"], s["landing_lines"], s["diff_ratio"]), (True, 1, 2, 0.5))
            self.assertEqual((s["build_ok"], s["tests_ok"], s["tests_run"], s["noop_writes"], s["proof"]), (True, True, 2, 1, "held"))
            self.assertTrue(s["valid"], s["invalid_reasons"])


class RunnerTests(unittest.TestCase):
    def test_argv_pins_settings_and_ends_with_the_variadic_flag(self):
        settings = run.Settings("sonnet", "high", "claim", claude_cmd=["claude"])
        argv = run.build_argv(settings, {"issue": 394}, "/skills", "sid", "/mcp.json")
        self.assertEqual(argv[:3], ["claude", "-p", "/implement #394"])
        for pair in (["--model", "sonnet"], ["--effort", "high"], ["--plugin-dir", "/skills"], ["--session-id", "sid"]):
            self.assertEqual(argv[argv.index(pair[0]) + 1], pair[1])
        self.assertIn("--strict-mcp-config", argv)
        self.assertEqual(argv[argv.index("--disallowedTools") + 1:], guards.DENIED_TOOLS)

    def test_the_plugin_under_test_must_be_the_one_that_loaded(self):
        init = {"plugins": [{"name": "skills", "path": "/a/skills"}]}
        self.assertTrue(run.plugin_verified(init, "/a/skills"))
        self.assertFalse(run.plugin_verified(init, "/b/skills"))
        self.assertIsNone(run.plugin_verified({}, "/a/skills"))
        both = {"plugins": [{"name": "skills", "path": "/a/skills"}, {"name": "skills", "path": "/installed"}]}
        self.assertIsNone(run.plugin_verified(both, "/a/skills"))

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
