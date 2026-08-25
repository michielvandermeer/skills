# Idea — Grilling waits on fact explorers

Status: idea

## Motivation

A `/grilling` session already says a running exploration is an unsettled prerequisite, and to
dispatch a sub-agent and block on it. In practice the driving session still hunts the same trees
while those explorers run: it greps and reads the files it just handed off. That doubles the token
cost and can open Round 1 on a partial picture before the explorers return.

This showed up in a Compliance Title-band grilling: two explore sub-agents spent about three
minutes on Edit pages and chrome ADRs, and the parent grepped `title-band`, sticky, CONTEXT, and
Edit pages in parallel.

## Goal

Once the driving session has dispatched sub-agents to gather facts, it waits for them. It does not
re-read the same trees in the meantime. Round 1 starts from the explorers' reports.

## Decisions (locked)

- This is a grilling-session rule, not a host-wide ban on parallel tools.
- The existing "block on it" line is the intent. The gap is the parent still working the same
  hunt.

## Out of scope

- Stopping the parent from asking Round 1 questions that do not need those facts.
- Changing how explorers are prompted or which agent type they use.

## Open questions

- If the parent has a *different* fact to find, may it hunt that while the explorers run, or does
  every environment fact go through a sub-agent first?
