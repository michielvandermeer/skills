---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

Implement the work described by the user in the spec.

# Process

1. Create a new branch on a new worktree for this session.
2. If the spec is large, start with the following prompt: `/goal implement <spec>`. Otherwise you may implement in the current session.
3. Once the spec is implemented, run `/code-review` and fix all recommended issues.
4. Once code review is done, run `/improve-data-structures`.
5. Commit the changes to the branch
6. Merge the branch for this session with master, then delete the branch and the worktree.
7. Provide a summary of all the work in this session to the user.