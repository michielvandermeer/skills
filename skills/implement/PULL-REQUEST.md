# A Spec on a GitHub issue

Read when the argument is a **GitHub issue** — a GitHub issue link, or a bare number for this checkout's own repository ([triage/GITHUB-ISSUE.md](../triage/GITHUB-ISSUE.md)). Its body is the Spec, and the run ends in a pull request against the repository's default branch instead of a land ([ADR-0055](../../docs/adr/0055-a-run-lands-on-the-branch-it-started-from-or-opens-a-pull-request.md)). Use whatever GitHub access the session has.

Pushing the run's branch, opening its pull request, and marking the grilling draft ready for review are this run's only acts outside a local checkout ([ADR-0028](../../docs/adr/0028-an-implement-run-leaves-the-repository-only-for-its-pull-request.md)). A Step that needs anything else published still halts, and work in another repository is still never pushed. The issue stays as it is: `ready-for-agent` stays on it, and the merge closes it.

## Start

Before anything else in step 1, **halt** on the first of these that fails, saying why:

1. The session can push to this repository and open pull requests on it.
2. The issue carries `ready-for-agent`. Without it, the body is not a Spec yet.
3. No open pull request ready for review closes the issue — `Closes #N` in its body. When one does, name it. An open draft that closes it is the **grilling draft**, and this run continues it.

Then step 1 runs with these in place of its own:

- `<slug>` is `issue-<N>`.
- The Spec path is `<spec>`: `$(git rev-parse --path-format=absolute --git-common-dir)/spec/<slug>.md`. Write the issue body there each time step 1 runs, fresh or resumed, and hand `<spec>` wherever the command hands the Spec path. It is run scratch: the land below deletes it, and a halt keeps it.
- `<base>` is the default branch as GitHub has it: fetch it and use its remote-tracking ref, such as `origin/main`. The run is reviewed and measured Green against it, except where `/implement-yolo` measures against `<start>`.
- `<branch>`, the run's branch, is the grilling draft's branch when there is one, at the head GitHub has; otherwise `<slug>`, starting from `<base>`. Step 1's in-flight checks look for `<branch>` where they name branch `<slug>`, and a name a host tool chose is recorded as `<branch>`.
- With a grilling draft, the run works on `<branch>` itself so the push lands on the draft: a fresh worktree opens on it with `git worktree add`, in place of a host tool and the reset to `<base>`. Once on `<branch>`, when `<base>` has commits it lacks, merge `<base>` in; a conflict is `/resolving-merge-conflicts`.

## In place of the land

This replaces the command's delete and land. Run it on `<branch>`, inside the worktree when there is one.

1. Hold `grep -h '^Safety fact:' .agents/steps/<slug>/*.md` for the final report. Delete `.agents/steps/<slug>/` in one commit, then delete `<proof>` and `<spec>`. The Spec stays in the issue body, and the Prototype folder stays. Commit anything still uncommitted.
2. Fetch `<base>`. Without a grilling draft, `git rebase <base>`; with one, `git merge <base>` when `<base>` has commits the branch lacks. A conflict is `/resolving-merge-conflicts`, and a `CHANGELOG.md` conflict keeps both, this run's entry above. When either brought in new commits, rebuild and re-run what the command's land re-runs after a rebase, with its flaky re-run and its one fixer ([ADR-0046](../../docs/adr/0046-a-flaky-post-rebase-failure-is-not-a-fixer-dispatch.md)).
3. `git push origin <branch>`, never forced. A rejected push **halts**.
4. Without a grilling draft, open a pull request from `<branch>` against the default branch, ready for review and titled with the Spec's title. Its body is a short summary of what the run built, and `Closes #N`. With a grilling draft, mark it ready for review and rewrite its body the same way, keeping `Closes #N`.
5. Return the session to the branch it started on: leave the worktree and `git worktree remove` it, never forced; with no worktree, check that branch out. `<branch>` stays, because the pull request is built on it.

The final report links the pull request and carries the `Safety fact:` lines. When step 2 brought in new commits, it says the Proofs predate them; they are not re-run. The command's `/retro` commit goes on the branch the session started on, outside the pull request.
