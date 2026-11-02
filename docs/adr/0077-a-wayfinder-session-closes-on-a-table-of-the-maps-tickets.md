# A wayfinder session closes on a table of the map's tickets

Every `/wayfinder` session ends by showing the user one table: a row for each Decision ticket of the Map, with its reference, name, and status (`resolved`, `ruled out`, `claimed`, `blocked`, or `available`). A session resolves one ticket and sees little else of the map, and the user cannot tell from the one ticket's answer where the whole effort stands or which ticket to run next. The table is built from a fresh list of the tickets in the Tracker at the end of the session, so it shows every other session's changes too. It is the same table for every ending: charting, resolving a ticket, an empty frontier, and writing the Specs. The Map's body stays an index of decisions.

## Considered Options

- Keep the table in the Map's body — rejected. The Map records each decision once, in its ticket, and a status column restates ticket state that other sessions change at the same time, so it would go stale between sessions.
- List only the tickets that remain — rejected. The user asked for every step of the way, and the resolved rows show how far the effort has come.
- Show the table only when the last ticket resolves — rejected. The sessions before it are where the user decides which ticket to run next.

## Consequences

- A ticket closed as not planned shows as `ruled out`, whether it sat past the destination or a decision invalidated it.
- The table is output for a person, so it runs at the bar `/technical-writing` sets ([ADR-0009](0009-skill-output-follows-technical-writing.md)).
