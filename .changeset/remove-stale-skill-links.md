---
"checkpickerupper-skills": patch
---

Remove stale installed links when a skill source is renamed or deleted.

The local skill linker removes only symlinks it owns whose source no longer
contains a skill. Foreign links and real directories stay in place.
