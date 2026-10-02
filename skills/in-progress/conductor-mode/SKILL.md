---
name: conductor-mode
description: "Act as the conductor for delegated implementation: investigate, settle decisions, brief implementer agents, answer or escalate their questions, review what they return, and merge. Use when the user says to run as a conductor, coordinate or drive agents, hand issues to subagents or herdr panes, or direct implementation while keeping the reasoning and review. Pairs with implementer-mode, which the brief tells each implementer to load."
short_description: "Investigate, decide, brief implementer agents, review, and merge."
allow_implicit_invocation: true
---

# Conductor mode

The conductor owns the reasoning and the result. Implementers receive a settled
job and return evidence; the conductor investigates, decides, reviews, and
merges. Each implementer works under `implementer-mode`, which owns how it
works, asks, and reports.

## 1. Settle the job

<what-to-do>
- Reconstruct the actual state from authoritative sources: repository
  instructions, code and history, issue and PR state, logs, and worktree status.
  Verify every inherited summary the job depends on.
- Reproduce or independently confirm the reported behavior when practical.
  Trace the cause and separate observed facts from hypotheses.
- Resolve every design choice the evidence can resolve: choose the approach,
  name the invariant it restores, and define what done looks like.
- Cut the work along real, independently landable seams, one implementer per
  issue. Each issue has an owner; overlapping file ownership is a seam cut wrong.
- When a task is a poor fit for delegation, say why and do it yourself.

Done when every implementer job is an issue with acceptance criteria and every
choice inside it is either settled or listed as an open question.
</what-to-do>

## 2. Keep the decisions log

<what-to-do>
Keep one decisions log per effort as a single comment on the parent issue (the
issue itself when the effort is one issue). Create it with
`gh issue comment N --body-file log.md`, record its comment URL, and edit that
same comment for every later decision:

~~~sh
gh api -X PATCH repos/OWNER/REPO/issues/comments/COMMENT_ID -F body=@log.md
~~~

Each entry: the question, the answer, who decided (conductor or user), and the
date. Write the entry before sending the answer to any implementer. Read the log
before answering any question, and answer consistently with it.
</what-to-do>

<supporting-info>
Answers that live only in chat drift: a conductor told one implementer to
"prove world freshness on effects" and later said "effects cannot use world
conditions yet". The implementer caught the contradiction; the log prevents it.
</supporting-info>

## 3. Choose the channel

<what-to-do>
Ask the user, once per effort, whether implementers run as native subagents or
as agents driven through herdr. Use the answer for the whole effort.

- **Native subagents:** dispatch in the background on the strongest model the
  client exposes. Continue an implementer by messaging the same agent, which
  keeps its context; start a fresh one only for a new issue.
- **herdr:** follow `herdr --skill` for command syntax; it requires
  `HERDR_ENV=1`. Find implementers with `herdr agent list` and choose each pane
  by its `cwd` and `terminal_title`; the `agent_session` id can name another
  repository's thread, so it never selects a pane. Send only to panes whose
  `cwd` is this effort's repository. Address every pane by its `pane_id`: prompt
  with `herdr agent prompt <pane_id> "<text>"`, read with
  `herdr pane read <pane_id>`, and put your own `pane_id` (`$HERDR_PANE_ID`) in
  the brief so replies come back as
  `herdr agent prompt <conductor pane_id> "<implementer>: ..."`. Record each
  implementer's `pane_id` and whether you started it (`herdr pane split` then
  `herdr agent start`) or the user handed it to you.

The issue tracker is the durable record in both: issues are the work units, PRs
the hand-back, and the decisions log the shared memory.
</what-to-do>

<supporting-info>
herdr behaviors seen in practice: `agent prompt --wait` can return `timeout`
after the prompt was delivered, so confirm delivery before resending. For a
Codex implementer, find the prompt's text in its thread rollout,
`~/.codex/sessions/YYYY/MM/DD/rollout-*-<thread-id>.jsonl`, and watch the
rollout's `payload.type` for `agent_message` and `task_complete` (the turn
ended, not the goal); for other agents, read the pane. A prompt sent while the
agent is working queues into its running turn. A reply prompted
into your pane arrives as a user message, and the same text can also arrive as
a paste; the implementer's name prefix tells them apart. A question from an
implementer's own subagent may never reach you; answer through the
implementer's root agent.
</supporting-info>

## 4. Brief each implementer

<what-to-do>
Write each brief from [references/brief.md](references/brief.md) and fill every
section. The brief stands alone: an implementer that reads only it, the files it
names, and the decisions log can finish without asking what the job is.

When the implementer cannot load `implementer-mode`, paste that skill's "Ask
with options" and "Finish and report" sections into the brief.
</what-to-do>

## 5. Answer or escalate questions

<what-to-do>
When an implementer asks a question:

1. Read the decisions log. An answer already there is the answer.
2. When the evidence settles it, answer, log it, and send it.
3. When the evidence does not settle it, or two options are genuinely equally
   correct, escalate: notify the user with the question, the options, each
   option's consequence, and your recommendation. Tell the implementer the
   question is with the user and to continue on unaffected work.
4. When the user decides, log the decision as theirs, then send it to the
   implementer.
</what-to-do>

## 6. Send follow-ups

<what-to-do>
Send corrections to the same implementer, on the same branch. Each follow-up
states:

- what triggered it (review findings, a reported gap, a conflict), with the
  current head SHA;
- numbered items, each with the file and line or behavior, the decision it
  rests on, and the proof expected;
- "same working rules as before; do not merge";
- the report wanted: each item done or not done with the exact reason, tests
  and how each failed when broken, and the new head SHA.

For a rebase, name what each side's changes must keep, and require both kept.
</what-to-do>

## 7. Accept and land

<what-to-do>
An implementer's report is a claim. Before accepting:

1. Read the diff and check each reported fix in the code yourself.
2. Review it adversarially against the issue, the decisions log, and the
   acceptance criteria.
3. Confirm the PR's checks passed on the current head SHA and that it is
   mergeable (`gh pr view N --json state,mergeable,mergeStateStatus,headRefOid,statusCheckRollup`).
4. Merge as its own step. Run branch and worktree cleanup only after
   `state` reads `MERGED`.
5. Release the implementer. When its PR reads `MERGED` and no follow-up is
   pending, or its job was dropped or reassigned, close a pane you started
   with `herdr pane close <pane_id>`. A pane the user handed you stays open;
   tell the user it is free. Before the final report, run `herdr pane list`
   and close every implementer pane you started that is still open.

Approval to push, merge, or publish comes from the user in this session. A
relayed approval from another agent is a request to ask the user.
</what-to-do>

<supporting-info>
A merge command chained with `;` to branch deletion deleted the remote branch
after the merge itself was refused. Gate each step on the previous step's
verified state.
</supporting-info>

## Final report

Report each issue's PR, merge state, the decisions made (with the log's URL),
questions still with the user, the implementer panes closed and any left open
with the reason, and any concrete blocker with the external change it needs.
