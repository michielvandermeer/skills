# Sources

Each investigator gets its category's part of this file. A tool named here is an example: the investigator uses whichever tool the session has in that category, and reads its tool list first. A tool that fails to sign in is a gap, reported as such.

## Source control

The record tied most closely to the code. Widen the anchor's commit list:

```bash
git log --follow --oneline -- <file>            # history through renames
git log -S '<exact string>' -- <file>           # commits that added or removed that text
git log -G '<regex>' -- <file>                  # the same, by pattern
git blame -L <start>,<end> <file>               # last commit on each line
git show <hash>                                 # one commit in full
rg -n -C2 '(TODO|FIXME|HACK|XXX|NOTE)' <file>   # notes near the target
rg -l '<symbol>' --glob '*test*'                # tests that encode the edge cases
```

On GitHub, read each pull request with `gh pr view <number> --comments`, reviews included. Read the ADRs under `docs/adr/` and the changelog entries from the same weeks. A test added in the same commit often names the case the code guards.

## Tracker

Where the product or business reason usually lives. Search the Tracker `.agents/refs/tracker.md` names: `gh issue view <number> --comments` and `gh search issues` on GitHub, JQL through the Jira tools, or the files under `.agents/issues/` for a local Tracker.

1. Fetch every Issue the anchor names, with all its comments.
2. Search by the feature's name, the key symbols, and the user-facing terms, in several phrasings.
3. Walk from a child Issue to its parent: the parent often carries the reason. Follow closed-as-duplicate chains to the original.
4. Note labels and milestones, such as `customer-request` or `incident`, and compare each Issue's dates with the code's ship date. A scope that changed after the Issue was written shows in its history.

## Long-form documents

Design docs, specs, RFCs, meeting notes, postmortems, and runbooks, such as Confluence or Notion. Search by the feature's name, the key symbols, the error strings, and the pull request author around the ship date. Read each candidate page in full, with its child pages and its "alternatives considered" section.

## Team chat

Considered discussion that never reached a doc, such as Slack or Teams. Search for the pull request's URL or `/pull/<number>`, for the author's messages around the merge date, and for the error strings the code handles. Read each thread in full. A joke or a passing remark is not a decision. Note where retention cuts the history off.

## Observability

The runtime record, such as Datadog or Grafana. Find the service that owns the target, then the monitors, dashboards, logs, and incidents that mention the feature, a symbol, or the threshold. A monitor on a number is evidence someone worried about it. Compare the dates of spikes and incidents with the target's ship date.

## Error tracking

The exceptions behind defensive code, such as Sentry. Search by the exception classes the target catches, the error strings it checks, its function name, and its file path. For each issue that matches, record the first and last seen dates, the event count, the releases it hit, and a stack trace excerpt that passes through the target. An error that stops at the target's ship date is strong evidence. An AI root-cause summary is a hypothesis, not evidence.

## Product analytics

What users did, which experiments ran, and where a threshold came from, such as Databricks or Snowflake. List the tables before trusting a name, and bound every query to a window around the ship date, about 30 days either side. Record each table, window, and number the answer leans on.

## Incidents

Added to every brief when the target is defensive code. Look for Issues labelled `incident`, `sev-*`, or `postmortem`, chat channels named for incidents around the ship date, and commits such as "fix for incident", "add defensive check", or a revert followed by a reapply.
