# `/wizard` is model-invoked so the agent can start it

Typed commands in this plugin are often user-invoked. `/wizard` is model-invoked: the agent starts it when it hits a step only a person can do, instead of pasting dashboard steps into the chat. User-invoked was rejected: the skill exists to stop those pasted steps, and that only works if the agent can reach it without the user remembering to type `/wizard`.

## Consequences

- The skill's description stays loaded on every turn and carries the jobs it covers.
- Other skills' bodies do not start `/wizard`. The agent can still reach it from the description.
- `/wizard` stays off the Named session skill list ([ADR-0038](0038-named-session-skills-apply-high-priority-retro.md)).
