# A Step names its Workflow

Every Step file carries a `Workflow:` line: `feature`, `bug-fix`, `refactor`, `perf`, or `visual-parity`. The Planner picks it per Step. Under `/implement-oneshot` and `/implement-yolo` the Driving session picks it for the one Step it writes, so the three commands still differ only in planning and worktree ([ADR-0054](0054-the-implement-commands-differ-only-in-planning-and-worktree.md)). `skills/implement/WORKFLOWS.md` holds one section per Workflow: the Step agent's first move, what the Safety fact names, a fourth Outcome line, and what the Checker checks beyond the Proof. It also holds the rules every Step keeps. The Step agent and the Checker read that shared section and their own Workflow's section, and nothing else of the file.

The rules adapt the implementation playbooks of pstack's `/poteto-mode`: Feature, Bug fix, Refactoring, Perf issue, and Visual parity. A bug fix starts from a repro that goes red, and its Checker sees that repro fail on the starting code. A refactor starts from a pin that holds behaviour. A perf change starts from a baseline measurement, and a visual-parity change from a frozen screenshot baseline. Before this, every Step ran as a feature. A bug fix could then land with a test that never failed without the fix, and a perf change could land on a reading of the source.

The Workflows add no sub-agent dispatch. Each runs inside the Step agent and the Checker that the run already sends.

## Considered Options

- **One Workflow per run.** Rejected: a bug-fix run often needs a prefactor first, which is a `refactor` Step, and a Wide refactor's stages are `refactor` Steps inside a `feature` Spec.
- **A command per Workflow, such as `/implement-bugfix`.** Rejected: the commands would differ in more than planning and worktree, and each would carry the same flow.
- **pstack's design fan-out per Step: `/architect`, `/arena`, parallel candidates.** Rejected: the Spec settled the design before the run, and each fan-out multiplies what a Step costs. `/codebase-design` and `/prototype` explore designs before a Spec exists.
- **Copy pstack's principle skills into this repo.** Rejected: the agents need only the rules that change what they do, and twenty-five skills would add a description each to every session's context.
- **Prototype and Hillclimb as Workflows.** Rejected: `/prototype` and `/hillclimb` already run them, and neither ends in a Spec-built Step.

## Consequences

- The Outcome entry has four lines. The final report holds every workflow line, and the landing commit's body carries each `Root cause:` and `Measure:` line.
- A Step file written before this change has no `Workflow:` line and runs as `feature`, so a resumed run goes on unchanged.
- A new Workflow is a row in the table and a section in `WORKFLOWS.md`. Its workflow line's label also goes in the final report's `grep` in all three implement skills.
