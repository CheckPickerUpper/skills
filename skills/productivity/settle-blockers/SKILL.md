---
name: settle-blockers
description: "Decide whether each blocked-by link or claimed blocker between GitHub issues is real, and record the verdict on the issue. Use before calling work blocked, waiting on another issue, or sequencing issues; when picking what can run in parallel; when reviewing or creating blocked-by edges; and when an agent reports 'blocked on #N'. A blocker is real only when the work cannot be done now or doing it now means redoing it; shared files, merge conflicts and relatedness never are. Sends cheap subagents to settle unclear links, then keeps each real link paired with its reason and removes the rest."
short_description: "Settle which issue blockers are real, and record why."
allow_implicit_invocation: true
---

# Settle blockers

Waiting costs time, so every wait has to buy something. An issue is
**blocked** only when one of these is true:

- **Missing**: it needs something only the blocker delivers (a function, a
  table, an API, a decision), and building that here would duplicate the
  blocker's work.
- **Rework**: doing it now means redoing part of it once the blocker lands.

Everything else is ready now. That includes touching the same file, an expected
merge conflict, a related topic, a preferred order, "safer to wait", a big or
important blocker, and a link that already exists. A conflict is fixed in
minutes at merge time; waiting costs the whole blocker.

This skill settles and records. Starting the work it finds ready is a separate
step the owner calls for.

## 1. List what needs a verdict

<what-to-do>
Run the check on the repository, or on the issues in question:

```bash
python3 <folder of this SKILL.md>/scripts/blockers.py check --repo OWNER/REPO [--issue N ...]
```

It lists every blocked-by link with no reason line, every reason line with no
link, every line with no reason, and every blocker that has already closed.
Add to the list any blocker someone claims in conversation ("blocked on #N")
and any link the owner asks you to re-judge.

Done when every candidate is on one list: the check's findings plus the
claimed and questioned blockers.
</what-to-do>

## 2. Judge each one

<what-to-do>
For each candidate, read both issues and answer two questions with the exact
thing as evidence: a function, table, file or decision, by name.

1. What does this issue need that only the blocker delivers?
2. If this issue lands first, which part of it changes when the blocker lands?

An answer that names a real thing makes the blocker real (Missing or Rework).
"Nothing" to both makes it not a blocker. A closed blocker no longer blocks.

When an answer needs reading code, or you are unsure, find out; uncertainty is
never a verdict. Send one subagent per unclear link, all at once, on the
lightest model your client offers (Haiku in Claude Code), with this brief:

> Read issue A (URL) and issue B (URL) and the code each one changes. Answer:
> (1) What does A need that only B delivers? (2) If A lands first, which part
> of A changes when B lands? Name each thing by file path and symbol, or say
> "nothing". Reply with: verdict (blocked or ready), kind (missing, rework or
> none), the evidence, and one sentence a stranger could read as the reason.

Accept a subagent's verdict when its evidence names a real file or symbol you
can open. When two answers conflict, the evidence is vague, or a "ready"
verdict would remove a link someone added on purpose, read the code yourself
and decide.

Done when every candidate has a verdict whose reason names the exact thing, or
says plainly that nothing is needed and nothing would be redone.
</what-to-do>

## 3. Record every verdict

<what-to-do>
A real blocker is a GitHub blocked-by link plus a line under `## Blocked by`
in the blocked issue's body, kept in step by the script:

```bash
# real: adds the link if missing and writes the reason line
python3 <folder>/scripts/blockers.py keep --repo OWNER/REPO --issue N --blocker REF \
  --reason "cannot prove X until B adds Y; doing it now means rewriting Z"
# not real, or the blocker closed: removes the link and the line
python3 <folder>/scripts/blockers.py drop --repo OWNER/REPO --issue N --blocker REF
```

The reason is one sentence naming what is missing or what would be redone.
Each command reads the issue back and fails unless the link and the line agree.
Then run step 1's check again.

Done when the check exits 0 for every issue you judged, and you have reported
each verdict to the owner: which links you kept and why, and which you removed
and why.
</what-to-do>
