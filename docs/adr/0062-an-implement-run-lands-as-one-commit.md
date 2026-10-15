# An implement run lands as one commit

Both implement commands land a run on the base branch as one **landing commit**: the run's whole change, named after what it does. Landing every commit a run makes would put all of them on the base branch: one commit per unit, a Bug fix's failing test before its fix, each fixer's commit, and a `wip:` commit from a halt. On 2026-10-08, seven runs in `mvdmio-suite` that landed every commit left between 7 and 18 commits each, most named for the run's own bookkeeping, which made `git log` slow to read for what changed and why.

The run still makes those commits, because a resume continues from them and `interrogate` reads the ordered sequence. They stay on the run's branch. After a rebase, only the newest commit on the branch is verified again, so a `git bisect` that stopped inside a run would test code nobody verified.

The landing commit's subject says what the change does and ends with the Issue's reference. The run writes it from the Spec, because an Issue's title often names the problem instead. The body lists each unit's title from the branch's `Unit:` trailers, a Bug fix's red and green output trimmed to the assertion and the counts, a Perf issue's baseline and post-fix numbers, a Hillclimb's baseline and final numbers with the ideas it tried and reverted, and the Issue's closing reference.

## Considered Options

- **A merge commit per run, with the unit commits underneath.** Rejected: only `git log --first-parent` shows one line per run. Plain `git log` and GitHub's commit list still show every commit. `/implement-yolo` also has no branch to merge.
- **Landing the ordered unit commits, as poteto-mode's Feature playbook stacks them for a pull request.** Rejected for now: the sequence proves itself to `interrogate` on the run branch, and the landing commit's Verification section carries the red-then-green excerpts a reviewer of the base branch would want. Reopen this when someone wants `git log` on the base branch to replay a run.
- **Keeping every commit, with subject lines that start with the Issue's reference.** Rejected: the log stays just as long. It only gets easier to search.
- **`git merge --squash` on the base branch.** Rejected: it stages the run's change on top of whatever the user had already staged in the original directory, so the commit after it would include the user's work.

## Consequences

- `/implement` builds the landing commit with `git commit-tree`, from the branch's final tree. Its parent is the base-branch commit the run rebased onto, held as a hash, not the branch's name. Then it fast-forwards the base branch to it. When another session lands on the base branch after the rebase, the fast-forward fails, and the run rebases, re-verifies, and tries again. The branch keeps its commits until the fast-forward succeeds, so that retry has them. Naming the branch would make the newer commit the parent while the tree still lacked it, so the fast-forward would succeed and undo that commit. On 2026-10-10 a run in `mvdmio-suite` nearly undid another run's fix this way. Then the run deletes the branch with `git branch -D`, once the branch and the base branch hold the same files.
- The Run directory is ignored by git from inside, so the branch's tree holds none of it and the run makes no deletion commit.
- `/implement-yolo` folds every commit since its start into one landing commit on its own branch. A commit the user makes on that branch during the run is folded in too.
- `/retro` reads an implement run's change from its landing commit.
- A Hillclimb lands as one landing commit too. Each Attempt it kept is a unit whose title carries its before-and-after number, so the body still records every measured change.
