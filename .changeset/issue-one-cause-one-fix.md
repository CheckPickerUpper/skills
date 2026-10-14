---
"checkpickerupper-skills": patch
---

Make **`to-issues-clearly`** file one issue per cause and fix, so the same bug or the same mechanical change no longer becomes dozens of issues.

`to-issues-clearly` (model-invoked) used to tell agents to err granular and split whenever parts could land separately, which turned one false refusal seen in three repositories into three issues and one change applied to forty rules into forty issues. It now defines an issue as one cause with one fix: a new sighting of a filed cause is added to that issue's evidence, the duplicate search looks for the cause (rule, symbol, owner, command) as well as the words, and the same change across many targets is one issue with a checklist that several pull requests can close in parts.

- Whether work can land separately now decides pull requests, not issues.
- Checklist targets under one change count as one acceptance criterion.
