---
"checkpickerupper-skills": patch
---

Make **`to-issues-clearly`** file one issue per cause and fix, so the same bug or the same mechanical change no longer becomes dozens of unrelated issues.

`to-issues-clearly` (model-invoked) used to tell agents to err granular and split whenever parts could land separately, which turned one false refusal seen in three repositories into three issues and one change applied to forty rules into forty issues. It now defines an issue as one cause with one fix: a new sighting of a filed cause is added to that issue's evidence, and the duplicate search looks for the cause (rule, symbol, owner, command) as well as the words. When one cause's fix lands in pieces, the cause is the parent issue and each piece is a GitHub sub-issue closed by exactly one pull request, so one issue, one pull request still holds.
