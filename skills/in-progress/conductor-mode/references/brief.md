# Implementer brief

Fill every section. Write facts and paths the implementer can open; leave
nothing for it to infer.

~~~markdown
Implement OWNER/REPO#N ("<issue title>") and open a PR. <merge line>
Work under the implementer-mode skill.

## You own
- <what this job delivers>
- Not yours: <adjacent work> belongs to #M; do not change it.

## Read first
- `gh issue view N --repo OWNER/REPO`: its Done when is the acceptance list.
  Parent: #P.
- Decisions log: <comment URL>. Every answer there is settled.
- Design: <doc path and the sections that apply>; <ADRs>.
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
- Worktree: `<checkout>-<issue>-<topic>` on branch `<branch>`, already
  created by the conductor and your pane's working directory. (For a
  subagent, give the command instead:
  `git -C <checkout> fetch origin && git -C <checkout> worktree add -b <branch> <checkout>-<issue>-<topic> origin/<base>`.)
  Leave the primary checkout on its branch.
- Enforcement: <write guard, hooks, and how to handle a refusal in this repo>.
- Tests: <test commands>; each new test fails against a plausible wrong
  version before it is committed.
- Commit each verified step; end messages with <attribution line>.

## Finish line
- Push the branch; the pre-push checks pass.
- Open a PR against <base> with `Closes #N` and a body saying what changed and
  how it was verified.
- Wait until the PR's checks pass on the pushed head SHA and it is mergeable.
- <merge line>: with `merge = "conductor"`, "Do not merge it; the conductor
  merges." With `merge = "implementer"`, "Merge it once the conductor sends
  acceptance, then confirm it reads MERGED."

## Asking
Ask <conductor name and channel> with the question, options with their
consequences, and your recommendation. Continue on work the question does not
affect.
~~~
