# A fresh session writes a wayfinder map's Specs

[ADR-0047](0047-a-wayfinder-map-ends-in-one-or-more-specs.md) had the session that resolved the last ticket go on to split the work and write the Specs. That session holds its own ticket and the map's one-line gists. The cut and every `/to-spec` need the full body of every resolved ticket, so it had to read all of them on top of a conversation already spent on one ticket. The session that leaves no tickets remaining now ends with a line telling the user to run `/wayfinder <effort>` in a fresh session. That session finds no tickets remaining, reads the map and every resolved ticket in full, and writes the Specs.

## Considered Options

- Keep writing the Specs in the last session — rejected. Its context is already spent on one ticket, which is the load a map exists to keep off a session.
- Let the last session choose, and write the Specs itself when the map is small — rejected. Every map would then carry two endings, and a small map costs only one extra command.

## Consequences

- A ticket **remains** until it is `resolved` or `out-of-scope`. A claimed or blocked ticket remains.
- A session that starts with tickets remaining but none it can take names them and ends, and does not release a claim.
- Only a session the user starts on a finished map writes Specs. Two sessions that each resolved a "last" ticket at the same moment no longer both write them.
- ADR-0047 stands for how the Specs are cut, and ADR-0011 stands for what a Map ends in. Only which session writes the Specs changes.
