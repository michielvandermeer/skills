---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

Implement the work described by the user in the spec.

# Process

1. If the spec is large, start with the following prompt: `/goal implement <spec>`. Otherwise you may implement in the current session.
2. Once the spec is implemented, run `/code-review` and fix all recommended issues.
3. Once code review is done, run `/improve-data-structures`.
4. When all is done, commit the changes and provide a summary of all the work to the user.
