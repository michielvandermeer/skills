# `/review-spec` runs `/validate-spec` after a write

Approved edits land in the Spec in the same run. Template shape and drift are `/validate-spec`'s job, and leaving them for a later typed command would skip them. After any approved change is written, `/review-spec` invokes `/validate-spec` on that Spec. Stopping after the write was rejected. Running `/validate-spec` during the judgement itself was rejected: that skill does not judge whether the Solution is good.
