---
name: audit-issues
description: "Audit a GitHub issue tracker: group issues by the fix that would make them all disappear, rewrite workaround premises to the proper fix, close what is done, duplicated or out of date, and show the owner a short before-and-after page to approve before anything changes. Use when asked to audit, clean up, triage, groom, merge or sweep issues, or to say which open issues are still real. A script finds hidden open work, suggests likely slices of one cause and oversized milestones, checks the plan, and applies it only once approved; closes go through close-issues; scope decisions go to the owner."
short_description: "Audit a tracker: one issue per cause, approved before applied."
allow_implicit_invocation: true
metadata:
  when: "the issue list has gone messy"
  situation: Filing or closing issues
---

# Audit issues

A tracker drifts: one cause gets filed ten times from ten sightings, issues ask
for workarounds instead of the fix, work closes early with pieces still open,
and old issues describe code or releases that have since moved on. An audit
turns the tracker back into one issue per cause, each with its slices under it,
and shows the owner the result before anything changes.

The script is `python3 <folder of this SKILL.md>/scripts/audit_issues.py`
(below, `audit`). Its plan format is in
[references/plan-format.md](references/plan-format.md). Every close it makes
runs through the `close-issues` skill's script, so that skill must be installed
beside this one.

<what-to-do>
1. **Scan.** Run `audit scan --repo OWNER/REPO [--milestone TITLE]`. It lists
   open work hidden under closed issues (fix each as it says and rerun until it
   exits 0), milestones with more than 10 top-level issues, groups of issues
   that look like slices of one cause, weaker one-signal leads, and issues
   whose asked-for fix reads like a workaround. Its groups are leads; you
   still read the issues before calling them one cause.
2. **Split the work when there is a lot of it.** Past about 100 open issues,
   write the full index with `audit index --repo R --out INDEX.tsv`, cut the
   issues into batches of about 100 by area, and give each batch to its own
   agent (where the client allows sub-agents, under its rules) together with
   the whole index, so it can spot duplicates and causes outside its batch.
   Each agent writes its verdicts into its own file, never a shared one.
3. **Give every open issue in scope one verdict**, from a check run now, never
   from the issue's age or wording:
   - **Done:** you ran the check that proves it; the proof is a commit, a test
     result or a walk through the product.
   - **Duplicate:** of a named issue that stays open.
   - **Slice of a cause:** group issues by the fix that would make them all
     disappear, not by how each was reported. A slice is a checkbox in the
     cause's `## Done when` (its details are copied into the cause and it
     closes), or a sub-issue that stays open because it is a real separate
     piece of work.
   - **Cause:** its own issue, with the reason it is a different cause from
     the ones it looks like.
   - **Wrong premise:** ask of every issue whether the fix it asks for is a
     workaround: raising a timeout, adding a retry, an exceptions list,
     running things one at a time, one copy per language. If so, give it a
     title and a `## Proper fix` for the real fix, and hang it under the
     issue that owns that fix.
   - **Out of date:** the code or release it describes has moved on ("Release
     0.1.166" after 0.1.170 shipped). Name the evidence; this is not a scope
     decision and does not wait on the owner.
   - **Still real:** you reproduced it or read the code that still has it.
   - **Unsure** is not a parking spot. Run the check that settles it. Unsure
     stands only when that check is truly impossible here, and the verdict
     names the check and why it cannot run.
4. **Keep each milestone to about 10 causes.** A milestone that ends with more
   needs a reason in the plan; most often the excess are slices of a cause
   already there.
5. **Never decide scope.** Dropping a feature, changing a priority or answering
   a decision goes to the owner as a question, using the client's question
   tool where it has one, with the facts behind each choice.
6. **Show the plan before changing anything.** Run
   `audit plan --repo R --plan PLAN.json [--verdicts BATCH.json ...] --page PAGE.md`
   until it exits 0. It writes a short page: open and top-level counts before
   and after per milestone, each cause with its slice count, what closes, and
   every unsure issue with its check. Show the owner that page, as a page they
   can open where the client can publish one, never the plan file itself.
7. **Apply only what they approved.** Run
   `audit apply --repo R --plan PLAN.json [--verdicts ...] --approved CODE`
   with the code `plan` printed. It refuses a plan that changed since the page
   was written, then creates new causes, moves slices under their causes,
   copies folded details in, and closes through close-issues, deepest issues
   first. A failed run is safe to rerun; it resumes.
8. **Report to whoever asked**, in their channel: the user, or the
   conducting agent when an agent asked, never only printed
   where nobody is looking. Lead with outcomes as counts before and after
   ("312 open issues are now 41 causes in 4 milestones; 120 closed with
   proof"), then the decisions waiting on the owner. Name every issue as a
   link with its title.

Done when scan exits 0, every open issue in scope has a verdict, the owner
approved the page, apply finished, and the person who asked has the report.
</what-to-do>
