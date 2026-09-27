# A fresh Validator checks a new Spec

`/to-spec` writes a Spec and then checks it against the repo. That check used to run in the Driving session, which already held the conversation and the Spec. The Driving session now dispatches a **Validator** (`skills:validator`) with the Spec's path and waits. The Validator runs `/validate-spec` from that path, corrects facts in the file, and returns the report. The Driving session shows the report and then takes the commit step it already had.

The Validator has not watched the Spec get written, so it reads the file. The repo walk stays in the Validator. The Driving session keeps the report.

## Considered Options

Keeping the check in the Driving session was rejected. That session watched the Spec get written, and it would also walk the repo.

Handing the Validator the conversation was rejected. The check would share the assumptions of the session that wrote the Spec.

Asking the user to start a second session was rejected. The skills that call `/to-spec` wait for it to finish, and the commit comes after the check.

Holding the commit for every open question was rejected. One flagged decision would stop every skill that writes a Spec. The report is shown, and the existing commit step still runs.

Running the check in the Driving session after a Validator failure was rejected. The work would return to the session this split is for. A check that does not finish stops the run before the commit. Corrections already in the file stay.

An unnamed sub-agent at the session's own effort was rejected. This check is a Spec-bound dispatch. Those agents are named and run at medium effort.

## Consequences

- `/to-spec` dispatches one Validator per Spec and waits. Skills that call `/to-spec` stay as they are. A `/validate-spec` the user types still runs in the Driving session.
- Open questions leave the commit step free to run. The Spec keeps the `ready-for-agent` line `/to-spec` wrote before the check.
- A Validator that fails, returns no report, or stops short of a finished checklist ends the session before that step. The Spec and the glossary and ADR edits that step would have committed stay uncommitted. A later Spec, the caller's commit, and a Retrospective stay unstarted. On a map, a Spec whose check already finished stays uncommitted too, because the map's one commit has not run.
- `/review-spec` still runs its check in the Driving session after an approved edit.
- The Validator runs at `effort: medium` on the session's model ([ADR-0049](0049-spec-bound-agents-keep-the-session-model.md)). A host without `skills:validator` dispatches `general-purpose` with the same prompt. That dispatch has no effort pin.
- `/refine` counts this Validator run as the check its done line names.
