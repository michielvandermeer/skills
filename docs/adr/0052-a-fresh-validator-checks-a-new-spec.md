# A fresh Validator checks a new Spec

`/to-spec` drafts a Spec in a temporary file, or in the Issue's own file on the local Tracker, and checks it against the repo before it writes the Spec to its Issue. The Driving session dispatches a **Validator** (`skills:validator`) with the draft's path and waits. The Validator runs `/validate-spec` on that path, corrects facts in the file, and returns the report. The Driving session shows the report, writes the corrected draft to the Issue in one update, and then takes its commit step.

The Validator has not watched the Spec get written, so it reads the file. The repo walk stays in the Validator. The Driving session keeps the report.

## Considered Options

Keeping the check in the Driving session was rejected. That session watched the Spec get written, and it would also walk the repo.

Handing the Validator the conversation was rejected. The check would share the assumptions of the session that wrote the Spec.

On a Tracker outside the repo, writing the Spec to its Issue before the check, so the Validator corrects it there, was rejected. People watching the Issue would be notified of an unchecked Spec and again of each correction. A draft file keeps it to one update.

Asking the user to start a second session was rejected. The skills that call `/to-spec` wait for it to finish, and the write and the commit come after the check.

Holding the write and the commit for every open question was rejected. One flagged decision would stop every skill that writes a Spec. The report is shown, and the write and the commit still run.

Running the check in the Driving session after a Validator failure was rejected. The work would return to the session this split is for. A check that does not finish stops the run before the write. Corrections already in the draft stay.

An unnamed sub-agent at the session's own effort was rejected. This check is a Spec-bound dispatch. Those agents are named and run at medium effort.

## Consequences

- `/to-spec` dispatches one Validator per Spec and waits. Skills that call `/to-spec` stay as they are. A `/validate-spec` the user types still runs in the Driving session.
- Open questions leave the write and the commit free to run. The Issue's status becomes `ready-for-agent` or `ready-for-human` in the same update that writes the Spec.
- A Validator that fails, returns no report, or stops short of a finished checklist ends the session before the write. The draft stays as the Validator left it, the write to the Issue does not run, and the glossary and ADR edits stay uncommitted. A later Spec, the caller's commit, and a Retrospective stay unstarted. On a map, a Spec already written to its Issue stays there, and its files stay uncommitted too, because the map's one commit has not run.
- `/review-spec` still runs its check in the Driving session after an approved edit.
- The Validator runs at `effort: medium` on the session's model ([ADR-0049](0049-spec-bound-agents-keep-the-session-model.md)). A host without `skills:validator` dispatches `general-purpose` with the same prompt. That dispatch has no effort pin.
- `/refine` counts this Validator run as the check its done line names.
