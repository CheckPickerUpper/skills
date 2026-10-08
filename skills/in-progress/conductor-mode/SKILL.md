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
Your first action, before step 1, is reading your settings. Run this from
the effort's repository; it needs no path lookup:

~~~sh
for f in "${XDG_CONFIG_HOME:-$HOME/.config}/checkpickerupper/conductor-mode.toml" \
         "$(git rev-parse --show-toplevel)/.checkpickerupper/conductor-mode.toml"; do
  echo "== $f"; cat "$f" 2>/dev/null || echo "(not set)"; done
~~~

The first file is global and the second is this repository's; a key in the
second overrides the first. A project `usage.<kind>` table replaces the global
table for that kind whole; its keys never merge across files.

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
- **`usage`:** one table per agent kind (`codex`, `claude`, `pi`), with a
  required `mode`. Read its live state with `conductor_config.py usage --kind K`:
  - `ignore`: usage is never read; the effort runs until finished.
  - `finish-in-flight`: at `at_percent`, assign nothing new; in-flight issues finish fully, through PR merge.
  - `stop-at-commit`: at `at_percent`, implementers stop at their next verified commit, push and report.
  - `finish-in-flight-then-stop`: wind down at `wind_down_at_percent`, then stop at `stop_at_percent`; the first must be lower.
  Percentages are ints in 1..100. Each mode allows only its named thresholds.
  Pi allows only `ignore` until it has a usage reader.
- **`credits.codex`:** whether Codex may spend account credits to finish in-flight
  work. Save it as `codex = true|false` in a global `[credits]` table; project
  files reject `[credits]`. Ask for it only when Codex uses `finish-in-flight`
  and the global choice is missing. Other modes leave it unused. Credit
  continuation requires usable credits and no reached spend control.

**When `max_implementers`, `merge` or `review_skills` is in neither file, ask
the user now**, before any other work, with `AskUserQuestion` where the client
has it. Ask only for the missing settings, plus where to save. Ask for a kind's
usage only for the kind chosen in step 3:

| Question | Options |
|---|---|
| How many implementers should run at once under one conductor, given this machine's memory and build load? | 1, 2, 3, 4 |
| Who merges an implementer's PR? | The conductor, after its review; the implementer, once the conductor sends acceptance |
| Which skills must review every PR before it is accepted or merged? | The review skills installed in this client, found by their names and descriptions, plus "None" (multi-select) |
| When an agent kind's usage fills, what should happen? | `ignore`; `finish-in-flight` with `at_percent`; `stop-at-commit` with `at_percent`; `finish-in-flight-then-stop` with `wind_down_at_percent` and `stop_at_percent`; Pi allows only `ignore`; for Codex `finish-in-flight`, also choose global `[credits].codex = true|false` |
| Save for every project or only this repository? | Every project (global); this repository only (committed project file) |

Save the answers with `scripts/conductor_config.py`, which sits beside this
SKILL.md (Claude Code prints that folder as the skill's base directory when the
skill loads). It validates the values and creates the folder and its README:

~~~sh
python3 <folder of this SKILL.md>/scripts/conductor_config.py write --scope global|project --max-implementers N --merge conductor|implementer --review-skills name,name
~~~

Save that kind's policy with `write --usage-kind K --usage-mode M`, adding
`--at-percent N` or `--wind-down-at-percent N --stop-at-percent N` as its mode
requires. Use the same `--scope` and `--project-dir` options as for the other
settings. Save the separate account choice with
`write --scope global --codex-spend-credits true|false`; usage tables contain
policy only and reject `spend_credits`.

A project file is a change to the repository; land it like any other change.
The channel and the agent kind are not settings: they depend on what the user
can use at the time, so step 3 asks for them each effort.
</what-to-do>

## Check in

<what-to-do>
The board, not the conversation, says what to do next. Run this from the
effort's checkout, naming the effort's parent issue or milestone:

~~~sh
python3 <folder of this SKILL.md>/scripts/conductor_board.py check-in --repo OWNER/REPO --parent N   # or --milestone "TITLE"
~~~

It reads issues, blocked-by edges and their reason lines, PRs, and the herdr
agents in the checkout's worktrees fresh on every run, prints one line per
thing that needs action with the rule for each kind, and exits 1 while
anything does (0 when nothing does, 2 when a read failed; `--json` prints the
same findings for a loop).

Run it at the start of the effort, after every implementer report, after every
merge, and on a loop for the whole effort. In Claude Code the loop is `/loop`
without an interval, whose body is "run check-in and act on every line"; in
other clients, re-run it on a timer. Each pass re-reads the board instead of
trusting the conversation.

Act on every line before doing anything else:

- `ready`: start it, up to `max_implementers` running at once (step 3).
- `stale-blocker`: remove the edge and its reason line, then start the issue.
- `parent-blocker`: move the edge down to the sub-issue that truly needs the
  blocker, with its reason line there.
- `missing-reason` and `orphan-reason`: ask the issue's author to record the
  reason line or drop the edge; record it yourself when you set the edge.
- `review`: review the PR (step 7) and record the result as a PR review on its
  head commit.
- `idle`: prompt the implementer with its next step, or release it (step 7).
- `unmapped`: put the issue number in the worktree's branch, or release the
  agent and remove the worktree when its work is done.

Every check-in report says what is running and what was just started. Never
forecast what will not finish.
</what-to-do>

## 1. Settle the job

<what-to-do>
- Before assigning an issue, check for an open PR that closes it, a worktree
  named for it, or a Codex rollout written in the last few minutes whose `cwd`
  is that worktree. When any exists, start no implementer: review that work and
  send findings through its channel.
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
- An issue is blocked by X only when doing it now would duplicate or conflict
  with work in X that must land first: it cannot start at all, or cannot meet
  one of its acceptance criteria, until X lands. Merge order, rebase-time
  checks (such as taking the next free migration number at merge), "cleaner
  after X", "extra work if done now", and anything already merged or closed
  are never blockers. When only one piece of an issue depends on X, the edge
  goes on that piece's own issue, never on the lane or parent above it.
- Whenever you add a native blocked-by edge, write its reason line in the
  blocked issue's body, one per blocking issue, under a `## Blocked by`
  heading:

  ~~~markdown
  ## Blocked by
  - #1212 Idempotency-key binding: cannot pass "a retried charge with the same key is rejected" until it lands, because keys are not bound to charges yet.
  ~~~

  The line starts with `- #N`, names an issue that is a blocked-by edge, and
  says what this issue `cannot` start or meet until it lands, and why. On an
  issue with sub-issues, the reason says "cannot start until it lands";
  anything narrower belongs on the sub-issue.
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
Ask the user, once per effort, whether implementers run as native subagents,
agents driven through herdr, or existing Codex Desktop threads, and for herdr,
which agent kind (Codex, Claude or Pi). Use the answers for the whole effort. When
the effort already has implementers running, their channel and kind are the
answer; ask only when no implementer exists yet.
For the chosen kind, run `conductor_config.py show --kind <kind>` and ask for
the missing settings, using the questions above. Before each start, run
`conductor_config.py usage --kind <kind>`; start nothing whose state
is `wind-down`, `stop`, `exhausted` or `unknown`.
Never run more implementers at once than `max_implementers`, and never fewer
while independent issues are waiting and that kind's usage state is `normal`.

- **Native subagents:** use the conductor's own agent kind; dispatch in the
  background on the strongest model the client exposes. Continue an implementer
  by messaging the same agent, which keeps its context; start a fresh one only
  for a new issue.
- **herdr:** use the chosen agent kind. Follow `herdr --skill` for command
  syntax; it requires `HERDR_ENV=1`. Address every pane by its `pane_id`: prompt with
  `herdr agent prompt <pane_id> "<text>"`, read with `herdr pane read <pane_id>`,
  and put your own `pane_id` (`$HERDR_PANE_ID`) in the brief so replies come
  back as `herdr agent prompt <conductor pane_id> "<implementer>: ..."`. Record
  each implementer's `pane_id` and whether you started it or the user handed it
  to you.

  **Give each implementer its own worktree workspace.** One command creates the
  issue's git worktree and a herdr workspace linked to the repository, with one
  pane whose working directory is that worktree. Then start the agent in it:

  ~~~sh
  NEW=$(herdr worktree create --cwd <checkout> --branch <branch> --base origin/<base> \
          --path <worktree path> --label "<repo> <topic>" --no-focus)
  P=$(jq -r .result.root_pane.pane_id <<<"$NEW"); WS=$(jq -r .result.workspace.workspace_id <<<"$NEW")
  herdr agent start <repo>-<topic> --kind <kind> --pane "$P" --timeout 120000
  ~~~

  Name the repository with `--cwd` alone: `--cwd` and `--workspace` together
  print usage and create nothing. The worktree path and branch follow the
  brief's worktree convention. Record `$P` and `$WS`; step 7 removes the
  workspace by its id. Add `--trust-repository` only when herdr refuses the
  repository as untrusted and the user confirms it.

  The agent name follows the label in lowercase, such as `nro-input-buffering`;
  it must match `[a-z][a-z0-9_-]{0,31}` and be unique among live agents. A
  Codex start can outlast herdr's 30-second default, so pass the timeout above.
  Send the brief only after `agent start` returns ready and `herdr pane read`
  shows the agent's input box rather than a shell prompt: `agent start -- resume`
  reports ready even when the resume failed.

  **Label what you own** with the repository name plus what it does, so the
  user can read the sidebar at a glance. Your own pane carries your standing
  area: `herdr pane rename "$HERDR_PANE_ID" "<repo> <area>"`, such as
  `NRO prediction`. Each implementer workspace carries its topic through
  `--label`, such as `NRO input buffering`. Leave issue numbers out of every
  label: a context can be cleared and reused for other issues, and a numbered
  label goes stale. Only the conductor labels panes and workspaces.

  **Leave every pane that runs an agent where it is.** `herdr pane move`
  reports success and kills the Codex agent inside
  ([herdrdev/herdr#4864](https://github.com/herdrdev/herdr/issues/4864)), so an
  implementer is addressed in place by its `pane_id`, wherever it runs.

  **A pane the user hands you** is chosen by its `cwd` and `terminal_title`;
  the `agent_session` id can name another repository's thread, so it never
  selects a pane. Send only to panes whose `cwd` is this effort's repository or
  one of its worktrees.

  **When an implementer's session dies**, resume the same thread in its
  worktree: find its thread id by searching
  `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` for text from its brief. When
  its pane is back at a shell prompt, reuse it; when its workspace is gone, open
  the worktree again with
  `herdr worktree open --cwd <checkout> --path <worktree path> --label "<repo> <topic>" --no-focus`
  and take `.result.root_pane.pane_id`. Start
  `herdr agent start <name> --kind codex --pane <pane_id> --timeout 120000 -- resume <thread id>`
  (for another kind, use that agent's own resume argument). Once it returns
  ready and `herdr pane read` shows its input box, re-send your last instruction:
  a resumed thread does not receive a prompt sent before it was ready.

- **Codex Desktop:** the agent kind is `codex`. Used for implementers the user
  already runs in the app; you cannot start one. Reach them as the shared rules'
  "Codex Desktop threads" section describes.

The issue tracker is the durable record in every channel: issues are the work
units, PRs the hand-back, and the decisions log the shared memory.
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

## Usage state changes

<what-to-do>
Re-read `conductor_config.py usage --kind <kind>` whenever an implementer
reports and while watching it through rollout or pane checks:

- `wind-down`: let in-flight issues finish fully, through PR merge; queue the rest.
- `stop` or `exhausted`: tell each implementer of that kind to stop at its next
  verified commit, push and report state. Record that state, and resume once
  usage returns to `normal`.
- `unknown`: assign nothing new until the reading is available. If it persists,
  ask the user whether to proceed.

A thread stopped by its limit may resume by itself once usage returns; check its
rollout before replacing it.
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
4. Confirm the PR's checks passed on the current head SHA, that it is
   mergeable, and that `baseRefName` is the base the brief named
   (`gh pr view N --json state,mergeable,mergeStateStatus,headRefOid,baseRefName,statusCheckRollup`).
5. Land it as its own step. With `merge = "conductor"`, merge it yourself.
   With `merge = "implementer"`, send the implementer acceptance and let it
   merge. Either way, run branch and worktree cleanup only after `state` reads
   `MERGED`.
6. Release the implementer, run check-in, then start its `ready` issues only if
   that kind's usage state is `normal`. When its PR reads `MERGED` and no follow-up is
   pending, or its job was dropped or reassigned, remove a worktree workspace
   you created with `herdr worktree remove --workspace <workspace_id>`, which
   deletes the checkout and closes the workspace and its panes, then delete the
   local branch with `git branch -D <branch>`, which herdr leaves behind. A
   dropped job's branch with unpushed commits is pushed first. A pane the user
   handed you stays open; tell the user it is free. Before the final report,
   run `herdr worktree list --cwd <checkout>` and remove every implementer
   worktree you created that is still open.

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
questions still with the user, the implementer worktrees removed and any left
open with the reason, and any concrete blocker with the external change it needs.
