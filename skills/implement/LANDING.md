# Landing

Read from the top once step 6's landing gate opens. `<branch>` is `<slug>`, or the name recorded when a host tool chose another. Each command runs where its branch is checked out, and that fixes the order. Under `/implement-yolo`, [Worktree waived](#worktree-waived) replaces the rebase, the landing commit, and the fast-forward.

## Before the rebase

Commit anything still uncommitted on the run branch as its own unit commit; `git rebase` refuses a dirty tree. Then `node <this skill's directory>/scripts/check-run.mjs <run directory>/todo.md`: exit 0 opens the land, and any printed line is an item still open, a gate still closed, or a line that is not a checklist line, so finish or fix it first or **halt**. Hold `git merge-base HEAD <base>` as `<fork>` and `git rev-parse <base>` as `<onto>`.

## The rebase

From the worktree, still on the branch: `git rebase <onto>`. A conflict is `/resolving-merge-conflicts` (the branch lives here, so only the worktree can rebase it). Later steps build on `<onto>`, held as a hash: other sessions land on `<base>` while this run verifies, and a commit built on the moved `<base>` would undo what they landed.

When the rebase replayed the branch onto commits `<base>` gained, the verification is not known any more. Skip the re-check only when every path `git diff --name-only <fork> <onto>` lists is Markdown or sits under `.agents/`, and no project file, build script, test, or verification command the trail names reads one of them; the report then quotes the range and why ([ADR-0029](../../docs/adr/0029-test-failures-are-measured-against-the-base-branch.md)). Otherwise a fresh Verifier re-runs step 6's verification gate on the rebased head. Before any fix, re-run each failing project once yourself: a failure that passes on the re-run is a flaky test, a flag for the report ([ADR-0046](../../docs/adr/0046-a-flaky-post-rebase-failure-is-not-a-fixer-dispatch.md)); one that fails again is red and goes to a fresh delegate under step 5's retry rule, and its commit lands before the fast-forward.

## Close the Issue

The Tracker ref's "close as done" operation runs here, on the run branch, when it is a change to files in this repository: with the local Tracker ([setup/LOCAL.md](../setup/LOCAL.md)), delete `.agents/issues/<slug>.md` and the Map folder beside it when there is one, and remove `<slug>` from every other Issue's `Blocked by:` line. Commit it as its own unit commit, `Unit: Close the Issue`, so the landing commit carries the close. A Tracker whose close is a reference in the commit message gives the landing commit its closing reference below and changes no file here. A run from a description closes nothing.

## The landing commit

The landing commit is the one commit the run leaves on `<base>` ([ADR-0062](../../docs/adr/0062-an-implement-run-lands-as-one-commit.md)). Build it from the branch's tree on top of `<onto>`, leaving the branch where it is: `git commit-tree HEAD^{tree} -p <onto> -F -`, with the message on stdin. Hold the hash it prints as `<landing>`. The Run directory is ignored, so the tree holds none of it and no deletion commit is needed.

- **Subject.** What the change does, ending with the Issue's reference: `Roles are given from the Person (#104)`. Write it from the Spec, not the Issue's title, which often names the problem. Follow the commit style the repo's `AGENTS.md`, `CLAUDE.md`, or Coding standards document, when they document one. A run from a description has no reference.
- **Body.** Each unit's title, one per line in commit order, from the branch's `Unit:` trailers, when the run had more than one. A Bug fix adds a `Verification` section quoting the red output from `evidence/` and the green output from the Verifier, each trimmed to the assertion and the counts. A Perf issue adds the baseline and post-fix numbers with their unit. Then the Issue's closing reference as the Tracker ref gives it; a ref whose close is a file change carries nothing here, and when the ref gives no close at all, the report names the Issue for the user to close.

## Fast-forward and cleanup

1. Add `Landed: <landing>` as a header line of `todo.md`.
2. Return the session to the original directory, keeping the branch and its commits: a host leave-worktree action when it does exactly that, otherwise change directory yourself.
3. Copy `.agents/runs/<slug>/` from the worktree to `.agents/runs/<slug>/` in the original checkout, replacing what is there; the worktree removal below takes the original with it.
4. On `<base>`: `git merge --ff-only <landing>`. `<landing>`'s parent is `<onto>`, so this is a fast-forward only while `<base>` is still `<onto>`. When it errors, `<base>` moved: re-enter the worktree, go through the rebase, the close, and the landing commit again, and retry. Two retries at most; a third refusal **halts** with the error quoted, and the branch holds the work.
5. `git worktree remove <path>`, never forced; a lock means another session still has it. Then `git branch -D <branch>` once `git diff --quiet <branch> <base>` succeeds: its commits never reach `<base>`, so `-d` refuses it, and the empty diff shows `<base>` holds all of its work. A non-empty diff keeps the branch and names it in the report.

Done when the merge succeeded, the worktree is gone, and the branch is deleted or named.

## The push

The push sends `<base>` from the original directory: in step 7, once the landing commit is on it, so the CI run it starts carries the landing commit's subject; and in step 8, when `/retro` committed ([ADR-0028](../../docs/adr/0028-implement-claims-its-issue-and-pushes-only-what-lands.md)). Skip both when the repo's `AGENTS.md` or `CLAUDE.md` says implement runs do not push, or when `git remote` lists nothing. Otherwise:

- `<base>` tracks a remote branch: `git push <remote> <base>:<branch>`, with `<remote>` from `git config branch.<base>.remote` and `<branch>` from `git config branch.<base>.merge`.
- `<base>` tracks nothing: `git push -u origin <base>`. A repo with no `origin` skips the push.

The push sends `<base>` as it stands, commits the user had not pushed yet included. It is a plain push with hooks running: never `--force`, `--force-with-lease`, or `--no-verify`. A refused or failed push gets no retry and is not a halt: the run has landed, and nothing is left to resume.

The run's last lines name the landing commit, then say what each push sent and to which remote branch. When it pushed nothing, they say why: the `AGENTS.md` or `CLAUDE.md` line, no remote, or no `origin`. When a push failed, they quote the error and name the commits that wait on this machine, the landing commit and `/retro`'s after a failed first push, `/retro`'s after a failed second, for the user to pull and push.

## Worktree waived

Under `/implement-yolo` there is no worktree, no run branch, and nothing to enter, exit, or remove. The session works at the git root of this checkout (`git rev-parse --show-toplevel`) on the branch it is on. `<start>` is `git rev-parse HEAD` when the run starts, recorded on `todo.md`'s `Start:` line, and stands in for `<base>` everywhere: the commits this run adds are `git log <start>..HEAD`, and failures are measured against `<start>` ([ADR-0055](../../docs/adr/0055-a-run-lands-on-the-branch-it-started-from.md)). A dirty tree is the working copy: a resume never stashes or resets it, and uncommitted files may land in a unit's commit.

The land is [Close the Issue](#close-the-issue) and then one fold in place of the rebase, the landing commit, and the fast-forward: after `check-run.mjs` exits 0, `git reset --soft <start>`, `git add -A`, then commit with the landing commit's message. Done when `git status` is clean and `git rev-list --count <start>..HEAD` prints `1`. Add `Landed: <sha>` to `todo.md`; the Run directory already sits in this checkout, so nothing is copied. The push and `/retro` run as above, with `<base>` the branch you are on and this checkout the original directory.

A run in flight is `.agents/runs/<slug>/todo.md` in this checkout with an open item and no `Landed:` line. A worktree on branch `<slug>`, or branch `<slug>` while this checkout is on a different branch, is another run: **halt** and say so.
