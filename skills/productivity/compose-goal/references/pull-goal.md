# Pull Goal

Use this branch when the user provides a /goal directive, a gist reference, or
asks to pull an existing goal.

## 1. Resolve the gist reference

Accept a bare gist id, a gh:gist:<id> reference, or a
https://gist.github.com/.../<id> URL. If the prompt contains more than one
reference, use the first one and ignore surrounding prose.

## 2. Pull the goal text

compose-goal names the gist's file goal.md. Pull it by that name:

~~~bash
gh gist view <id> --filename goal.md --raw
~~~

Save the output to a scratchpad file before reading or acting on it. If gh is
missing, unauthenticated, or the gist is inaccessible, surface the exact error
and stop.

If the pulled goal names GitHub issues, read each live issue from the repository
and number recorded in the goal before changing files. The gist is not a frozen
copy of issue bodies.

## 3. Continue or stop

If the current message is a /goal directive or asks you to complete or run the
goal, follow it exactly. Preserve its human outcome, live issue references,
real-behavior proof, and hard-blocker contract.

Otherwise reply with one line naming the scratchpad file. Do not summarize the
goal body unless explicitly asked.
