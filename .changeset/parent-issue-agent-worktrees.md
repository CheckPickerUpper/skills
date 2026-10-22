---
"checkpickerupper-skills": patch
---

Align **`conductor-mode`** and **`implementer-mode`** with one worktree per parent issue.

**`conductor-mode`** and **`implementer-mode`** (model-invoked) keep every owned
repository parent's sub-issues and helpers in the same worktree, with verified
commits pushed directly to its development or canonical branch. Briefs name
that shared parent path, and cleanup waits for the parent to finish. Existing
ownership and external-contribution rules still decide whether a PR workflow
is permitted.
