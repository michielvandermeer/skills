# An implement run lands as one commit

Both implement commands land a run on the base branch as one **landing commit**: the run's whole change, named after what it does. Landing every commit a run makes would put all of them on the base branch: the Spec copy, each Iteration's commits, and the commit that deletes the run folder. On 2026-10-08, seven runs in `mvdmio-suite` that landed every commit left between 7 and 18 commits each, and most were named for the run's own bookkeeping. That makes `git log` slow to read for what changed and why.

The run still makes those commits, because a halted run resumes from them ([ADR-0004](0004-the-run-folder-is-outside-the-tracker.md)). They stay on the run's branch. Dropping them loses little. An Iteration's commit is not finished work until Review and Verify pass it. After a rebase, only the newest commit on the branch is verified again. So a `git bisect` that stops inside a run tests code nobody proved green.

The landing commit's subject says what the change does and ends with the Issue's reference. The run writes it from the Spec, because an Issue's title often names the problem instead. The body carries the Issue's closing reference.

## Considered Options

- **A merge commit per run, with the Iteration commits underneath.** Rejected: only `git log --first-parent` shows one line per run. Plain `git log` and GitHub's commit list still show every commit. `/implement-yolo` also has no branch to merge.
- **One commit per Iteration.** Rejected: the run would have to rewrite its branch with a scripted rebase before landing, which adds a new way for the land to fail. Every Iteration commit but the last would still be unverified.
- **Keeping every commit, with subject lines that start with the Issue's reference.** Rejected: the log stays just as long. It only gets easier to search.
- **`git merge --squash` on the base branch.** Rejected: it stages the run's change on top of whatever the user had already staged in the original directory, so the commit after it would include the user's work.

## Consequences

- `/implement` builds the landing commit with `git commit-tree`, from the branch's final tree. Its parent is the base-branch commit the run rebased onto, held as a hash, not the branch's name. Then they fast-forward the base branch to it. When another session lands on the base branch after the rebase, the fast-forward fails, and the run rebases, verifies again, and tries again. The branch keeps its commits until the fast-forward succeeds, so that retry has them. Naming the branch would make the newer commit the parent while the tree still lacked it, so the fast-forward would succeed and undo that commit. On 2026-10-10 a run in `mvdmio-suite` nearly undid another run's fix this way. Then the run deletes the branch with `git branch -D`, once the branch and the base branch hold the same files.
- `/implement-yolo` folds every commit since its start into one landing commit on its own branch. A commit the user makes on that branch during the run is folded in too.
- On the base branch only the whole run can be reverted, so `/pr` judges Merge risk on the whole run.
- `/retro` reads an implement run's change from its landing commit.
- `/hillclimb` keeps its commits. Each Attempt it keeps is a measured change with its own before-and-after number, so those commits are the record of the work.
