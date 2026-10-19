---
"checkpickerupper-skills": minor
---

Ship **`audit-issues`** in the **Productivity** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

`audit-issues` (model-invoked) loads when a tracker is to be audited, cleaned up, triaged or swept. `scripts/audit_issues.py --repo OWNER/REPO` reads every issue and lists open issues under closed parents, issues closed as completed with open sub-issues or unticked lines, duplicates of nothing, decisions closed without a `## Decision`, and decisions waiting on the owner; it exits 1 while any but the last remain. Every open issue then gets a checked verdict, each close goes through `close-issues`, and scope decisions go to the owner.
