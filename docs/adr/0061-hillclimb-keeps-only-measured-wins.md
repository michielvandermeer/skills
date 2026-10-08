# `/hillclimb` improves one number by keeping only measured wins

The plugin carries `/hillclimb`, adapted from the Hillclimb playbook in Lauren Tan's pstack. It runs a long effort to push one measured number in one direction, such as how long a test suite takes. It tries one change at a time and keeps a change only when the measurement shows it helped and the tests still pass.

The need came back four times in six weeks, all on the `mvdmio-suite` test suite. Each time, the method was carried by hand. Two efforts ran under `/goal` with a long prompt, and the second prompt lost words when it was pasted. An agent memory file held what had been tried, kept, and disproven, and a handoff prompt carried it to the next session. The fourth effort went through a Spec. But an implement run builds Steps it planned up front, and it has no way to try a change, measure it, and throw it away. Three of the four efforts were open-ended, so nobody could name their changes in advance.

The shape follows from what those efforts learned:

- **One Attempt at a time.** One run on a shared machine swings by ±50% when other sessions are busy. So both sides are measured in the same hour, alternating, at least 3 runs each, and a gap smaller than the spread counts as no change.
- **A sub-agent writes, and the driving session judges.** The **Climber** writes each Attempt and leaves it uncommitted. The driving session measures it, runs the tests, and keeps or reverts it. Over eight hours, the driving session then holds only the log and the numbers, and no agent judges its own change.
- **The Attempt log is committed.** It lives at `.agents/hillclimbs/<slug>/` beside the frozen measurement script, one folder per number. Most of what each round learned was what not to try again. Only a record in the repo reaches the next round on every host.
- **A target and a minimum number of Attempts decide when to stop.** A time limit can sit on top. Both `/goal` rounds read "max 8 hours" as a ceiling and stopped after 2 to 2.5 hours. A target alone lets one lucky early win end the effort.
- **It lands like `/implement`.** It works in its own worktree. Before landing, a fresh `/code-review` reviews the whole branch. It then rebases, runs the tests until Green, fast-forwards the **Base branch**, and pushes under [ADR-0028](0028-implement-claims-its-issue-and-pushes-only-what-lands.md). After both `/goal` rounds the user read the result and said to land it, and both rounds left their worktree and branch behind.
- **The agent may load it.** A request such as "my test suites are running too slow, let's improve that" started the first effort, and nobody types a command for that. So `/diagnosing-bugs` keeps "slow" only for something that got slower than it was, and `/hillclimb` takes requests to make a number better.

## Considered Options

- **No skill: write the method into a `/goal` prompt or a Spec each time.** Rejected: that is the hand-carrying this skill ends, and a Spec cannot name changes nobody knows yet.
- **Only the measurement rules, added to `/diagnosing-bugs`.** Rejected: no loop, no stop rule, and no record that carries over to the next effort.
- **Copying pstack's playbook as it is.** Rejected: it points at pstack skills this plugin lacks, names a Grok model, and ends in a pull request. Its `benchmark-checklist` survives as the skill's `MEASURE.md`.
- **The log outside the repo, as pstack keeps it, or in agent memory.** Rejected: the next effort cannot find it, and agent memory belongs to one host while this plugin also runs on Grok.
- **The log as comments on the Issue.** Rejected: an effort started from a plain request has no Issue, and a hundred comments are hard to scan.
- **The driving session writes every change, as both `/goal` rounds did.** Rejected: hours of diffs and logs pile into one context, and the agent that wrote a change would judge it.
- **Attempts side by side, each in its own worktree, as pstack and the first effort did.** Rejected: side-by-side runs on one machine measure each other's load. [ADR-0045](0045-implement-runs-steps-one-at-a-time.md) rejected parallel worktrees for Steps on other grounds too.
- **Stopping with the branch for the user to land, or opening a pull request.** Rejected: an unattended effort leaves its worktree and branch behind, and the implement commands never open a pull request.
- **The driving session reads each diff before measuring it, as pstack does.** Rejected: every diff would fill the context the Climber keeps small. One review of the whole branch before landing does the same job.
- **A Safety fact and a Prover for each kept Attempt.** Rejected: the measurement and the tests are the evidence, and the driving session ran both itself rather than the Climber.
- **User-invoked only.** Rejected: the first effort began as a plain request, and the agent could not have reached a user-only skill.

## Consequences

- `/hillclimb` joins the Named session skill list ([ADR-0038](0038-named-session-skills-apply-high-priority-retro.md)) and starts a retrospective even when the agent loaded it.
- The Climber runs at `effort: medium` ([ADR-0049](0049-spec-bound-agents-keep-the-session-model.md)).
- The final measurement after the rebase compares the result with the Base branch. It goes in the report and does not block landing.
- A Hillclimb writes no Changelog entry. Every number so far is one only developers notice, and `/document-changes` can backfill one from git.
- The README credits pstack (MIT).
