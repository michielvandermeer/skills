# One hunt reads the code and one probes the running app

`/hunt-codebase-improvements` reads the code, and `/hunt-application-improvements` probes the app it starts locally, from outside. Neither skill does the other's job. Each Hunter of `/hunt-application-improvements` plays one kind of person, such as an attacker or a search crawler, and sees only what that person can see. The repo stays closed to all of them, so a missing label or an exposed key counts only when an outsider can find it. A check that can only be read from the code or a dashboard, such as a key in git history or an unsigned webhook, is a Hunt axis of `/hunt-codebase-improvements`.

## Considered Options

- **One skill for every check, in the code and in the running app.** Rejected: every run would be huge, and a Hunter that can read the code stops judging the app the way an outsider meets it.
- **Dropping the checks that need the code.** Rejected: leaked keys, unsigned webhooks, and untested backups would be checked nowhere.

## Consequences

- The UI polish and Performance Hunt axes stay in `/hunt-codebase-improvements`. They judge code and use the running app only as evidence.
- `/hunt-application-improvements` always starts the app through the repo's Verify skill and takes no URL. It never runs against a deployed site, so its attacker checks never reach production.
