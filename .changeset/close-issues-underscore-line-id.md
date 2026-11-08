---
"checkpickerupper-skills": patch
---

**`close-issues`** reads a checklist line id that contains an underscore, such as `- [ ] all_or_none: <text>`, and a commit saying `Part of #N: all_or_none` proves it. Before, such a line was read as having no id and stayed open no matter which commit claimed it.
