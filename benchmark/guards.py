"""Guards that keep a benchmark run local, whatever the skill does.

  gh        shim on PATH: reads pass through to the real gh, every write is refused and logged
  pre-push  git hook: refuses every push and logs it
  bench-log what the skill runs in benchmark mode in place of a write; appends a NOOP line

Every line goes to the file SKILLS_BENCHMARK_LOG names. The scorer counts BLOCKED lines: a run that
tripped a guard did not follow benchmark mode."""
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve()
READ_COMMANDS = {
    ("issue", "view"), ("issue", "list"), ("issue", "status"),
    ("pr", "view"), ("pr", "list"), ("pr", "status"), ("pr", "diff"), ("pr", "checks"),
    ("repo", "view"), ("repo", "list"), ("run", "view"), ("run", "list"),
    ("release", "view"), ("release", "list"), ("label", "list"),
    ("auth", "status"), ("auth", "token"),
}
READ_GROUPS = {"search", "status", "version"}
API_FIELD_FLAGS = {"-f", "-F", "--field", "--raw-field", "--input"}
DENIED_TOOLS = [
    "Bash(git push)", "Bash(git push *)",
    "Bash(gh issue comment *)", "Bash(gh issue edit *)", "Bash(gh issue close *)",
    "Bash(gh issue create *)", "Bash(gh pr create *)", "Bash(gh pr merge *)", "Bash(gh pr comment *)",
    "Bash(gh release *)", "Bash(kamal *)", "Bash(stripe *)",
]


def gh_is_read_only(args):
    words, method, has_fields, skip = [], None, False, False
    for i, arg in enumerate(args):
        if skip:
            skip = False
        elif arg in ("-R", "--repo"):
            skip = True
        elif arg in ("-X", "--method") and i + 1 < len(args):
            method = args[i + 1].upper()
            skip = True
        elif arg.startswith("--method=") or (arg.startswith("-X") and len(arg) > 2):
            method = arg.split("=")[-1].removeprefix("-X").upper()
        elif arg in API_FIELD_FLAGS or arg.startswith(("--field=", "--raw-field=", "--input=", "-f", "-F")):
            has_fields = True
        elif arg in ("-h", "--help", "--version"):
            return True
        elif not arg.startswith("-"):
            words.append(arg)
    if not words:
        return True
    if words[0] == "api":
        if any(w.startswith("graphql") for w in words[1:]):
            return False
        return method == "GET" or (method is None and not has_fields)
    return words[0] in READ_GROUPS or tuple(words[:2]) in READ_COMMANDS


def log(line):
    path = os.environ.get("SKILLS_BENCHMARK_LOG")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')} {line}\n")


def run_gh(args):
    if gh_is_read_only(args):
        shim = os.path.normcase(os.environ.get("BENCH_GUARD_BIN", ""))
        path = os.pathsep.join(p for p in os.environ.get("PATH", "").split(os.pathsep) if os.path.normcase(p) != shim)
        real = shutil.which("gh", path=path)
        if not real:
            print("benchmark: no real gh on PATH", file=sys.stderr)
            return 127
        return subprocess.call([real, *args])
    log("BLOCKED gh " + " ".join(args))
    print("benchmark: this gh command writes, so the benchmark shim refused it", file=sys.stderr)
    return 1


def main(argv):
    mode, rest = argv[0], argv[1:]
    if mode == "gh":
        return run_gh(rest)
    if mode == "prepush":
        log("BLOCKED git push " + " ".join(rest))
        print("benchmark: pushes are refused", file=sys.stderr)
        return 1
    if mode == "log":
        log("NOOP " + " ".join(rest))
        return 0
    return 2


def install(dest, log_path):
    """Write the shims and the hook under dest; return the environment a run needs on top of its own."""
    dest = Path(dest).resolve()
    bin_dir, hooks = dest / "bin", dest / "hooks"
    bin_dir.mkdir(parents=True, exist_ok=True)
    hooks.mkdir(parents=True, exist_ok=True)
    py, me = Path(sys.executable).as_posix(), HERE.as_posix()
    for name, mode in (("gh", "gh"), ("bench-log", "log")):
        _write(bin_dir / name, f'#!/bin/sh\nexec "{py}" "{me}" {mode} "$@"\n')
        _write(bin_dir / f"{name}.cmd", f'@echo off\r\n"{py}" "{me}" {mode} %*\r\n')
    _write(hooks / "pre-push", f'#!/bin/sh\nexec "{py}" "{me}" prepush "$@"\n')
    return {
        "PATH": str(bin_dir) + os.pathsep + os.environ.get("PATH", ""),
        "BENCH_GUARD_BIN": str(bin_dir),
        "SKILLS_BENCHMARK": "1",
        "SKILLS_BENCHMARK_LOG": str(log_path),
        # env config outranks the repo's own, so no worktree the run makes can push
        "GIT_CONFIG_COUNT": "2",
        "GIT_CONFIG_KEY_0": "core.hooksPath", "GIT_CONFIG_VALUE_0": str(hooks),
        "GIT_CONFIG_KEY_1": "remote.origin.pushurl", "GIT_CONFIG_VALUE_1": "benchmark-no-push://refused",
        "GIT_TERMINAL_PROMPT": "0",
    }


def _write(path, text):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    path.chmod(0o755)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
