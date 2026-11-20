# Hunt application improvements

`/skills:hunt-application-improvements` starts the app through the repo's own Verify skill and sends Hunters through it, each playing one outsider along one Hunt axis. It stops the app with the Verify skill's Cleanup, writes `.agents/hunt-application/<stamp>/seed.md` ordered by severity, and triages the seed into Specs and parked Issues with screenshots attached.

## Sub-features

- `hunt-app-no-verify` stops with `no Verify skill: run /setup verify` in a repo with no `.claude/skills/verify/`, and dispatches no Hunter. Driven on 2026-11-21.
- `hunt-app-named-axes` sends one Hunter per named axis, each brief carrying BROWSER.md's commands with values filled in and the stop goal, then writes the seed and triages it. Driven on 2026-11-21 with the attacker, the search crawler and the breaker.
- `hunt-app-free-form` sends one `free-form` Hunter for instructions that name no axis. Not yet driven.
- `hunt-app-all-axes` sends all ten Hunters when there are no instructions. Not yet driven. It costs about three times a three-axis run.

## How to get to it (user POV)

- Type `/skills:hunt-application-improvements`, optionally with instructions such as `the attacker and the breaker, stop after 5 minutes`.
- It takes no URL. The URL comes from the Verify skill's Launch section.
- It is user-only (`disable-model-invocation: true`).

## Driving it with verify.py

Preconditions for `hunt-app-named-axes`:

- `playwright cli --help` works on the machine, and `chromium` is on PATH.
- A fresh run with a tiny committed app and a `.claude/skills/verify/SKILL.md` holding Launch (`nohup python3 server.py <port> ... & echo $! > .server.pid`), Doctor (`curl -sf`), and Cleanup (`kill "$(cat .server.pid)"`) sections. Plant findable problems: a `sk_live_...` string in a served JS file, a list with no empty state, a form that shows an error before typing, a nav link to another host.

- **No Verify skill.** In a plain run, `turn <run> "/skills:hunt-application-improvements"`. The final message is the stop line, `agents dispatched this turn: 0`, and the scratch repo is unchanged.
- **Named axes.** `turn <run> "/skills:hunt-application-improvements the attacker, the search crawler and the breaker, stop after 5 minutes" --budget 15`. The turn ran in one go with no triage questions, for about $4.
- **Proof.** Read the main transcript's Bash calls and Agent prompts, not the final message. The Launch command runs before any Hunter, and Cleanup's `kill` runs after the last Hunter reports. `agents dispatched` lists one `general-purpose` Hunter per named axis. Each browser Hunter's prompt names `-s=<stamp>-<slug>`, its `cli.json` path, and `5 minutes`. The seed's heredoc shows severities in order. The scratch repo ends with one triage commit adding `.agents/issues/*.md` and `.agents/attachments/<slug>/*.png`. `grep -r <planted key> .agents` finds nothing. No Hunter's Bash call touches the off-host link.

## Gotchas

- Cleanup deletes the scratch folder, so `seed.md` survives only in the main transcript's heredoc.
- Triage reads the repo code and may restart the app to reproduce a finding. That is triage's investigate step, not a Hunter breaking the closed-code rule.
- Only the attacker's brief says to report a key by location. On 2026-11-21 the search crawler quoted the full planted value in its own report, though the seed and Issues held only the prefix.
- The session runs on Sonnet, the model the skill's frontmatter pins.
