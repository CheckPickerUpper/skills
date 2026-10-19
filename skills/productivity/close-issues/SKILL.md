---
name: close-issues
description: "Close GitHub issues only with proof. Use every time an issue is about to close or has just closed: before `gh issue close`, before pushing a commit with `Closes #N`, when work looks done, when marking a duplicate, and when someone says drop it or won't fix. Closes through a script that refuses open sub-issues and unticked lines, and records the proof, the duplicate's carried details or the owner's decision in the body."
short_description: "Close issues only with proof."
allow_implicit_invocation: true
---

# Close issues

A closed issue tells everyone the work is finished or deliberately dropped.
A close without proof, or with open work under it, hides that work from every
view, and GitHub does nothing to stop it. Every close in this skill goes
through `scripts/close_issue.py`, which refuses those closes and reads the
issue back afterwards. Never close with a bare `gh issue close`.

<what-to-do>
1. **Check it can close.** Run
   `python3 <folder of this SKILL.md>/scripts/close_issue.py ready --repo OWNER/REPO --issue N`.
   It lists open sub-issues and unticked checklist lines. Finish each one,
   move it under an open parent, or close it with its own reason first.
2. **Pick the reason from the evidence:**
   - **Completed.** Read the current code and run the check that proves each
     "Done when" line: the passing test, the commit that shipped it, a walk
     through the product. The issue's text describes the past; only the check
     says it is done now.
     `close_issue.py completed --repo R --issue N --proof "<commit url>" --proof "<test and its result>"`
     writes the proof under `## Proof` and closes it. A commit with
     `Closes #N` closes the issue when it is pushed: run `ready` before that
     commit, and `completed` with the commit as proof right after the push.
     A commit that does only part of the work says `Part of #N` and ticks
     its checklist line.
   - **Duplicate.** Copy every detail the surviving issue lacks into its
     body, word for word, under a line ending `(was #N)`, then run
     `close_issue.py duplicate --repo R --issue N --of M`.
   - **Not planned.** Dropping work is the owner's call, and a bug closed as
     won't fix is the owner's call too. Ask them, then quote their answer:
     `close_issue.py not-planned --repo R --issue N --owner-said "<their words>"`.
     Age, noise and "nobody has touched it" are never reasons.
3. **A decision issue** closes as completed once its answer is written under
   `## Decision` in the body; `ready` refuses it until then.

Done when the script printed "closed as <reason>" for the issue.
</what-to-do>

