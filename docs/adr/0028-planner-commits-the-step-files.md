# The Planner commits the Step files

`/implement` retries and resumes with `git reset --hard && git clean -fd`, and nothing said who committed the Step files the Planner wrote. They stayed untracked until each Step's own agent committed its file, so the clean that a retry or resume runs would have deleted every pending Step and broken the in-flight check that looks for them. The Planner now commits the whole steps directory in one commit before it returns the index; the Driving session commits it itself when that did not happen.

Excluding the steps directory from the clean was rejected: it leaves the Step files at the mercy of whichever agent touches them next. Having each Step agent commit the siblings it finds was rejected: it mixes plan and code in one commit and still leaves a window before step 01.

## Consequences

- A resume after a halt finds every Step file where the Planner left it.
- `git log` on the branch opens with the plan commit.
