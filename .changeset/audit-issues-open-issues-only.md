---
"checkpickerupper-skills": patch
---

**`audit-issues`** reads and changes open issues only. It no longer lists closed issues with unticked checklist lines, open sub-issues, a decision with no `## Decision` section or a duplicate with no original, and never asks to reopen or edit one; on a large tracker those turned an audit of the open issues into a sweep of every issue ever closed. An open issue under a closed parent is still listed, to move under an open parent or to the top level.
