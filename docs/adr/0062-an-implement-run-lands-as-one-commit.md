# An implement run lands as one commit

`/implement` lands a run on the base branch as one **landing commit**: the run's whole change, named after what it does. Landing every commit a run makes would put all of them on the base branch: the Spec copy, the plan, each Step's and each Iteration's commits, and the commit that deletes the run folder. On 2026-10-08, seven runs in `mvdmio-suite` that landed every commit left between 7 and 18 commits each, and most were named for the run's own bookkeeping. That makes `git log` slow to read for what changed and why.

The run still makes those commits, because a halted run resumes from them ([ADR-0004](0004-the-run-folder-is-outside-the-tracker.md)). They stay on the run's branch. Dropping them loses little. An Iteration's commit is not finished work until Review and Verify pass it. After a rebase, only the newest commit on the branch is verified again. So a `git bisect` that stops inside a run tests code nobody proved green.

The landing commit's subject says what the change does and ends with the Issue's reference. The run writes it from the Spec, because an Issue's title often names the problem instead. The body lists each Step's title when the run had more than one, then the Issue's closing reference.

## Considered Options

- **A merge commit per run, with the Iteration commits underneath.** Rejected: only `git log --first-parent` shows one line per run. Plain `git log` and GitHub's commit list still show every commit.
- **One commit per Iteration.** Rejected: the run would have to rewrite its branch with a scripted rebase before landing, which adds a new way for the land to fail. Every Iteration commit but the last would still be unverified.
- **Keeping every commit, with subject lines that start with the Issue's reference.** Rejected: the log stays just as long. It only gets easier to search.
- **`git merge --squash` on the base branch.** Rejected: it stages the run's change on top of whatever the user had already staged in the original directory, so the commit after it would include the user's work.
- **`git commit-tree`, with a check the repo names on its own line run over the landing range.** Rejected: the repo's hooks already hold its commit rules, and a second line would repeat them and drift from them. A plain `git commit` runs the hooks themselves, with no new line.

## Consequences

- `/implement` builds the landing commit with a plain `git commit` on a detached HEAD in the run's worktree. It detaches at the branch tip, deletes the run folder, moves the index back to the base-branch commit the run rebased onto with `git reset --soft`, and commits. That parent is held as a hash, not the branch's name. Then it fast-forwards the base branch to the commit. The staged change is the whole run's diff on the rebased files, so the repo's hooks check the combined code. A rebase runs no pre-commit hook, so a tree it combines has never been checked. `git commit-tree`, used here before, ran no hooks either. In mvdmio-suite #1645 the run's own commits kept two files under the 20,000-byte limit, the base branch grew them meanwhile, and the rebased tree landed at 21,490 and 20,232 bytes for CI to catch.
- A hook that refuses the landing commit is a finding, as a failed Verify after the rebase is: it starts the next Iteration, and on the third Iteration it halts the run with a Halt record. The branch never gets the deletion, so it still holds its run folder for that Iteration.
- When another session lands on the base branch after the rebase, the fast-forward fails, and the run rebases, verifies again, and tries again. The branch keeps its commits until the fast-forward succeeds, so that retry has them. Naming the branch as the parent would make the newer commit the parent while the tree still lacked it, so the fast-forward would succeed and undo that commit. On 2026-10-10 a run in `mvdmio-suite` nearly undid another run's fix this way. Then the run deletes the branch with `git branch -D`, once the branch holds the same files as the base branch outside its run folder.
- On the base branch only the whole run can be reverted, so `/pr` judges Merge risk on the whole run.
- `/retro` reads an implement run's change from its landing commit.
- `/hillclimb` keeps its commits. Each Attempt it keeps is a measured change with its own before-and-after number, so those commits are the record of the work.
