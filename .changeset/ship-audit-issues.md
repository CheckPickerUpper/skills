---
"checkpickerupper-skills": minor
---

Ship **`audit-issues`** in the **Productivity** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

`audit-issues` (model-invoked) loads when a tracker is to be audited, cleaned up, triaged, merged or swept. `scripts/audit_issues.py` has five commands:

| Command | What it does |
|---|---|
| `scan --repo R [--milestone M]` | Lists open work hidden under closed issues (exits 1 while any remains), milestones over 10 top-level issues, groups that look like one cause (error text, one bug in several languages, or two shared file paths or code names), weaker one-signal leads, and workaround premises. |
| `index --repo R --out FILE` | Writes one line per open issue, the index every batch agent reads in full. |
| `draft --repo R --title T --body-file F [--milestone M] [--parent N]` | Checks one issue before it is filed: refuses a likely duplicate cause, a workaround premise, or a milestone pushed past 10 causes until the draft records why it does not apply. |
| `plan --repo R --plan P [--verdicts F ...] --page PAGE` | Checks that every open issue in scope has a complete verdict and writes the short before-and-after page the owner approves, with its approval code. |
| `apply --repo R --plan P [--verdicts F ...] --approved CODE` | Applies the approved plan: creates new causes, moves slices under them, folds checkbox slices and duplicates in under `(was #N)`, and closes through close-issues, deepest first. Refuses a changed plan; resumes after a failure. |

Verdicts are done, duplicate, slice of a cause (checkbox or sub-issue), cause, wrong premise, out of date, still real and unsure, which needs the settling check and why it cannot run. The plan format is in `references/plan-format.md`.
