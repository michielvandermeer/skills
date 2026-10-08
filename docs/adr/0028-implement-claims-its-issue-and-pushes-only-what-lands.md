# An implement run claims its Issue and pushes only what lands

An `/implement` run pushed a package release from a second repository and created live billing products, unattended, because a Step needed them and nothing said no. So no Step pushes, publishes, or changes an external system: the work stays inside local working trees, this repository's or another's. Work a Spec puts in another repository goes on a branch named after the run there, committed and never pushed, and the final report names it. A Step that needs something published — a package, a deployed page, a live record — halts the run and says so.

The run writes outside those working trees twice. The first write is the claim on its own Issue, made through the Tracker before the run does any other work. Several unattended runs can start from the same list of `ready-for-agent` Issues, and without a claim two of them build the same Issue. A run on an Issue another user has claimed stops and names them.

The second write is the push of the base branch. It goes out as soon as the landing commit is on the base branch, and again after `/retro` when `/retro` made a commit. By then the code has passed every review and Proof the run holds, on a branch the user chose by checking it out. The push is also what lets a Tracker act on the landing commit's closing reference: GitHub closes the Issue, and Jira smart commits move it to done. When the push was left to the user, every finished Issue stayed open until they came back. A repo turns the push off with a line in its `AGENTS.md` or `CLAUDE.md` saying implement runs do not push. A repo where a push to the main branch deploys is the case that line is for.

GitHub names a CI run after the newest commit in the push that started it. A push after `/retro` carries `/retro`'s commit as its newest whenever `/retro` made one, and nobody can tell from that name which change the CI run builds or deploys. So the first push goes out before `/retro`, and its CI run is named after the landing commit. `/retro` still runs after the land, because the land is part of what it learns from.

The run pushes the base branch as it stands, to the branch it tracks. A branch with no remote copy goes to `origin` and tracks it there; a repo with no `origin` skips the push. The push is never forced and never skips hooks. When the remote refuses a push, or it fails for any other reason, the run says so and pushes nothing more: the work stays landed locally, and the user pulls and pushes. `/retro` still runs after a failed first push. A failed push is not a halt, because nothing is left to resume. A halted run never reaches the push.

## Considered Options

- **The Step agent decides case by case.** Rejected: an unattended run has no one to weigh an irreversible action.
- **Asking the user mid-run.** Rejected: the run lands unattended by design, and a question stops it anyway — so it stops as a halt, which is resumable and leaves a record.
- **Whatever starts the runs claims the Issue.** Rejected: every scheduler would have to claim, and a run started by hand would still race one a scheduler started.
- **The run worktree's lock is the only claim.** Rejected: it is seen only by runs in the same repository on the same machine.
- **A status label marks the Issue as taken.** Rejected: an Issue carries one status at a time, and the status says where the Issue stands, not who holds it.
- **Always pushing, with no way to turn it off.** Rejected: in a repo where a push deploys, every run would deploy with nobody watching.
- **Pushing only in repos that turn it on.** Rejected: nothing would change until each repo opted in, while most repos want the push.
- **The switch as a setting in the Tracker ref, or in a new file under `.agents/refs/`.** Rejected: the Tracker ref describes the Tracker, and a new file adds a document to every repo. The host already loads `AGENTS.md` and `CLAUDE.md` into every session, and repos already steer implement runs from there.
- **`/setup` asking whether a push deploys.** Rejected: repos already set up never run `/setup` again, and it would start writing rules into `AGENTS.md`.
- **Fetching, rebasing, re-testing and pushing again after a refusal.** Rejected: by then the run's worktree and Step files are gone, so the Proofs cannot re-run, and a rebase conflict would land in the user's own checkout.
- **Catching up with the remote before landing, inside the existing retry loop.** Rejected: the run would pull into the user's branch for them and could still lose a last-second race. A refusal needs someone else pushing to the same branch during the run, and runs on one machine already queue behind each other on the local branch.
- **Skipping a branch with no remote copy.** Rejected: a run on a fresh feature branch, common under `/implement-yolo`, would never push.
- **Skipping the push when the branch was already ahead of the remote.** Rejected: git cannot push the run's commits without the commits underneath them, and the run was tested with those commits underneath.
- **Pushing the run's branch in another repository too.** Rejected: that branch has landed nowhere, and the user still decides what becomes of it.
- **One push, after `/retro`.** Rejected: the CI run it starts is named after `/retro`'s commit whenever `/retro` made one.
- **One push before `/retro`, with `/retro`'s commit left for the next push.** Rejected: the last `/retro` commit of a day stays on the machine until something else pushes.
- **Running `/retro` before the land, with its edits inside the landing commit.** Rejected: `/retro` would no longer see the land, and reverting the run would also revert what `/retro` learned.

## Consequences

- The Planner plans another-repository work last and names its files by absolute path.
- All three implement commands push once the landing commit is on the base branch, then run `/retro`, then push again when `/retro` made a commit. A workflow without a path filter runs twice for such a run.
- The run's last lines name the landing commit and say what each push sent and where, or why it pushed nothing.
- On GitHub, a pushed run closes its Issue only when the base branch is the default branch, because GitHub acts only on commits that reach it.
- The claim stays when the run halts or lands. A later run by the same user carries on past it; closing the Issue, or the user, clears it.
- The Tracker ref says how to claim an Issue. A ref that gives no claim for Issues leaves the run unclaimed. The local template gives none: its Issues live in the repository, so a claim written there would reach no session that the run's branch does not already reach.
