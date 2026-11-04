---
name: close-issues
description: "Close GitHub issues only with proof. Use every time an issue is about to close or has just closed: before `gh issue close`, before pushing a commit with `Closes #N`, when work looks done, when marking a duplicate, and when someone says drop it or won't fix. Closes through a script that refuses open sub-issues, checklist lines no landed commit proves (a box ticked by hand counts for nothing), lines deleted without a recorded move or drop, and a bug whose reproduction was never rerun or still fails, and records the proof, the duplicate's carried details, the out-of-date evidence or the owner's decision in the body."
short_description: "Close issues only with proof."
allow_implicit_invocation: true
metadata:
  when: "an issue is about to be closed"
  situation: Filing or closing issues
---

# Close issues

A closed issue tells everyone the work is finished or deliberately dropped.
A close without proof, or with open work under it, hides that work from every
view, and GitHub does nothing to stop it. Every close in this skill goes
through `scripts/close_issue.py`, which refuses those closes and reads the
issue back afterwards. Never close with a bare `gh issue close`.

A checklist box is a view of what landed, never a claim. Each line starts with
a short id, `- [ ] cleanse: Cleanse effects`, and a line is done only when a
commit on the landing branch names it: `Part of #N: cleanse` (several ids
separated by commas; `Closes #N: cleanse` on the last). The script works out
every box from those commits and resets any box ticked by hand. A line leaves
the body only with a record under `## Checklist changes`:
`- cleanse: moved to #M` (the script checks #M has it) or
`- cleanse: dropped, <reason>`; it reads the body's edit history to find lines
that disappeared. Run every command inside a checkout of the repository.

<what-to-do>
1. **Check it can close.** Run
   `python3 <folder of this SKILL.md>/scripts/close_issue.py ready --repo OWNER/REPO --issue N`.
   It lists open sub-issues, unproved lines and lines removed without a
   record. Finish each one, move it under an open parent, or close it with its
   own reason first. `close_issue.py sync --repo R --issue N` sets the boxes to
   what has landed.
2. **Pick the reason from the evidence:**
   - **Completed.** Read the current code and run the check that proves each
     "Done when" line: the passing test, the commit that shipped it, a walk
     through the product. The issue's text describes the past; only the check
     says it is done now.
     When the issue has a reproduction ("Steps to reproduce", "Reproduction"),
     rerun those exact steps on the fixed code and record what happened:
     `close_issue.py reran --repo R --issue N --ran "<the reproduction's command>" --saw "<what it did>" --result fixed`.
     Tests passing is not this rerun, and the script refuses a rerun that runs
     none of the reproduction's commands. If the tests pass but the
     reproduction still fails, the tests miss the bug: record it with
     `--result still-fails`, leave the issue open, and keep working.
     `ready` and `completed` refuse until a rerun shows it fixed.
     `close_issue.py completed --repo R --issue N --proof "<commit url>" --proof "<test and its result>"`
     adds the proof under `## Proof`, keeping any proof from an earlier close, and closes it. A commit with
     `Closes #N` closes the issue when it is pushed: run `ready` before that
     commit, and `completed` with the commit as proof right after the push.
     A "Done when" line that can only pass once the commit exists, such as an
     exact-commit gate or a push, goes the other way round: the commit says
     `Part of #N`, and after the real pass a `## Proof` line
     `- <line id>: <link to the pass>` proves it; then `ready` and `completed`
     close the issue with that commit as proof. Never add an empty commit to
     carry `Closes #N`.
     A commit that does only part of the work says `Part of #N: <line id>`.
     Never tick a box by hand; the script derives it.
   - **Duplicate.** Copy every detail the surviving issue lacks into its
     body, word for word, under a line ending `(was #N)`, then run
     `close_issue.py duplicate --repo R --issue N --of M`.
   - **Out of date.** The code or release the issue describes has moved on
     ("Release 0.1.166" after 0.1.170 shipped). That is evidence, not a scope
     call, so it needs no owner:
     `close_issue.py out-of-date --repo R --issue N --evidence "<the commit, release or code that moved on>"`.
   - **Not planned.** Dropping work is the owner's call, and a bug closed as
     won't fix is the owner's call too. Ask them, then quote their answer:
     `close_issue.py not-planned --repo R --issue N --owner-said "<their words>"`.
     Age, noise and "nobody has touched it" are never reasons.
3. **A decision issue** closes as completed once its answer is written under
   `## Decision` in the body; `ready` refuses it until then.

**Install the pre-push check once per repository,** so a `Closes #N` commit
cannot close an issue on push while the script would refuse it. Add this line
to the repository's pre-push hook (create `.git/hooks/pre-push` if it has none,
and make it executable):
`python3 <folder of this SKILL.md>/scripts/close_issue.py pre-push "$1" "$2" || exit 1`.
It refuses the push and lists what is missing; say `Part of #N: <line id>`
instead, or finish the work.

GitHub never closes a milestone itself: when a close leaves its milestone with
no open issue, the script closes the milestone too.

Done when the script printed "closed as <reason>" for the issue.
</what-to-do>

