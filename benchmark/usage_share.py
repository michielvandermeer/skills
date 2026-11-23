"""The share of the weekly Claude limit a measurement used, from Claude Code's status line input.

Every run passes a status line command in its --settings. Claude Code feeds it JSON, and when that JSON carries
rate_limits.seven_day.used_percentage the command appends the value and a timestamp to a capture file in the run's
folder. A measurement's share is the last value minus the first across its capture files. Other sessions on the
same account move the figure too, so a share is an upper bound.

  python usage_share.py capture <file>      status line mode: reads the status line JSON from stdin"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve()


def status_line_command(capture_file):
    return f'"{Path(sys.executable).as_posix()}" "{HERE.as_posix()}" capture "{Path(capture_file).resolve().as_posix()}"'


def capture(path, stdin_text):
    try:
        value = json.loads(stdin_text)["rate_limits"]["seven_day"]["used_percentage"]
    except (ValueError, KeyError, TypeError):
        return
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')}\t{value}\n")


def read_values(path):
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    values = []
    for line in lines:
        try:
            values.append(float(line.split("\t")[1]))
        except (IndexError, ValueError):
            pass
    return values


def share(paths):
    """Last value minus the first across the files, in the order given; None when a file is missing or holds no value."""
    per_file = [read_values(p) for p in paths]
    if not per_file or not all(per_file):
        return None
    return per_file[-1][-1] - per_file[0][0]


def main(argv):
    if argv[:1] == ["capture"] and len(argv) == 2:
        sys.stdin.reconfigure(encoding="utf-8")
        capture(argv[1], sys.stdin.read())
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
