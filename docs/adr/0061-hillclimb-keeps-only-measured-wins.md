# A Hillclimb keeps only measured wins, and runs as an implement route

A **Hillclimb** pushes one measured number in one direction, such as how long a test suite takes. It tries one change at a time and keeps a change only when the measurement shows it helped and the tests still pass. The method is the `poteto-mode` skill's Hillclimb playbook. `/implement` routes a Spec that names a number to push toward a target to that playbook and lands the result like any run. A plain request reaches the same playbook through poteto-mode and ends in a pull request. The plugin has no `/hillclimb` skill.

The need came back four times in six weeks, all on the `mvdmio-suite` test suite, and each time the method was carried by hand: in a long `/goal` prompt, in an agent memory file, in a handoff prompt. A `/hillclimb` skill with its own Climber agent and a committed Attempt log first ended that, because the implement run of the time built Steps planned up front and could not try a change, measure it, and throw it away. An implement run is now a poteto-mode playbook ([ADR-0069](0069-an-implement-run-is-a-poteto-mode-playbook.md)), and poteto-mode's Hillclimb playbook is that loop. The skill copied `/implement`'s worktree entry, run scratch, and landing passages, and those copies drifted until #21 brought them back in line. One route keeps one copy.

What those four efforts learned still holds, now in the playbook and the route:

- **One Attempt at a time.** One run on a shared machine swings by ±50% when other sessions are busy. Both sides are measured in the same hour, with the median of several runs, and an implement run's one-writer rule keeps Attempts from running side by side and measuring each other's load.
- **The agent that wrote a change never judges it.** A delegate writes each Attempt and commits it as one unit; the Driving session measures it, runs the tests, and keeps it or resets it off the branch.
- **A target and a minimum number of Attempts decide when to stop.** Both `/goal` rounds read "max 8 hours" as a ceiling and stopped after 2 to 2.5 hours, and a target alone lets one lucky early win end the effort.
- **What was tried lands in git.** Most of what each effort learned was what not to try again. The decision log sits in the Run directory, which git ignores, so the landing commit's body carries the baseline, the final number, each kept Attempt with its before and after, and each reverted idea with why it failed.

## Considered Options

- **Keep `/hillclimb` beside the route.** Rejected: two methods for one loop, and the skill's copies of the implement passages drift.
- **Route a Spec that names a number to the Perf issue playbook.** Rejected: Perf issue fixes one measured slowness once. It has no loop and no stop rule.
- **Keep the Attempt log committed under `.agents/hillclimbs/<slug>/`.** Rejected: the landing commit already puts the kept and reverted Attempts in `git log`, which every host reads, and the folder was one more document kind for a few efforts a year.
- **No method in the plugin: write it into a `/goal` prompt or a Spec each time.** Rejected: that is the hand-carrying the four efforts suffered. The Spec now names only the number, its target, and the tests that must keep passing.

## Consequences

- The Climber agent, the measurement rules in `MEASURE.md`, and the `.agents/hillclimbs/` document kind are gone. The `benchmark-checklist` skill vets the playbook's harness. A Hillclimb folder that already exists stays as a record.
- A Hillclimb that `/implement` runs lands as one landing commit ([ADR-0062](0062-an-implement-run-lands-as-one-commit.md)), and starts `/retro` under the run's usual trigger. A reverted Attempt is not a `revert` in the trail, because reverting is how a Hillclimb works.
- The delegates run on the operator's `hillclimb` model line, Opus by default ([ADR-0049](0049-agents-are-pinned-in-their-agent-files.md)).
