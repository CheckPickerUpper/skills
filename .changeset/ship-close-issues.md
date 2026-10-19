---
"checkpickerupper-skills": minor
---

Ship **`close-issues`** in the **Productivity** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

`close-issues` (model-invoked) loads whenever an issue is about to close. It closes issues through `scripts/close_issue.py`, which refuses a close while sub-issues or checklist lines are open and records the reason in the issue body: the proof under `## Proof`, the owner's quoted decision under `## Not planned`, or, for a duplicate, the survivor carrying the details under `(was #N)`. `sweep` finds open issues under closed parents, issues closed with open work under them, duplicates of nothing, and decisions closed without a `## Decision`. `to-issues-clearly` now says each sub-issue is closed by the commit that finishes it, with `Part of #N` on earlier commits.
