---
"checkpickerupper-skills": patch
---

**`to-issues-clearly`** settles every blocked-by edge with `settle-blockers` before showing the set, and creates each edge with its reason line through `settle-blockers`' `keep` command.

The user is no longer asked whether each blocking edge is real; the agent decides with the same test `settle-blockers` uses, and the set shows each edge with its reason.
