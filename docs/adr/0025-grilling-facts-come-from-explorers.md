# Grilling facts come from explorers, and the session waits for them

A `/grilling` session already said to dispatch a sub-agent for a fact and block on it. In practice the Driving session read the same code itself while the explorer ran, posted round 1 before the report landed, and sometimes never read the report. The session now reads only `CONTEXT.md`, the ADRs, and the brief it started from itself; every fact from the code arrives as an Explorer's report, the session waits for that report however long it takes, and a round leaning on it is not posted before it lands. Round 1 may go out while explorers run only when it asks scope alone, which needs no facts from the code.

Letting the session hunt a different fact while explorers run was rejected: every fact it reads stays in its context for the whole session, and the Driving session's job is to hold the tree small. A time limit on waiting was rejected: a round built on guesses costs more than the wait.

## Consequences

- The Idea `grilling-wait-on-fact-explorers` is resolved by this decision and deleted.
- A fact only the user holds is a question, with a line saying why it could not be found.
- A report that lands after a round is posted waits for the next round.
