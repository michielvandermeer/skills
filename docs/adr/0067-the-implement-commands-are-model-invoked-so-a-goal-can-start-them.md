# The implement commands are model-invoked so a goal can start them

`/implement` and `/implement-yolo` are model-invoked. A `/goal` session works toward its condition without the user typing, so it can start a skill only through the Skill tool, and the host refuses that call for a user-invoked skill. A goal that names an implement command could therefore never run it. Each description fires only when the user or a `/goal` names that command, so a plain request to build something still does not start a run.

## Considered Options

- **Keeping them user-invoked.** Rejected: a `/goal` session cannot run them at all.
- **One model-invoked router that starts the two.** Rejected: a skill cannot start a user-invoked skill either, so the router would hit the same refusal.
- **Descriptions that fire on any request to build something.** Rejected: an implement run claims the Issue, opens a worktree, and pushes, which nobody should get from asking for a small change.

## Consequences

- Two descriptions stay loaded on every turn.
- Each keeps its pin to Opus at high ([ADR-0049](0049-agents-are-pinned-in-their-agent-files.md)). Starting one switches the session to that model for the rest of the turn, which is the setting the run is meant to have.
- No skill's step starts an implement command, because the pin would swap the calling skill's model. A skill that ends where an implement run would start tells the user to run it, as before.
- A `/goal` that named `/implement-oneshot` names `/implement` now ([ADR-0054](0054-the-implement-commands-differ-only-in-the-worktree.md)).
