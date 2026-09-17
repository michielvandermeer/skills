# The Planner is a named plugin agent

Status: ready-for-agent

## Problem Statement

You typed `/implement`. The run stopped. It said the Planner did not return the step list, and no Step files were written.

That reply should not be possible. The slicing rules already say: write the Step files, commit them, and return only the compact index.

What happened is a type collision. `/implement` says "dispatch a planner" and does not name an agent type. The host has a built-in planning agent. The Driving session picks that type because the names match. That built-in agent cannot write files. Its job is to produce a design document. So it walks the code, returns a long write-up, and the run halts.

This happened in more than one session. Re-invoking `/implement` with the same argument runs the same untyped dispatch again.

## Solution

The Driving session dispatches the Planner as a named plugin agent, the same way it already dispatches a Step agent as the named implementer.

That plugin agent can write files. It reads the slicing rules the prompt already names, writes the Step files, commits them, and returns only the index.

It is not the host's built-in planning agent. A host that does not have the plugin agent uses a general-purpose agent that can write files, still not the host's built-in planning agent.

The halt rule stays. A reply that is not the index, or a missing steps directory, still stops the run. This change makes that halt a follow-the-rules failure, not the default on every host that ships a planning type.

## User Stories

1. As a developer, I want `/implement` to write Step files on the first Planner pass, so the run can start building instead of halting with an empty steps directory.

2. As a developer, I want the Planner to return the compact index and nothing else, so the Driving session can treat that reply as success.

3. As a developer, I want that index to match the Step files on disk, so a later resume finds the same plan the Driving session holds.

4. As a Driving session, I want an explicit agent type for the Planner, so I do not have to guess which of the host's types "planner" means.

5. As a Driving session, I want that type to be the plugin's named planner agent, so it matches how I already dispatch a Step agent.

6. As a Driving session, I want that agent to be able to write and commit, so it can do the job the slicing rules already name.

7. As a developer, I do not want the host's built-in planning agent used as the Planner, so a type that only reads and writes design documents cannot run this step.

8. As a Driving session on a host that has not loaded the plugin agent, I want to dispatch a general-purpose agent that can write files, so the run still plans instead of failing the spawn.

9. As a Driving session on that fallback, I still do not want the host's built-in planning agent, so the name collision cannot return through the fallback.

10. As a developer, I want the Planner to keep running at this session's own model and effort, so slicing a Spec is still paid as judgement work, not as a cheaper spec-bound pass.

11. As a later reader of the planner agent file, I want it to say how the Planner works — write the files, commit, return only the index — so its identity is not "produce a design document".

12. As a later reader of that file, I want the slicing rules to stay the file the Driving session already hands, so the agent file does not copy the slice, footprint, and tracer-bullet rules.

13. As a Driving session, I still want to hand only the spec path (or the argument text), the slug, and the slicing-rules path, so the Planner still reads those itself.

14. As a developer, I want a Planner that writes no files, or replies with a long note, to still halt the run, so a bad plan is not rescued by a second agent inventing the files.

15. As a developer, I want the Driving session's dirty-directory commit to stay the only write it does in this step, so the Planner still owns the Step files.

16. As a developer who re-invokes `/implement` after this change, I want the named agent to run, so the same slug does not hit the host planning type again.

17. As a developer who runs `/implement-oneshot` or `/implement-yolo`, I want those commands left as they are, so skipping the Planner still skips it.

18. As a developer, I want the fixer and the data-structures pass left as general-purpose, so this change is only the Planner dispatch.

19. As a later reader of the install notes, I want the new agent listed with the others, so the plugin's agent folder matches what the skill dispatches.

20. As a later reader of the cost-tier notes, I want the Planner called out as running at the session's own model and effort, so it is not folded into "every shipped agent is medium effort".

21. As a later reader of the glossary, I want Planner to name the plugin agent and to avoid the host's planning type, so the collision is visible at the definition site.

22. As a later reader of the decision record, I want to know why we did not pin general-purpose alone, and why we did not keep the host planning type, so the next session does not reopen those.

23. As a developer, I want no retry of a Planner that returned a design document, so the halt stays one failure and a re-invoke is the recovery.

24. As a developer, I want leftover gaps in the Spec still closed by the Planner into the Step files, so naming the agent does not change what it writes, only which type runs.

## Implementation Decisions

- `/implement` names the Planner's type the same way it already names the Step agent's type: the plugin's planner agent, at `agents/planner.md`, dispatched as `skills:planner`.

- That file is how the Planner works. It writes the Step files itself. It commits them. Its turn ends with the index, nothing before it and nothing after. It has no user. It does not pin a model or an effort: slicing still runs at the Driving session's own settings ([ADR-0007](../../docs/adr/0007-pinned-subagent-model-tiers.md)).

- The slicing rules stay [STEPS.md](../../skills/implement/STEPS.md). The Driving session still hands that path with the spec (or the argument text) and the slug, and nothing else. The agent file does not copy those rules.

- A host without that agent type dispatches `general-purpose`. It does not dispatch the host's built-in planning type (`plan` / `Plan`).

- The success and halt rules in step 2 stay. The plan succeeded when the reply is the index and the steps directory holds Step files. Otherwise halt. The Driving session still does not dispatch another agent to write or commit those files. The dirty-directory commit stays the only Driving-session write for this step.

- `/implement-oneshot`, `/implement-yolo`, the fixer, and the data-structures pass are unchanged.

- The glossary Planner entry names `skills:planner` and avoids the host's planning type. A new ADR records why the Planner is a named plugin agent rather than the host type or a bare general-purpose dispatch.

- The README agent list and the cost-tier paragraph name the new file. The Planner is not one of the agents pinned at medium effort.

## Testing Decisions

A good check is what the Driving session dispatches, and whether that type can write files. It is not a wording pass on a design document a Planner should never return.

- `/implement` step 2 names `skills:planner` (or `general-purpose` as the fallback), and does not name the host's `plan` / `Plan` type as the Planner.
- `agents/planner.md` exists, has no model or effort pin, and says the turn ends with the index.
- The three-item prompt (spec or argument, slug, slicing-rules path) is unchanged.
- `/implement-oneshot` and `/implement-yolo` still do not dispatch a Planner.
- This repo has no automated suite for skill prose. The check is a read of the dispatch line against the Step-agent dispatch, the way `/validate-spec` already reads a Spec against the current skills. Prior art for "name the plugin agent, not the host built-in" is `skills:explorer` replacing the host Explore type, and `skills:implementer` for Step agents.

## Out of Scope

- Teaching the Driving session to parse a design document for a buried index.
- Letting the Driving session write the Step files from a host planning agent's output.
- Changing the index format, the halt rule, or the dirty-directory commit.
- Pinning the Planner to a cheaper model or to medium effort.
- Changing `/implement-oneshot`, `/implement-yolo`, the fixer, or the data-structures pass.
- Replacing every use of the host's planning agent in other skills.
- Changing how Step agents, explorers, or oneshot agents are dispatched.

## Further Notes

Grok session `01a0b01f-fa5b-70f1-98a4-92e948f0eb50` dispatched `subagent_type: plan` with the three-line prompt. That child cannot write or run a shell. It returned a design write-up with a "Suggested step index" at the end and left the steps directory missing. Session `01a0ac52-27ca-7883-936c-04d83f28954d` hit the same type and stopped on read-only. Both halts are this bug, not a Planner that forgot the index format.
