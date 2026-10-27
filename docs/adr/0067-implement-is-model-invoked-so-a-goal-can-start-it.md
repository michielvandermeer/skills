# `/implement` is model-invoked so a goal can start it

`/implement` is model-invoked. A `/goal` session works toward its condition without the user typing, so it can start a skill only through the Skill tool, and the host refuses that call for a user-invoked skill. A goal that names `/implement` could therefore never run it. The description fires only when the user or a `/goal` names the command, so a plain request to build something still does not start a run.

## Considered Options

- **Keeping it user-invoked.** Rejected: a `/goal` session cannot run it at all.
- **A goal that follows `/implement` by path**, as skills follow `/retro` and the Library skills ([ADR-0074](0074-skills-other-skills-follow-are-read-by-path.md)). Rejected: following by path skips the Sonnet pin, so the run would go on at the goal session's model.
- **A description that fires on any request to build something.** Rejected: an implement run claims the Issue, opens a worktree, and pushes, which nobody should get from asking for a small change.

## Consequences

- Its description stays loaded on every turn.
- It keeps its pin to Sonnet at high ([ADR-0049](0049-agents-are-pinned-in-their-agent-files.md)). Starting it switches the session to that model for the rest of the turn, which is the setting the run is meant to have.
- No skill's step starts `/implement`. A skill that ends where an implement run would start tells the user to run it.
