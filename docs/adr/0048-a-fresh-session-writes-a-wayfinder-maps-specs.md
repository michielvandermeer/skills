# A fresh session writes a wayfinder map's Specs

The session that leaves no tickets remaining ends with a line telling the user to run `/wayfinder <map>` in a fresh session. That session finds no tickets remaining, reads the map and every resolved ticket in full, and writes the Specs. The session that resolved the last ticket holds its own ticket and the map's one-line gists. The cut and every `/to-spec` need the full body of every resolved ticket, which is more than a conversation already spent on one ticket can carry. How the Specs are cut is [ADR-0047](0047-a-wayfinder-map-ends-in-one-or-more-specs.md). What a Map ends in is [ADR-0011](0011-every-wayfinder-map-ends-in-a-spec.md).

## Considered Options

- Keep writing the Specs in the last session — rejected. Its context is already spent on one ticket, which is the load a map exists to keep off a session.
- Let the last session choose, and write the Specs itself when the map is small — rejected. Every map would then carry two endings, and a small map costs only one extra command.

## Consequences

- A ticket **remains** until it is `resolved`, `out-of-scope`, or closed as not planned. Closing as not planned removes a ticket the decision invalidated. A claimed or blocked ticket remains.
- A session that starts with tickets remaining but none it can take names them and ends, and does not release a claim.
- Only a session the user starts on a finished map writes Specs, so two sessions cannot each write them.
