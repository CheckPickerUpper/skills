---
"checkpickerupper-skills": patch
---

Make **`to-issues-clearly`** test every blocked-by edge and check the published set, so no issue sits idle behind a blocker that is not real.

`to-issues-clearly` (model-invoked) now applies a fixed blocker test before adding any blocked-by edge. Merge order, rebase-time checks, "cleaner after X" and closed issues never count as blockers, and an edge that only one piece depends on goes on that piece's own issue. Each edge gets a reason line under `## Blocked by` in the blocked issue's body, which the user reviews with the breakdown. After wiring, the skill runs the new `scripts/issues_check.py` on every issue it created or edited and fixes each finding until the check exits 0. The final report quotes the check's summary of labels, milestones and edges.

- `issues_check.py --repo OWNER/REPO ISSUE...` reads each issue fresh from GitHub. It flags `stale-blocker`, `parent-blocker`, `missing-reason` and `orphan-reason`, and exits 0, 1, or 2 when a read fails.
