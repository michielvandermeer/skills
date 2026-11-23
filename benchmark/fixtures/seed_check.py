"""The Spec's `tests` command in the recorder test: test_a fails unless a.txt in the current folder has its third line."""
from pathlib import Path

text = Path("a.txt").read_text()
print("FAILED test_a" if "three" not in text else "passed test_a")
print("Passed!  - Failed: 0, Passed: 2, Skipped: 0, Total: 2")
