"""Tests for the benchmark tooling, on synthetic data only: python benchmark/test_benchmark.py"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import guards  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
