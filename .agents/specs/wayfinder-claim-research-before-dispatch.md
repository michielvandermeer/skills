# Claim research tickets before dispatch

Status: ready-for-agent

## Problem Statement

A `/wayfinder` charting session (the first session that draws the map) starts a research subagent for each research ticket and then ends. Those tickets stay unclaimed while the subagents work: they have no `Status:` line. A second `/wayfinder` session therefore treats the same tickets as open work and starts a second set of subagents for them.

This happened on the OpenIddict migration map. The first session started three researchers. The second session, invoked with the map about a minute later, read three research tickets with no `Status:` line, decided they had never been started, claimed them itself, and started three more researchers for the same tickets.

The skill already says a session claims a ticket before any work, so concurrent sessions skip it. Charting never does that claim. A later session is told to skip research that is still running, but that state is not on disk unless the ticket is Claimed. Concurrent sessions only see the files.

## Solution

The Driving session writes `Status: claimed` on the shared map before it starts a research subagent. It waits until that write is on disk, then starts the subagent. Charting does this for every research ticket it creates. A later session does this for any research ticket that was not started at charting.

A second `/wayfinder` session skips Claimed tickets. They are not open work. If a grilling or other unclaimed ticket is open, that session takes it. If the only remaining tickets are Claimed research, it tells the user that research is still running and does not start another subagent.

The research subagent still writes the answer and sets `Status: resolved`. It does not claim. `/research` and the researcher agent do not learn wayfinder claim rules.

## User Stories

1. As someone who charts a map that includes research tickets, I want those tickets Claimed on the shared map before any research subagent starts, so a later session can see that the work is already in flight.

2. As someone who charts a map, I want each research ticket Claimed as its own write that lands before its subagent starts, so a second session that opens in the gap between "create tickets" and "start subagents" still sees the claim.

3. As someone who starts `/wayfinder` on an existing map while charting research is still running, I want that session to skip Claimed research tickets, so I do not pay for a second researcher on the same question.

4. As someone who starts `/wayfinder` on an existing map while charting research is still running, and a grilling or other unclaimed ticket is already open, I want that session to take the unclaimed ticket, so the map still moves.

5. As someone who starts `/wayfinder` on an existing map while the only open tickets are Claimed research, I want the session to say that research is still running and stop, so it does not invent a second dispatch.

6. As someone who names a Claimed research ticket when I start `/wayfinder`, I want the session to say that ticket is already in flight and not start another subagent, so an explicit name cannot override the claim.

7. As someone whose map later grows a new research ticket, I want the Driving session to Claim that ticket on the shared map and then start its research subagent, so later-graduated research uses the same claim-then-start sequence as charting.

8. As someone running two `/wayfinder` sessions at once, I want the claim to live on the map those sessions both scan, so a throwaway research branch or an isolated copy of the repo cannot hide the claim from the other session.

9. As a research subagent, I want to write the answer and set `Status: resolved` on the ticket I was given, so I do not also have to claim it.

10. As someone who reads `/research` or the researcher agent prompt, I do not want those documents to carry wayfinder claim rules, so a standalone research question stays a standalone research question.

11. As someone who charts a map, I want the charting session to still end after it has Claimed and started the research subagents, so charting does not wait for the answers and does not resolve those tickets itself.

12. As a later `/wayfinder` session, I want a ticket with no `Status:` line to still mean unclaimed, so the existing scan ("open tickets have no `Status:` line") keeps working.

13. As a later `/wayfinder` session, I want `Status: claimed` to be enough to skip a research ticket, so I do not have to guess whether a subagent from another session is still running.

14. As someone whose research subagent finishes, I want the ticket to move from Claimed to `resolved` with an answer and a pointer to the findings, so the map's Decisions so far can take it.

15. As someone working a grilling ticket that is blocked on research, I want that grilling ticket to stay blocked until the research ticket is `resolved`, not merely Claimed, so a claim does not pretend the answer is in.

16. As someone who reads the wayfinder skill, I want "skip research still being burned down" to mean "skip Claimed research tickets", so the skip is a file check, not a memory of which session started which subagent.

17. As someone who creates several research tickets in one charting session, I want all of them Claimed and started in that session, so the existing exception that research tickets may run together still holds.

18. As someone who opens the map after a crash, I want a Claimed research ticket to stay Claimed, so a restart does not treat it as open and start a third researcher. Clearing a stuck claim is a later, separate change.

## Implementation Decisions

- The claim rule stays one rule: the Driving session writes `Status: claimed` on the ticket, first, before any work. Charting is not an exception. Starting a research subagent is work.

- Both places that start a research subagent use the same sequence: write `Status: claimed` on the shared map, wait until that write is on disk, then start the subagent. The two places are charting after it creates research tickets, and a later session that finds an unclaimed research ticket that was not started at charting, including a ticket that graduated later. Creating a research ticket already Claimed is allowed when that same session will start its subagent.

- Charting still ends after it has Claimed and started the research subagents. It does not wait for answers. It does not write those tickets' answers itself.

- The claim is written on the map other `/wayfinder` sessions scan — the effort directory in the working copy the user invoked. A throwaway research branch may still hold findings. It is not the only place the claim lives.

- A later session chooses the next ticket from the existing open set: no `Status:` line, unblocked, unclaimed. Claimed research is already out of that set. Drop the extra "still being burned down" test as a separate heuristic. Replace it with the file check: a research ticket whose `Status:` is `claimed` is in flight; do not start another subagent for it.

- If the user named a Claimed research ticket, the session reports that it is in flight and does not start another subagent.

- If every remaining unblocked ticket is Claimed research, the session tells the user that research is still running and ends. It does not wait for the subagents, and it does not start new ones.

- The research subagent still writes `## Answer`, leaves a pointer to the findings, and sets `Status: resolved`. It does not write `Status: claimed`. `/research` and the researcher agent prompt do not mention claims.

- A Claimed ticket does not unblock tickets that list it under `Blocked by`. Only `resolved` does.

- No new `Status:` value. `claimed` is the in-flight signal.

## Testing Decisions

A good test is what a second `/wayfinder` session does when it reads the files, not how the skill is worded.

- Chart a map that creates at least two research tickets. Confirm each research ticket has `Status: claimed` on disk before its subagent exists. Confirm the charting session has ended with those tickets still Claimed, not `resolved`.

- Start a second `/wayfinder` on that map while those subagents are still running. Confirm it does not start a second subagent for a Claimed research ticket.

- When an unclaimed grilling ticket is already open beside Claimed research, the second session takes the grilling ticket.

- When the user names a Claimed research ticket, the second session reports in-flight and starts no subagent.

- When a new research ticket graduates on an existing map, it is Claimed on disk before its subagent starts.

- A ticket that lists a Claimed research ticket under `Blocked by` stays blocked until that research ticket is `resolved`.

Do not test the markdown shape of the skill. Do not add a product test suite for this; the plugin has none. Prior art is the wayfinder skill's own claim rule, already used when a later session works a ticket and missing from charting.

## Out of Scope

- Clearing or unclaiming a ticket whose research subagent died, was cancelled, or never wrote `resolved`.
- Changing how findings land on a throwaway `research/<name>` branch, or whether a research subagent uses an isolated worktree.
- A new `Status:` value such as `researching`.
- Changing who may run unblocked tickets in parallel.
- Changing `/research` for questions that are not wayfinder tickets.
- The OpenIddict migration map itself.

## Further Notes

Verified from Grok sessions `01a0b481-9941-77e1-872d-59a96965f752` (chart) and `01a0b4a0-669f-7ba0-90d4-340b12cf99be` (second invoke) in jewel-modern. Charting started three researchers at 13:05 without claiming. The second session read Can OpenIddict serve implicit id_tokens, What storage OpenIddict needs, and What key material OpenIddict needs with no `Status:` line, wrote `claimed` itself, and started three more researchers at 13:10.

A later session on an existing map already claims before it works a ticket. Charting is the path that starts research and then ends, so it is the path that leaves the gap. No ADR: the skill already named the claim, and this change makes charting use it.
