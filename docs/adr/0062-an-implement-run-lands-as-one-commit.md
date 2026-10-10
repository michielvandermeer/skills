# An implement run lands as one commit

All three implement commands land a run on the base branch as one **landing commit**: the run's whole change, named after what it does. Landing every commit a run makes would put all of them on the base branch: the plan commit, each Step agent's commit, each Checker's commit, the fixers' commits, the Changelog commit, and the commit that deletes the Step files. On 2026-10-08, seven runs in `mvdmio-suite` that landed this way left between 7 and 18 commits each, and most were named for the run's own bookkeeping. That makes `git log` slow to read for what changed and why.

The run still makes those commits, because a halted run resumes from them ([ADR-0030](0030-planner-commits-the-step-files.md), [ADR-0051](0051-a-fresh-checker-finishes-each-step.md)). They stay on the run's branch. Dropping them loses little. A Step agent's commit is not a finished Step: in `mvdmio-suite`, the Checker's commit that followed changed source and tests in every pair we checked. After a rebase, only the newest commit on the branch is tested again. So a `git bisect` that stops inside a run tests code nobody proved green.

The landing commit's subject says what the change does and ends with the Issue's reference. The run writes it from the Spec, because an Issue's title often names the problem instead. The body lists each Step's title and carries the Issue's closing reference.

## Considered Options

- **A merge commit per run, with the Step commits underneath.** Rejected: only `git log --first-parent` shows one line per run. Plain `git log` and GitHub's commit list still show every commit. `/implement-yolo` also has no branch to merge.
- **One commit per Step**, folding each Step agent's commit into its Checker's. Rejected: the run would have to rewrite its branch with a scripted rebase before landing, which adds a new way for the land to fail. Each Step commit would still be untested after the rebase.
- **Keeping every commit, with subject lines that start with the Issue's reference.** Rejected: the log stays just as long. It only gets easier to search.
- **`git merge --squash` on the base branch.** Rejected: it stages the run's change on top of whatever the user had already staged in the original directory, so the commit after it would include the user's work.

## Consequences

- `/implement` and `/implement-oneshot` build the landing commit with `git commit-tree`, from the branch's final tree. Its parent is the base-branch commit the run rebased onto, held as a hash, not the branch's name. Then they fast-forward the base branch to it. When another session lands on the base branch after the rebase, the fast-forward fails, and the run rebases, re-tests, and tries again. The branch keeps its commits until the fast-forward succeeds, so that retry has them. Naming the branch would make the newer commit the parent while the tree still lacked it, so the fast-forward would succeed and undo that commit. On 2026-10-10 a run in `mvdmio-suite` nearly undid another run's fix this way. Then the run deletes the branch with `git branch -D`, once the branch and the base branch hold the same files.
- `/implement-yolo` folds every commit since its start into one landing commit on its own branch. A commit the user makes on that branch during the run is folded in too.
- A Step's Merge risk is judged by reverting that Step's change, because on the base branch only the whole run can be reverted.
- `/retro` reads an implement run's change from its landing commit.
- `/hillclimb` keeps its commits. Each Attempt it keeps is a measured change with its own before-and-after number, so those commits are the record of the work.
