---
"checkpickerupper-skills": patch
---

close-issues: an issue with a reproduction section no longer closes as completed on passing tests alone. `close_issue.py reran` records a rerun of that reproduction under `## Reproduction rerun` and refuses a rerun that runs none of the reproduction's commands. `ready` and `completed` refuse until a recorded rerun shows the bug fixed, so an issue whose tests pass while its reproduction still fails stays open. Suggested by u/MiserableFlatworm337.
