---
name: audit-issues
description: "Audit a GitHub issue tracker: find open work hidden under closed issues, and give every open issue a checked verdict (done, duplicate, still real, or unsure with the check that would settle it). Use when asked to audit, clean up, triage, groom or sweep issues, or to say which open issues are still real. A script lists open issues under closed parents, issues closed with open work under them, duplicates of nothing and decisions closed without their answer; closes go through close-issues; scope decisions go to the owner."
short_description: "Audit a tracker: hidden open work and a verdict per issue."
allow_implicit_invocation: true
---

# Audit issues

A tracker drifts: work closes early with pieces still open, children stay open
under a closed parent, and old issues describe code that has since changed. An
audit finds that drift and says, for every open issue, whether it is still real.
It never closes an issue itself: each close goes through the `close-issues`
skill, and each scope decision goes to the owner.

<what-to-do>
1. **Find the hidden work.** Run
   `python3 <folder of this SKILL.md>/scripts/audit_issues.py --repo OWNER/REPO`.
   It lists open issues under closed parents, issues closed as completed with
   open sub-issues or unticked lines, duplicates of nothing, decisions closed
   without a `## Decision`, and decision issues waiting on the owner. Fix each
   structural finding as it says and rerun until it exits 0.
2. **Give every open issue in scope one verdict**, from a check run now, never
   from the issue's age or text:
   - **Done:** you ran the check that proves it. Close it with `close-issues`.
   - **Duplicate:** of a named issue. Close it with `close-issues`.
   - **Still real:** you reproduced it or read the code that still has it.
   - **Unsure:** name the one exact check that would settle it.
3. **Never decide scope.** Dropping a feature, changing a priority or answering
   a decision goes to the owner as a question, using the client's question
   tool where it has one, with the facts behind each choice.
4. **Report to the owner:** each issue closed, its reason and proof; each
   duplicate and the issue it went into; each issue left open, with its
   verdict; and the decisions waiting on them. Name every issue as a link with
   its title.

Done when the script exits 0, every open issue in scope has a verdict, and the
owner has the report.
</what-to-do>
