---
"checkpickerupper-skills": minor
---

Ship **`issues-to-outcomes`** in the **Productivity** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

`issues-to-outcomes` (model-invoked) makes an agent report finished work as what its reader would notice, instead of a list of issue and PR titles. The report opens with how much of the work shows in the product, describes each visible change as the situation before and now, and describes the invisible work as what was stuck or silently wrong and no longer is. References trail the sentence they support.

- `scripts/check_report.py` reads a draft report and refuses it while any line opens with an issue or pull-request reference, naming each line.
