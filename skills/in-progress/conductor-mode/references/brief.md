# Implementer brief

Fill every section. Write facts and paths the implementer can open; leave
nothing for it to infer. Select the workflow the governing ownership rules
permit, and omit the other workflow's lines from the completed brief.

~~~markdown
Implement OWNER/REPO#N ("<issue title>"). <finish line for the permitted workflow>
Work under the implementer-mode skill.

## You own
- <what this job delivers>
- Not yours: <adjacent work> belongs to #M; do not change it.

## Read first
- `gh issue view N --repo OWNER/REPO`: its Done when is the acceptance list.
  Parent: #P.
- Decisions log: <comment URL>. Every answer there is settled.
- Cause and fix: <quoted from the decisions log: the defect's file and line, or
  for new work the missing capability and its owner; and the settled fix design:
  tables, types, and which code owns each rule>. Build this design; ask before
  departing from it.
- Design docs: <doc path and the sections that apply>; <ADRs>.
- Repo rules: <CLAUDE.md / AGENTS.md / skills to read before writing>.
- Where the code is: <the existing modules, types, and entry points this job
  touches, and what each holds today>.

## Settled for this job
- <decision>: <answer> (log entry <date>)
- Vocabulary: <the domain words to use, and the words they replace>

## Acceptance criteria
<copied from the issue, adjusted for anything settled since filing; each one
names the proof that shows it met>

## Working rules
- Owned repository: work in `<checkout-parent>/<repo>-worktrees/<parent issue
  number>-<what the fix does>`, created or reused through
  `parent-issue-worktree`. This is top-level parent #P's single worktree;
  every sub-issue and helper for #P uses this same path. Different parents use
  different worktrees. Commit and push directly to the development or
  canonical branch, with a detached worktree HEAD. Keep the main checkout out
  of implementation. A subagent receives the same parent worktree path.
- Only where governing ownership and external-contribution rules permit a
  branch and PR workflow: <the repository's worktree convention from its AGENTS.md or
  CLAUDE.md, else `<checkout>-<issue>-<topic>`> on branch `<branch>` from
  `origin/<base>`, already created by the conductor and your pane's working
  directory. (For a subagent, give the command instead:
  `git -C <checkout> fetch origin && git -C <checkout> worktree add -b <branch> <checkout>-<issue>-<topic> origin/<base>`.)
  Leave the primary checkout on its branch. <base> is the repository's
  canonical branch unless the decisions log records another.
- Enforcement: <write guard, hooks, and how to handle a refusal in this repo>.
- Tests: <test commands>; each new test fails against a plausible wrong
  version before it is committed.
- Commit each verified step; end messages with <the trailer the repository
  requires, or "no trailer">.

## Self-check before reporting
- Once the change is complete, run each of these skills once on your diff against
  <base commit SHA recorded before work starts>: <review_skills, or "none declared">. Fix every finding that survives
  a review's refutation and commit each fix. The conductor's independent review
  follows your report.

## Finish line
- Push verified commits to the workflow's target branch; the pre-push checks pass as the repository configures them
  now. Never turn back on a check the owner has turned off: no `git -c` or
  config change that forces a hook on, no re-added CI job, no fuller lane than
  the configured one. If you think a disabled check is needed, ask me with the
  reason and the failure it would catch, and do not run it until answered.
- Owned repository: record proof in issue #N and close it with its finishing
  commit. Keep parent #P's worktree for every remaining sub-issue. Once #P is
  closed and independent review accepts the work, remove its clean landed
  worktree through `parent-issue-worktree`'s `finish`.
- Only in a permitted PR workflow: open a PR against <base> with `Closes #N` and a body saying what changed and
  how it was verified.
- In that PR workflow, wait until the PR's checks pass on the pushed head SHA and it is mergeable.
- In that PR workflow, <merge line>: with `merge = "conductor"`, "Do not merge it; the conductor
  merges." With `merge = "implementer"`, "Merge it once the conductor sends
  acceptance, then confirm it reads MERGED."

## Asking
Build, test, commit and push your own verified work; never ask permission to
commit. Ask <conductor name and channel> only for a product or design decision
you truly cannot make (one line, with your recommendation), another group
touching a file you need (I settle it with that group's root first), or a
release blocker you cannot fix. Continue on work the question does not affect.
Send no status, acknowledgement, plan or receipt messages: your pushed commits
and issue proof (or the permitted PR) are the report. Forward this rule to every subagent you start; they ask
you, never me.
~~~
