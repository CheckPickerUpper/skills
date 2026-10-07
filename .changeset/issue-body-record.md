---
"checkpickerupper-skills": patch
---

Make **`to-issues-clearly`** keep every issue fact in the issue body, so a settled decision never reads as open.

`to-issues-clearly` (model-invoked) now records a settled decision by editing the decision issue itself: a `## Decision` section at the top, ticked boxes, a link to the build issue, then closing it. A decision recorded only in a comment left the issue open, and it read as undecided. A replaced issue now gets `Replaced by` in its body instead of a closing comment. Issue bodies link to a fact another issue owns instead of copying it.
