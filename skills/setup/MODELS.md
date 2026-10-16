# Models

Write or update `.agents/refs/models.md`, the **Models ref**: the model and effort each of the plugin's agents runs at in this repo. An agent's own header holds its default pin ([ADR-0049](../../docs/adr/0049-agents-are-pinned-in-their-agent-files.md)); a row in the Models ref overrides it on every dispatch. A skill's own pin stays as its header sets it, since the host picks a skill's model before any repo file is read.

## 1. Read what is there

- Each agent file in [../../agents/](../../agents/): its `name:`, `model:`, and `effort:`. These are the defaults.
- `.agents/refs/models.md`. When it exists, this run is an update, and its rows are the current values. A row for an agent the plugin no longer ships is dropped; an agent without a row takes its default.
- The repo's `AGENTS.md` and `CLAUDE.md`, for the pointer line [below](#the-models-ref).

Done: every agent has a default and a current value.

## 2. Choose

Show the table — agent, model, effort — with each row whose current value differs from its default marked, and each dropped row listed under it. Ask, in one round, which rows to change.

- A model is a name the Agent tool's `model` parameter accepts in this session.
- An effort is `low`, `medium`, `high`, `xhigh`, or `max`.

An answer outside those lists is asked again. Show the changed table and wait for a yes.

Done: the user said yes to the table.

## 3. Apply

1. Write `.agents/refs/models.md` in the shape below, the whole file, so a re-run gives the same file.
2. Add the pointer line to the instruction file the host loads at every session start — on Claude Code, `CLAUDE.md` or an `AGENTS.md` it includes — unless that file already carries it. A repo with neither gets a new `CLAUDE.md`.
3. Commit both, staged by name, in one commit.

Done: the commit exists.

## 4. Report

Name the ref's path, each row that differs from its default, and whether the pointer line was added or already there.

Done: the report names the path, every changed row, and the pointer line.

## The Models ref

The file, with one row per agent in [../../agents/](../../agents/):

```markdown
# Models

The model and effort each of the `skills` plugin's agents runs at in this repo. When you dispatch one, pass its row's model as `model` and its effort as `effort` on the Agent call, also when the host lacks the agent type and dispatches `general-purpose` in its place. A host whose dispatch takes no effort gets the model only. An agent without a row runs at the pin in its own header. `/setup models` changes this file.

| Agent | Model | Effort |
|---|---|---|
| `skills:planner` | sonnet | high |
```

The pointer line:

```markdown
- `.agents/refs/models.md`: the model and effort for each `skills:` agent. Read it before dispatching one.
```
