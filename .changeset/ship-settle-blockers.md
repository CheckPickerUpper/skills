---
"checkpickerupper-skills": minor
---

Ship **`settle-blockers`** in the **Productivity** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

`settle-blockers` (model-invoked) makes an agent decide whether each blocked-by link or claimed blocker between GitHub issues is real before anyone waits on it. Work is blocked only when it cannot be done now, or doing it now means redoing part of it once the blocker lands; a shared file, a merge conflict, a related topic or an existing link never is. Unclear links go to cheap subagents in parallel, each answering the same two questions with file and symbol evidence.

- `scripts/blockers.py check` lists blocked-by links with no reason line, reason lines with no link, lines with no reason, and blockers that have closed. `keep` and `drop` change a link and its line under `## Blocked by` together and read the issue back.
