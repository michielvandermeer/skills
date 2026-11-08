#!/usr/bin/env python3
"""Print the lines a resumed /implement run owes the user.

    resume.py SLUG [--spec SPEC] [--issue BODY] [--halt HALT]

Prints `Resuming from the Halt record: <count> findings` when HALT exists, where count is the
number of `- ` bullets in HALT's first list, a lone `- none` not counted. The lists are told apart
by their `## ` headings; a record with no `## ` heading, as older records have, has them told apart
by the unindented line that follows a blank line.

Prints the Issue-changed line when SPEC and BODY both exist and differ. SPEC's H1 and one blank
line after it are dropped; BODY is the Issue's body as the Tracker returned it. Only line endings,
trailing whitespace on each line, and trailing blank lines are ignored. Prints nothing when
neither applies; exits 0.
"""
import argparse
import re
import sys
from pathlib import Path

NEWLINE = r"\r\n|\r|\n"


def lines_of(text):
    lines = [line.rstrip() for line in re.split(NEWLINE, text)]
    while lines and not lines[-1]:
        lines.pop()
    return lines


def read(path):
    return Path(path).read_text(encoding="utf-8-sig")


def spec_body(text):
    lines = re.split(NEWLINE, text)[1:]
    if lines and not lines[0].strip():
        lines = lines[1:]
    return "\n".join(lines)


def halt_findings(text):
    lines = re.split(NEWLINE, text)
    if any(line.startswith("## ") for line in lines):
        starts = [line.startswith("## ") for line in lines]
    else:
        starts = [
            line and not line[0].isspace() and not line.startswith(("#", "- ")) and (i == 0 or not lines[i - 1].strip())
            for i, line in enumerate(lines)
        ]
    if True not in starts:
        return 0
    first = starts.index(True) + 1
    end = starts.index(True, first) if True in starts[first:] else len(lines)
    return sum(1 for line in lines[first:end] if re.match(r"- (?!none\s*$)", line))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("slug")
    parser.add_argument("--spec")
    parser.add_argument("--issue")
    parser.add_argument("--halt")
    args = parser.parse_args()

    if args.halt and Path(args.halt).is_file():
        print(f"Resuming from the Halt record: {halt_findings(read(args.halt))} findings")
    if args.spec and args.issue and Path(args.spec).is_file() and Path(args.issue).is_file():
        if lines_of(spec_body(read(args.spec))) != lines_of(read(args.issue)):
            print(
                "The Issue changed after this run started. This run builds the text it started with. "
                f"To build the new text, delete branch {args.slug} and its worktree, then run /implement again."
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
