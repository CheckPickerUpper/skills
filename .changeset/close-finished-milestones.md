---
"checkpickerupper-skills": patch
---

close-issues: a close that leaves its milestone with no open issue now closes the milestone too. GitHub never closes a milestone by itself, so a milestone whose every issue was done stayed open and kept showing as 100% wherever open milestones are listed. `close_issue.py` reads the issue's milestone after every close (completed, duplicate, out-of-date or not planned) and closes it when nothing in it is still open.
