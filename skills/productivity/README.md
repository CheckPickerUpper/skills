# Productivity

General workflow tools.

| Skill | The problem it fixes | Example |
|---|---|---|
| [audit-issues](./audit-issues/SKILL.md) | The tracker has hundreds of issues, many duplicated or already done, and nobody knows which are still real. You approve a before-and-after page before anything changes. | `/audit-issues OWNER/REPO` |
| [check-protection](./check-protection/SKILL.md) | Agents rerun full suites and checks whose result is already known, and the time goes nowhere. | `/check-protection which checks does this commit need?` |
| [close-issues](./close-issues/SKILL.md) | Agents close issues that are not done, and later nobody can tell why one closed. A script refuses the close until the proof is written into the issue. | `/close-issues #142 is finished` |
| [compose-goal](./compose-goal/SKILL.md) | Handing work to another agent loses the outcome, the issue links and how to prove it works. | `/compose-goal hand #142 to another agent` |
| [dependency-trace](./dependency-trace/SKILL.md) | You build a feature in the wrong order because nobody mapped what it needs to exist first. | `/dependency-trace what does checkout depend on?` |
| [issues-to-outcomes](./issues-to-outcomes/SKILL.md) | Status reports are lists of issue titles that mean nothing to the person reading them. | `/issues-to-outcomes what landed this week` |
| [make-diagram](./make-diagram/SKILL.md) | Agent-drawn diagrams overlap, use jargon and leave out how the thing actually works. A script renders the drawing and refuses those defects. | `/make-diagram how a payment goes from cart to receipt` |
| [settle-blockers](./settle-blockers/SKILL.md) | Issues get marked blocked over a shared file or a merge conflict, so work waits for no reason. | `/settle-blockers OWNER/REPO#88` |
| [to-issues-clearly](./to-issues-clearly/SKILL.md) | Agent-filed issues have vague titles you must open to understand, and no clear point at which they are done. | `/to-issues-clearly turn this plan into issues` |
