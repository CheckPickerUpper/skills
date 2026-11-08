---
"checkpickerupper-skills": patch
---

**`close-issues`** no longer reports a checklist line as lost when it is given a line id (`- [ ] <id>: <same text>`), so an issue's lines can get ids before the commit that proves them. A line deleted outright is still refused.
