# `pr` is model-invoked so every pull request description carries evidence and merge risk

The plugin carries `pr`, adapted from upstream's skill of the same name. The agent loads it on its own whenever it writes or edits a pull request description. Agents here rarely write one: 3 of about 2,100 sessions between late August and early October 2026 did. So its one-line description sits in every session's context to serve a few. That is the price of reaching every description. An agent opens a pull request because someone asked for one in passing, and nobody types `/pr` first.

A description holds three sections: a small picture of the change, before-and-after evidence, and the **Merge risk**. The evidence comes from a run on the exact code being pushed. A screenshot goes up with `gh --attach`, never into the repo.

## Considered Options

- **No skill.** Rejected: `/plain-language` alone gives a description no evidence and no merge risk, and those are what a reviewer needs.
- **A user-invoked `/pr`.** Rejected: it fires only when someone remembers it, which is the case `/wizard` is model-invoked to avoid ([ADR-0044](0044-wizard-is-model-invoked.md)).
- **Copying upstream as it is.** Rejected: it reads a `GLOSSARY.md` that this plugin calls `CONTEXT.md`. Its "S-tier" and "A-tier" ranking of evidence competes with the Proof ladder and accepts output nobody re-ran. Its "keep prose brief" falls below the plain-language bar ([ADR-0009](0009-plain-language-for-output-not-source.md)).
- **Committing screenshots to the branch.** Rejected: the image would stay in the repo's history for good.
- **A hard Merge risk stops an implement run from pushing.** Rejected: a Step agent's judgement would decide whether the push happens. A repo where a push deploys already turns the push off ([ADR-0028](0028-implement-claims-its-issue-and-pushes-only-what-lands.md)). Elsewhere the hard part, such as running a migration, happens later and under the user's control.

## Consequences

- The description stays one line and names only when to load the skill.
- `pr` stays off the Named session skill list ([ADR-0038](0038-named-session-skills-apply-high-priority-retro.md)).
- Every implement Step records a Merge risk beside its Safety fact. The Checker corrects it, and the final report lists it with each Step's Safety fact and Proof. A description written after a run starts from those lines.
- `pr` shapes the description only. The implement commands still never open a pull request.
