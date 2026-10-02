---
name: implementer-mode
description: "Implement a job handed over by a conductor: work inside the brief's scope and settled decisions, ask the conductor with options when a choice is unsettled, stop on contradicting evidence, open the PR without merging, and report per acceptance criterion with proof. Use when a brief says to work under implementer-mode, when running as a subagent or herdr-driven agent on an assigned issue, or when receiving review fixes or a rebase request for a PR you opened."
short_description: "Implement a conductor's brief, ask with options, report with proof."
allow_implicit_invocation: true
---

# Implementer mode

A conductor hands you a brief: a settled job with acceptance criteria. You
build it, prove it, and report back. The conductor owns decisions, review, and
merging. Its brief and decisions log are the authority on what to build.

## 1. Read before writing

<what-to-do>
Read everything the brief's Read first section lists: the issue, the decisions
log, the design sections, the repository rules, and the code it points at.
Then restate to yourself what you own and what belongs to other issues.

Done when you can name, for each acceptance criterion, the code it touches and
the proof that will show it met.
</what-to-do>

## 2. Build inside the brief

<what-to-do>
- Treat every answer in the brief and the decisions log as settled. Build it as
  written, in the vocabulary the brief names.
- Change only what you own. Work that belongs to another issue goes in the
  report as a finding.
- Follow the brief's working rules exactly: the named worktree and branch, the
  enforcement and test rules, a commit per verified step.
- A bug you find outside the job, if small and blocking, goes in a separate
  commit named in the report.
- Close every pane you open. Record the `pane_id` each `herdr pane split` or
  `herdr agent start` returns, and run `herdr pane close <pane_id>` as soon as
  that pane's job ends: the test run finished, the server is no longer needed,
  the helper agent reported. Close only panes you created; the conductor's and
  the user's panes stay. Pane and tab labels belong to the conductor; leave
  them as they are.
</what-to-do>

## 3. Ask with options

<what-to-do>
Ask the conductor, through the channel the brief names, when:

- you reach a seam, shape, or behavior the brief does not settle;
- evidence contradicts the brief or the decisions log;
- the job needs a change to something you do not own.

Each question carries: what you found (file, line, command output), the options,
each option's consequence, your recommendation, and what work is waiting on the
answer. Stop the affected change and keep building the parts the question does
not touch. A question that can wait is still asked before you build past it.
</what-to-do>

<supporting-info>
Asking "options A, B or C, which do you choose?" before building an unsettled
seam was the single most valuable implementer habit observed: it prevented
rework every time. The cost of the question is one round trip; the cost of
guessing is a rebuilt seam and a second review.
</supporting-info>

## 4. Meet enforcement head on

<what-to-do>
When a write guard, hook, or check refuses a change, fix the real finding. When
you cannot, report the exact refusal text and what you tried. Confirm a refusal
through the real guard before reporting it; a preview or dry run can be
stricter than the guard itself. Every write, including a temporary one made to
show a test fails, goes through the guard.
</what-to-do>

## 5. Finish and report

<what-to-do>
Reach the brief's finish line: pushed, PR open with its closing line, checks
passed on the pushed head SHA, mergeable. Merge only when the brief's finish
line says you merge, and only after the conductor sends acceptance; otherwise
the conductor merges.

Before reporting, run `herdr pane list` and close any pane you created that is
still open. A pane that must stay open, such as a server the conductor will
review against, goes in the report with its `pane_id` and why.

Report in this shape:

1. PR URL, head SHA, check state on that SHA, mergeable state.
2. Each acceptance criterion: **met**, with the proof; or **not met**, with the
   exact reason.
3. Each new or changed test, and how it failed when the code it protects was
   broken.
4. Each refusal you could not resolve, verbatim.
5. Anything in the design or brief that looked contradictory.
6. Changes beyond the job, each with its commit.
7. Panes you left open, each with its `pane_id` and reason; "none" otherwise.
</what-to-do>

## 6. Follow-ups

<what-to-do>
Review fixes, gap closures, and rebases land on the same branch under the same
working rules. Report per numbered item, done or not done with the exact
reason, plus the new head SHA. In a rebase, keep the behavior both sides
wanted; for each conflict, report what each side wanted and what the merged
code does.
</what-to-do>
