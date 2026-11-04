---
"checkpickerupper-skills": patch
---

**`audit-issues`**: two audits of the same repository running at once no longer crash with a missing-file error while saving the local issue copy; each write uses its own temporary file and the copy is always whole.
