# Code review

`/skills:code-review` reviews the changes since a fixed point along two axes, Standards and Spec, in two parallel `skills:reviewer` agents, and reports both side by side. It writes nothing.

## Sub-features

- `review-two-axes` dispatches two reviewers and reports `## Standards` and `## Spec` with a one-line summary per axis.
- `review-no-spec` skips the Spec axis as "no spec available" when the user says there is none.
- `review-ask-fixed-point` asks for a fixed point when none is given.
- `review-bad-ref` fails early on an unknown ref or an empty diff.
- `review-again` re-reviews only what changed since the last review in the same conversation, marking each earlier finding fixed or still open.

## How to get to it (user POV)

- Type `/skills:code-review <fixed-point>`, such as a commit, branch, or tag.
- Type `/skills:code-review` alone; it asks for the fixed point.
- Ask in plain words, such as "review the changes since main"; the skill is model-invoked.

## Driving it with verify.py

Preconditions:

- A run whose scratch repo holds a change to review. In a fresh run, write a small source file into the scratch repo and commit it, so `HEAD~1..HEAD` is non-empty. A miss a design principle names, such as two same-typed parameters that mean different things (`user_id: str, order_id: str`), gives the Standards axis something to find.
- Optionally, an Issue file at `.agents/issues/<slug>.md` describing what the change should do, for the Spec axis.

- **Review.** Run `verify.py turn <run> "/skills:code-review HEAD~1"`. With no Issue, the skill asks for the Spec. Run `verify.py turn <run> "there is none"`.
- **Two reviewers.** The summary lists two dispatches of `skills:reviewer`. Their transcripts are under `transcripts/<session>/subagents/`.
- **Report.** The final message has `## Standards` and `## Spec`, the Spec axis reads "no spec available", and a summary line names the worst finding per axis.
- **Read-only.** `scratch-NN.txt` shows the same `git log` and a clean status as before the review.
- **Plain request.** In another run, `turn <run> "review the changes since HEAD~1"`. The summary shows `skills:code-review` under `skills invoked by the model`.
- **Review again.** In a fresh run, commit a source file with two Standards misses, then `turn <run> "/skills:code-review HEAD~1"` and `turn <run> "there is none"`. The summary line ends with `reviewed up to` and the short SHA of `HEAD`. Then, in the same run:
  1. Fix the first miss only, commit, and `turn <run> "review it again"`. The Standards section lists the first finding as `Fixed:` and the second as `Still open:`, one line each, with nothing about lines the fix did not touch, and the summary line names the new `HEAD`'s short SHA. The Standards reviewer's diff command in `transcripts/<session>/subagents/` runs from the first review's SHA.
  2. Commit a change that adds a new miss and `turn <run> "review it again"`. The earlier findings come first by status, then the new miss as a new finding.
  3. `turn <run> "review all of it again"`. The reviewers' diff commands run from `HEAD~3`, and the report has no `Fixed:` or `Still open:` lines.
  4. `git log` and `git status` in the scratch repo are unchanged by the reviews, and no Issue was filed.
- **Bad ref.** `turn <run> "/skills:code-review no-such-ref"` ends with an error naming the ref, and dispatches no reviewer.

## Gotchas

- The reviewers run on Opus at high effort; a review costs a few dollars.
- With an Issue present, the skill takes the Spec from it without asking. Write the Issue only for the Spec-axis journey.
