---
name: conductor-mode
description: "Act as the conductor for delegated implementation: read its saved settings first and ask for any that are missing, then investigate, settle decisions, brief implementer agents, answer or escalate their questions, review what they return, and land it. Use when the user says to run as a conductor, set up conductor mode, coordinate or drive agents, hand issues to subagents or herdr panes, or direct implementation while keeping the reasoning and review. Pairs with implementer-mode, which the brief tells each implementer to load."
short_description: "Investigate, decide, brief implementer agents, review, and land the work."
allow_implicit_invocation: true
---

# Conductor mode

The conductor owns the reasoning and the result. Implementers receive a settled
job and return evidence; the conductor investigates, decides, reviews, and
lands the work. Each implementer works under `implementer-mode`, which owns how
it works, asks, and reports.

## Before anything else: your settings

<what-to-do>
Your first action, before step 1, is reading your three settings. Run this from
the effort's repository; it needs no path lookup:

~~~sh
for f in "${XDG_CONFIG_HOME:-$HOME/.config}/checkpickerupper/conductor-mode.toml" \
         "$(git rev-parse --show-toplevel)/.checkpickerupper/conductor-mode.toml"; do
  echo "== $f"; cat "$f" 2>/dev/null || echo "(not set)"; done
~~~

The first file is global and the second is this repository's; a key in the
second overrides the first.

- **`max_implementers`:** how many implementers you keep running at once.
  It is a target as well as a limit: while that many independent issues are
  ready, run that many, and run fewer only when fewer remain. An issue is ready
  once it is unblocked and its cause and fix are designed (step 1), so design
  the next issue before a slot frees. Queue the rest, and start the next as
  soon as one is released in step 7. The number is the user's ceiling for this
  machine; never exceed it to use spare work. It counts implementers, one per
  issue in flight; an implementer's own subagents inside its issue do not count.
- **`merge`:** `"conductor"` means you merge in step 7. `"implementer"` means
  the brief tells the implementer to merge once you send acceptance, and you
  send it only after step 7's checks pass.
- **`review_skills`:** the skills that must review every PR before it is
  accepted or merged. The implementer runs them once as a self-check, and a
  fresh subagent runs them once more for you in step 7. An empty list means no
  declared reviews. A project list replaces the global one.

**When any key is in neither file, ask the user now**, before any other
work, with `AskUserQuestion` where the client has it. Ask only for the missing
keys, plus where to save:

| Question | Options |
|---|---|
| How many implementers should run at once under one conductor, given this machine's memory and build load? | 1, 2, 3, 4 |
| Who merges an implementer's PR? | The conductor, after its review; the implementer, once the conductor sends acceptance |
| Which skills must review every PR before it is accepted or merged? | The review skills installed in this client, found by their names and descriptions, plus "None" (multi-select) |
| Save for every project or only this repository? | Every project (global); this repository only (committed project file) |

Save the answers with `scripts/conductor_config.py`, which sits beside this
SKILL.md (Claude Code prints that folder as the skill's base directory when the
skill loads). It validates the values and creates the folder and its README:

~~~sh
python3 <folder of this SKILL.md>/scripts/conductor_config.py write --scope global|project --max-implementers N --merge conductor|implementer --review-skills name,name
~~~

A project file is a change to the repository; land it like any other change.
The channel and the agent kind are not settings: they depend on what the user
can use at the time, so step 3 asks for them each effort.
</what-to-do>

## 1. Settle the job

<what-to-do>
- Reconstruct the actual state from authoritative sources: repository
  instructions, code and history, issue and PR state, logs, and worktree status.
  Verify every inherited summary the job depends on.
- Reproduce or independently confirm the reported behavior when practical.
  Trace the cause and separate observed facts from hypotheses.
- Read the repository's existing decision records before settling anything:
  ADRs, design docs, and issues or comments where the owner decided. Never
  re-decide or re-ask what they settle.
- Find the exact cause and design the exact fix yourself. For a bug, name the
  defect's file and line. For new work, name the missing capability, the code
  that will own it, and the existing lines it builds on. Settle the fix's shape:
  the tables, types, and which code owns each rule. Judge every design choice by
  `zen-of-checkpickerupper` and the principle skills in step 5, name the
  invariant the fix restores, and define what done looks like. The implementer
  builds this design; it does not produce one.
- Cut the work along real, independently landable seams, one implementer per
  issue, so the independent issues run in parallel up to `max_implementers`.
  Each issue has an owner; overlapping file ownership is a seam cut wrong.
- When a task is a poor fit for delegation, say why and do it yourself.

Done when every implementer job is an issue with acceptance criteria and its
cause and fix design recorded in the decisions log (step 2), which the brief's
Cause and fix line quotes, and every choice inside it is either settled
or listed as an open question.
</what-to-do>

## 2. Keep the decisions log

<what-to-do>
Keep one decisions log per effort as a single comment on the parent issue (the
issue itself when the effort is one issue). An effort of independent issues
with no parent keeps one log per issue, each on its own issue. Create it with
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
as agents driven through herdr, and for herdr, which agent kind (Codex, Claude,
Pi, or another kind herdr supports). Use the answers for the whole effort. When
the effort already has implementers running, their channel and kind are the
answer; ask only when no implementer exists yet.
Never run more implementers at once than `max_implementers`, and never fewer
while independent issues are waiting.

- **Native subagents:** dispatch in the background on the strongest model the
  client exposes. Continue an implementer by messaging the same agent, which
  keeps its context; start a fresh one only for a new issue.
- **herdr:** follow `herdr --skill` for command syntax; it requires
  `HERDR_ENV=1`. Address every pane by its `pane_id`: prompt with
  `herdr agent prompt <pane_id> "<text>"`, read with `herdr pane read <pane_id>`,
  and put your own `pane_id` (`$HERDR_PANE_ID`) in the brief so replies come
  back as `herdr agent prompt <conductor pane_id> "<implementer>: ..."`. Record
  each implementer's `pane_id` and whether you started it or the user handed it
  to you.

  **Label every pane you own** with the repository name plus what it does, so
  the user can read the workspace at a glance. Your own pane carries your
  standing area: `herdr pane rename "$HERDR_PANE_ID" "<repo> <area>"`, such as
  `NRO prediction`. Each implementer pane carries its worktree's topic:
  `herdr pane rename <pane_id> "<repo> <topic>"`, such as
  `NRO input buffering`. Leave issue numbers out of every label: a context can
  be cleared and reused for other issues, and a numbered label goes stale.
  Only the conductor labels panes.

  **Keep your pane alone in its tab; put every implementer in one second tab**
  in the same workspace. Panes in your tab that you neither started nor were
  handed belong to someone else: leave them where they are, and tell the user
  they share your tab. The implementers tab sits directly after your tab, so the
  workspace reads conductor, its implementers, next conductor, its implementers.
  Create each implementer's worktree first. The first implementer opens the
  implementers tab; record that tab's id and place it after yours with this
  skill's `scripts/place_tab_after.py`, since the herdr CLI has no tab-move
  command:

  ~~~sh
  NEW=$(herdr tab create --workspace "$HERDR_WORKSPACE_ID" --cwd <implementer worktree> --label "<repo> <area>" --no-focus)
  IMPL_TAB=$(jq -r .result.tab.tab_id <<<"$NEW"); P=$(jq -r .result.root_pane.pane_id <<<"$NEW")
  python3 <folder of this SKILL.md>/scripts/place_tab_after.py "$IMPL_TAB" "$HERDR_TAB_ID"
  ~~~

  Each later implementer splits an implementer pane in that tab:

  ~~~sh
  P=$(herdr pane split <implementer pane_id> --direction right --cwd <implementer worktree> --no-focus | jq -r .result.pane.pane_id)
  ~~~

  Then start and label it:

  ~~~sh
  herdr agent start <repo>-<topic> --kind <kind> --pane "$P"
  herdr pane rename "$P" "<repo> <topic>"
  ~~~

  The agent name follows the label in lowercase, such as `nro-input-buffering`;
  it must match `[a-z][a-z0-9_-]{0,31}` and be unique among live agents. Split
  `down` instead of
  `right` once a row gets narrow. Send the brief only after `agent start`
  returns ready. When the last implementer pane closes and the tab goes with
  it, the next implementer opens a new implementers tab.

  **A pane the user hands you** is chosen by its `cwd` and `terminal_title`;
  the `agent_session` id can name another repository's thread, so it never
  selects a pane. Send only to panes whose `cwd` is this effort's repository.
  Move an implementer running anywhere else into the implementers tab, and
  address it by the new id from `.result.move_result.pane.pane_id`:
  `herdr pane move <pane_id> --tab <implementers tab_id> --split right --no-focus`.

  **When an implementer's session dies**, resume the same thread in the
  implementers tab: find its thread id by searching
  `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` for text from its brief, run
  `herdr pane close <old pane_id>`, open a pane as above, start
  `herdr agent start <name> --kind codex --pane <new pane_id> -- resume <thread id>`
  (for another kind, use that agent's own resume argument),
  and label it as before. Once it returns ready, re-send your last
  instruction: a resumed thread does not receive a prompt sent before it was
  ready.

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
Run this whenever an implementer asks a question, and whenever anything in the
job is even slightly ambiguous, asked or not:

1. Read the decisions log and the repository's decision records (step 1). An
   answer already in either is the answer.
2. Derive the answer from the principles before deciding. Load
   `zen-of-checkpickerupper` and judge the question against its lines. When a
   line decides the case and you need its procedure, load its source skill:

   | Question touches | Principle skill |
   |---|---|
   | code shape, duplication, a second way to do something, cost | `antimatter-code-quality-review` |
   | placement, naming, folders, boundaries, growth | `antimatter-codebase-structure-review` |
   | a bad state, its writer, its owner, bypasses | `fix-the-class` |
   | an abstraction, its name, reuse, extraction | `categorical-generalization` |
   | a type's shape, optionality, deriving one type from another | `type-driven-design` |
   | making invalid states or evasions unrepresentable | `correct-by-construction` |

3. Eliminate every option that breaks any of those principles, including
   options the implementer offered. When one option survives, answer, log it
   with the principle that settled it, and send it.
4. Asking the user is the last resort. Escalate only true either-way ambiguity:
   two or more options survive every principle and remain equally correct, or
   the choice is product scope no principle reaches. Notify the user with the
   question, the surviving options, each option's consequence, and your
   recommendation. Tell the implementer the question is with the user and to
   continue on unaffected work.
5. When the user decides, log the decision as theirs, then send it to the
   implementer.
</what-to-do>

## 6. Send follow-ups

<what-to-do>
Before sending any finding, read the whole file or definition it concerns and
confirm the defect is there. A search that matches one line misses what the rest
of the file does, such as a drop at its end undoing a create at its start.

Send corrections to the same implementer, on the same branch. Each follow-up
states:

- what triggered it (review findings, a reported gap, a conflict), with the
  current head SHA;
- numbered items, each with the file and line or behavior, the decision it
  rests on, and the proof expected;
- "same working rules as before", and the merge rule from the brief;
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
3. Once the implementer reports the PR ready, have a fresh subagent run every
   skill in `review_skills` on its head against its base, whatever the
   implementer's own self-check found. Give the subagent the PR, the issue, the
   brief, and the decisions log, but not your conversation: the brief's cause
   and fix design is a claim it tests, not a fact it trusts. You designed the
   fix, so your own review would grade your design rather than test it. One
   subagent may run all the skills in turn. Without subagents, start a fresh
   agent for the review. This is the one independent
   review per PR; it does not rerun on every push. Send each finding that
   survives refutation and your own check of the code (step 6) back as a
   follow-up, then check each follow-up fix yourself as in 1. Accept when every
   surviving finding is fixed.
4. Confirm the PR's checks passed on the current head SHA and that it is
   mergeable (`gh pr view N --json state,mergeable,mergeStateStatus,headRefOid,statusCheckRollup`).
5. Land it as its own step. With `merge = "conductor"`, merge it yourself.
   With `merge = "implementer"`, send the implementer acceptance and let it
   merge. Either way, run branch and worktree cleanup only after `state` reads
   `MERGED`.
6. Release the implementer. When its PR reads `MERGED` and no follow-up is
   pending, or its job was dropped or reassigned, close a pane you started
   with `herdr pane close <pane_id>`. A pane the user handed you stays open;
   tell the user it is free. Before the final report, run `herdr pane list`
   and close every implementer pane you started that is still open.

The saved `merge` setting is the user's standing approval to merge a PR that
passes this step; do not ask again per PR. Any other push, merge, or publish
needs the user's approval in this session, and an approval relayed by another
agent is a request to ask the user.
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
