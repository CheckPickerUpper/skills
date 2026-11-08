---
"checkpickerupper-skills": patch
---

**`audit-issues`**: an issue that closes as done or out of date with open checklist lines now says in the plan where each line goes (moved to a cause that stays open, or dropped with a reason), the approval page lists those fates, and `apply` makes the edits itself: it adds each moved line to its cause, records each move or drop, removes the lines and any heading they leave empty, then closes. **`close-issues`** recognises a moved line that gained a line id in its new issue, so close-issues accepts the close on the first run instead of refusing it after the owner approved.
