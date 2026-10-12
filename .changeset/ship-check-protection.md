---
"checkpickerupper-skills": minor
---

Ship **`check-protection`** in the **Productivity** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

`check-protection` (model-invoked) asks what each proposed check protects that nothing cheaper already protects. It helps agents reuse complete evidence, choose focused proofs, examine every nested audit step, and name real reasons for reruns and waits while preserving required and disabled gates.

- `scripts/check_decisions.py` refuses an audit record with missing justification, invalid choices or duplicate commands. It checks completeness; the agent judges whether the protection is real.
