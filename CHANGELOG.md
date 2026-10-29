# checkpickerupper-skills

## 2.1.1

### Patch Changes

- [`b0c2ee6`](https://github.com/CheckPickerUpper/skills/commit/b0c2ee65b76dfbf85b4aac9d2abefb1362d2e674) close-issues: a close that leaves its milestone with no open issue now closes the milestone too. GitHub never closes a milestone by itself, so a milestone whose every issue was done stayed open and kept showing as 100% wherever open milestones are listed. `close_issue.py` reads the issue's milestone after every close (completed, duplicate, out-of-date or not planned) and closes it when nothing in it is still open.

## 2.1.0

### Minor Changes

- [`ab284be`](https://github.com/CheckPickerUpper/skills/commit/ab284be083bd9d62636d7f7840a449a31001d2b4) Ship **`correct-by-construction`** in the **Engineering** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

  `correct-by-construction` (model-invoked) makes a whole class of invalid states impossible to write, starting from the type system: it traces the writer of the bad state, strips the incident's names to find the class, moves the rule to the earliest owner that can refuse it, deletes every bypass, and proves the former bad shape fails the type checker. `zen-of-checkpickerupper` already cited it as a source.

- [`7e5906e`](https://github.com/CheckPickerUpper/skills/commit/7e5906e9ebcc4ffa2d4fe18cee59ef71195ee299) Ship **`cut-extraneous-load`** in the **Productivity** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

  `cut-extraneous-load` (model-invoked) changes how an agent writes, never what it does: every sentence serves the reader's question, never the writer's need to show its work. It cuts restated questions, narration, repeated points, phrases that need translating, hedges in place of a lookup and bare numbers, keeps every reason and one checkable pointer per claim, and never cuts a finding to look short.

### Patch Changes

- [`5aeb593`](https://github.com/CheckPickerUpper/skills/commit/5aeb5937d3303d123ec8ce34c0f8b165c5eb6e7e) close-issues: an issue with a reproduction section no longer closes as completed on passing tests alone. `close_issue.py reran` records a rerun of that reproduction under `## Reproduction rerun` and refuses a rerun that runs none of the reproduction's commands. `ready` and `completed` refuse until a recorded rerun shows the bug fixed, so an issue whose tests pass while its reproduction still fails stays open. Suggested by u/MiserableFlatworm337.

## 2.0.1

### Patch Changes

- [`c470154`](https://github.com/CheckPickerUpper/skills/commit/c47015419606d59e9957077b53bebb7f44de03ee) audit-issues keeps a local copy of the repository's issues and fetches only what changed since the last run, so filing a set of issues no longer downloads the whole tracker each time.

- [`a3dfe0c`](https://github.com/CheckPickerUpper/skills/commit/a3dfe0caca14c65f6db1eb62f817ede8565dda39) audit-issues: `audit_issues.py draft` also catches a duplicate written in plain words. It refuses a draft whose title shares rare words with an open issue's title (worth as much as two words no other open title has), lists the three closest titles to read before filing, and its passing message now says exactly what it checked.

## 2.0.0

### Major Changes

- [`3f0ffb6`](https://github.com/CheckPickerUpper/skills/commit/3f0ffb6298ab7c41cf5491f0e49d39c0521c02a5) Remove **`grill-with-docs-requiem`** from the **Productivity** bucket, so it no longer installs with `npx skills` or loads from the Claude Code plugin.

  `grill-with-docs-requiem` (model-invoked) was a design interview that recorded domain language and ADRs as it went. Its owner retired it as unused; the text stays in `skills/deprecated`.

### Minor Changes

- [`771dd49`](https://github.com/CheckPickerUpper/skills/commit/771dd49ef7686121b4eec271f1def4a2454006b3) Ship **`audit-issues`** in the **Productivity** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

  `audit-issues` (model-invoked) loads when a tracker is to be audited, cleaned up, triaged, merged or swept. `scripts/audit_issues.py` has five commands:

  | Command                                                               | What it does                                                                                                                                                                                                                                                                       |
  | --------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | `scan --repo R [--milestone M]`                                       | Lists open work hidden under closed issues (exits 1 while any remains), milestones over 10 top-level issues, groups that look like one cause (error text, one bug in several languages, or two shared file paths or code names), weaker one-signal leads, and workaround premises. |
  | `index --repo R --out FILE`                                           | Writes one line per open issue, the index every batch agent reads in full.                                                                                                                                                                                                         |
  | `draft --repo R --title T --body-file F [--milestone M] [--parent N]` | Checks one issue before it is filed: refuses a likely duplicate cause, a workaround premise, or a milestone pushed past 10 causes until the draft records why it does not apply.                                                                                                   |
  | `plan --repo R --plan P [--verdicts F ...] --page PAGE`               | Checks that every open issue in scope has a complete verdict and writes the short before-and-after page the owner approves, with its approval code.                                                                                                                                |
  | `apply --repo R --plan P [--verdicts F ...] --approved CODE`          | Applies the approved plan: creates new causes, moves slices under them, folds checkbox slices and duplicates in under `(was #N)`, and closes through close-issues, deepest first. Refuses a changed plan; resumes after a failure.                                                 |

  Verdicts are done, duplicate, slice of a cause (checkbox or sub-issue), cause, wrong premise, out of date, still real and unsure, which needs the settling check and why it cannot run. The plan format is in `references/plan-format.md`.

- [`c84d09f`](https://github.com/CheckPickerUpper/skills/commit/c84d09f605746be44a586f1cb22030728a9800a4) Ship **`close-issues`** in the **Productivity** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

  `close-issues` (model-invoked) loads whenever an issue is about to close. It closes issues through `scripts/close_issue.py`, which refuses a close while sub-issues or checklist lines are open and records the reason in the issue body: the proof under `## Proof`, the owner's quoted decision under `## Not planned`, or, for a duplicate, the survivor carrying the details under `(was #N)`. `to-issues-clearly` now says each sub-issue is closed by the commit that finishes it, with `Part of #N` on earlier commits.

- [`90a47a1`](https://github.com/CheckPickerUpper/skills/commit/90a47a1978823f354bab1e71e3a0047edeb80abd) Ship **`explain-diff`** in the **Engineering** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

  `explain-diff` (model-invoked) turns a change, diff, branch or PR into one self-contained page: background, intuition with a worked example, a walkthrough in the order the code runs with `path:line` links, what could break, and a quiz. It is based on Geoffrey Litt's `explain-diff` gist and fixes what that gist's readers reported:

  - The quiz is written as data and a script places the answers, so the right one is not in a predictable spot, and the build refuses a quiz whose correct answers are noticeably the longest.
  - `--quiz chat` replaces multiple choice with free-response questions graded in the conversation.
  - The diff and PR text are treated as data, never instructions.
  - A fixed template carries all CSS and JavaScript, so each run spends its tokens on the explanation; `--md` writes plain Markdown for the lowest cost.

- [`ef337a4`](https://github.com/CheckPickerUpper/skills/commit/ef337a427fb862239b9bf8ef79999fc3777ad78c) Ship **`facts-as-data`** in the **Engineering** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

  `facts-as-data` (model-invoked) moves knowledge buried in logic into one table every reader shares, before a second copy of it exists. It covers four jobs: a census of a codebase, the design of each table, the review of one diff, and a counter-test that keeps code as code when its variation has no real form.

  - `scripts/buried_facts.py <paths>` lists leads (regex alternations of names, `||` chains, literal name lists, runs of branches keyed by a literal) and, with `--record <census.tsv>`, exits non-zero until every lead site has a recorded decision: `table`, `is-table` or `not-data`.

- [`4979604`](https://github.com/CheckPickerUpper/skills/commit/4979604a32d575772c637c88360ee500eb033f48) Ship **`issues-to-outcomes`** in the **Productivity** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

  `issues-to-outcomes` (model-invoked) makes an agent report finished work as what its reader would notice, instead of a list of issue and PR titles. The report opens with how much of the work shows in the product, describes each visible change as the situation before and now, and describes the invisible work as what was stuck or silently wrong and no longer is. References trail the sentence they support.

  - `scripts/check_report.py` reads a draft report and refuses it while any line opens with an issue or pull-request reference, naming each line.

- [`c9baa2d`](https://github.com/CheckPickerUpper/skills/commit/c9baa2da8ee4560fe8958c28727eafbf39b6f754) Ship **`make-diagram`** in the **Productivity** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

  `make-diagram` (model-invoked) makes an agent draw any diagram (a system map, flowchart, pipeline or process map) that a stranger can read. It settles the domain with the owner before drawing and keeps the owner's wording corrections in a words file. The mechanism is drawn as more nodes rather than longer box text, every check is a diamond with labelled yes and no branches, and each source of truth gets its own lane. Arrows carry semantic colours with a legend, and the drawing carries no captions or notes.

  - `scripts/check_diagram.py` renders each diagram in light and dark themes, writes both images for the agent to look at, and refuses text under 15px, overlapping or clipped labels, labels on lines, boxes over three short rows, floating nodes and text, decisions missing a labelled yes or no branch, backward or crossing arrows, arrow colours that break the legend, captions, low contrast, and phrases the owner corrected. Three of its rules are judgment calls (long rows, crossing arrows, arrows that point up or back): the agent can leave one standing by writing the finding and its reason in `<diagram>.accepted.txt`, which the owner can read.

- [`8138ac0`](https://github.com/CheckPickerUpper/skills/commit/8138ac0a869d71dc0d088f44edf82da6d1aedc74) Ship **`settle-blockers`** in the **Productivity** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

  `settle-blockers` (model-invoked) makes an agent decide whether each blocked-by link or claimed blocker between GitHub issues is real before anyone waits on it. Work is blocked only when it cannot be done now, or doing it now means redoing part of it once the blocker lands; a shared file, a merge conflict, a related topic or an existing link never is. Unclear links go to cheap subagents in parallel, each answering the same two questions with file and symbol evidence.

  - `scripts/blockers.py check` lists blocked-by links with no reason line, reason lines with no link, lines with no reason, and blockers that have closed. `keep` and `drop` change a link and its line under `## Blocked by` together and read the issue back.

- [`82515cf`](https://github.com/CheckPickerUpper/skills/commit/82515cf2d8185636d34a91768a2f37873f7db0b9) Ship **`test-hygiene`** in the **Engineering** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

  `test-hygiene` (model-invoked) holds every test to two facts: it fails when its rule breaks, and no other test already fails for that break. Both are proved by breaking the rule on purpose and recording which tests fail. A test that cannot fail is fixed at its cause, usually code that collapses different failures into one answer; a test another test already catches is deleted; and a new test is written only when nothing existing fails for its break.

### Patch Changes

- [`853c229`](https://github.com/CheckPickerUpper/skills/commit/853c229154431925ce756d369dab70a1c56e428d) audit-issues: `audit_issues.py draft --parent N` no longer refuses a sub-issue for sharing its parent's cause; every other open issue that shares the cause is still flagged.

- [`526f12c`](https://github.com/CheckPickerUpper/skills/commit/526f12cadf7e776e47102bacc472357a668ef33d) audit-issues: the final report goes to the user, or to the conducting agent when an agent asked, with no assumption about a particular terminal or pane setup.

- [`d336b2b`](https://github.com/CheckPickerUpper/skills/commit/d336b2bb71b30570202c31bc29299d18a22bba8f) The catalog's second column is now **Use it when**: each skill's row names the situation you are in when you would reach for it, in plain words, instead of the problem it fixes.

- [`b5bec5e`](https://github.com/CheckPickerUpper/skills/commit/b5bec5ee19d4a37baa318ef0d5ac9b02c5eb6e5d) close-issues: `close_issue.py out-of-date --evidence TEXT` closes an issue whose code or release has moved on, recording the evidence under `## Out of date`, without waiting on the owner. `duplicate` now lets a duplicate close when its survivor carries each of its unticked checklist lines.

- [`e24b0fb`](https://github.com/CheckPickerUpper/skills/commit/e24b0fb2ec58aa4a86d385dda09437cbd0421f21) close-issues: `close_issue.py` explains that `CLOSE_ISSUES_SCRIPT` is ignored by plain `gh` and exists only for a `gh` wrapper that refuses hand-typed closes.

- [`87d955e`](https://github.com/CheckPickerUpper/skills/commit/87d955ef658fba4990f471f5f8da9c1025cbde2d) Make **`to-issues-clearly`** keep every issue fact in the issue body, so a settled decision never reads as open.

  `to-issues-clearly` (model-invoked) now records a settled decision by editing the decision issue itself: a `## Decision` section at the top, ticked boxes, a link to the build issue, then closing it. A decision recorded only in a comment left the issue open, and it read as undecided. A replaced issue now gets `Replaced by` in its body instead of a closing comment. Issue bodies link to a fact another issue owns instead of copying it.

- [`762b875`](https://github.com/CheckPickerUpper/skills/commit/762b8756ccd12e2cd7e90b970e3b4c91320ce464) Make **`to-issues-clearly`** file one issue per cause and fix, so the same bug or the same mechanical change no longer becomes dozens of unrelated issues.

  `to-issues-clearly` (model-invoked) used to tell agents to err granular and split whenever parts could land separately, which turned one false refusal seen in three repositories into three issues and one change applied to forty rules into forty issues. It now defines an issue as one cause with one fix: a new sighting of a filed cause is added to that issue's evidence, and the duplicate search looks for the cause (rule, symbol, owner, command) as well as the words. When one cause's fix lands in pieces, the cause is the parent issue and each piece is a GitHub sub-issue closed by exactly one pull request, so one issue, one pull request still holds.

- [`3438acf`](https://github.com/CheckPickerUpper/skills/commit/3438acf8b32d1cfeea8285c9ad352fd3723201c1) **`make-diagram`** now catches what readers objected to in diagrams the checker had passed.

  `make-diagram` (model-invoked) now has the author read every word as a non-technical stranger before the first render, and draws only flows; rulebooks become tables.

  - An arrow means the target waits on the source, so outputs produced independently branch side by side instead of being chained.
  - Lanes hold only the steps that differ. A step both lanes take is drawn once in a shared flow, and the checker refuses a step drawn twice.
  - A box row holds one item, and the checker refuses comma lists; use bullet rows.
  - Every check states its exact condition, every branch what follows, and every end whether it can be retried. The checker refuses an end box that gives only its name.
  - The checker refuses a diagram with no `<stem>.words.txt`, so the cold read of every word happens before the owner sees it.
  - Levels, ranks and other states with move-up and drop rules go in a table. An arrow back to an earlier state is no longer an accepted judgment call.

- [`0d492f5`](https://github.com/CheckPickerUpper/skills/commit/0d492f5b43dcdee1b3dbe52c5b79d62400bb344a) make-diagram: a box may hold a titled checklist (subheadings ending in ":" and one "• " bullet per concrete thing) beyond the three-row limit. A new judgment rule, `vague`, flags a row joining two things with "and" and no number ("jerseys and the court"). A new rule, `example`, refuses a check unless the diamond or its failure box shows a real case as an "e.g." row. The skill also replaces the system's own nouns (markers, queues, verified records) with the real thing a person sees.

- [`dae1685`](https://github.com/CheckPickerUpper/skills/commit/dae16859cfb781489649a28b2f08a60ac250afef) make-diagram: a phrase in the words file now matches whole words only, so banning "round" no longer refuses "background" or "around".

- [`7e559a3`](https://github.com/CheckPickerUpper/skills/commit/7e559a353776b19c4e5452f881f9604795cd67e9) The catalog in `README.md` and each bucket README is now a table per bucket: each skill with the problem it fixes and an example prompt, instead of a restatement of its frontmatter description. It also says that every skill loads on its own when its situation comes up, except `readonly`.

- [`b34890f`](https://github.com/CheckPickerUpper/skills/commit/b34890f708954642de1b7905dc270f393f2716cf) Reconcile stale skill links before installing current sources.

  Moving a skill between source folders while keeping its name now replaces
  the old owned link. Foreign links and real directories remain protected.

- [`8c7da12`](https://github.com/CheckPickerUpper/skills/commit/8c7da12084635dc531a1193c7a226b15de86e623) Remove stale installed links when a skill source is renamed or deleted.

  The local skill linker removes only symlinks it owns whose source no longer
  contains a skill. Foreign links and real directories stay in place.

- [`2451dca`](https://github.com/CheckPickerUpper/skills/commit/2451dca2af8e6e0f84f0c1dc4a30fd34ddcb8fcf) Say when to reach for each published skill, in its own frontmatter.

  Every published skill (**`antimatter-code-quality-review`**, **`antimatter-codebase-structure-review`**, **`explain-diff`**, **`pizza1`**, **`readonly`**, **`zen-of-checkpickerupper`**, **`audit-issues`**, **`close-issues`**, **`compose-goal`**, **`dependency-trace`**, **`make-diagram`**, **`settle-blockers`**, **`to-issues-clearly`**, **`issues-to-outcomes`**; model-invoked unless noted) now carries `metadata.when`, a short plain phrase such as "an issue is about to be closed", and `metadata.situation`, the group a status screen files it under. Skill behaviour is unchanged.

- [`6c8f526`](https://github.com/CheckPickerUpper/skills/commit/6c8f526a0d66a40284cdc7f198876cf055ca4d8d) settle-blockers: the tests use an example repository and invented issue titles.

- [`b9d3fa4`](https://github.com/CheckPickerUpper/skills/commit/b9d3fa46c29787adc2b0ffdd569ceda32e3b2ccd) to-issues-clearly: each issue is checked with `audit_issues.py draft` before it is filed, so a new sighting of a filed cause, a workaround premise or a milestone pushed past 10 causes is caught before it reaches the tracker. The skill also asks for the proper fix instead of a workaround and keeps a milestone to about 10 causes.

- [`cb74e6b`](https://github.com/CheckPickerUpper/skills/commit/cb74e6b887652dec7d004ac15450f1bbf171a936) **`to-issues-clearly`** settles every blocked-by edge with `settle-blockers` before showing the set, and creates each edge with its reason line through `settle-blockers`' `keep` command.

  The user is no longer asked whether each blocking edge is real; the agent decides with the same test `settle-blockers` uses, and the set shows each edge with its reason.

## 1.0.0

### Major Changes

- [`2efa3c0`](https://github.com/CheckPickerUpper/skills/commit/2efa3c0e31668407db006fa829cf13221e9ecdbf) Ship **`pizza1`** in the **Engineering** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

  `pizza1` (model-invoked) justifies by correctness, never by convention. If a codebase named every variable `pizza1`, `pizza2`, `pizza3`, that would not make those names good. It loads the moment a design, fix, API or name is defended by "it's what the codebase already does", "the established pattern", "the canonical lane does it", ergonomics, churn, compatibility or scope:

  - Those justifications are banned from the next response. Prevalence and transition size are not evidence.
  - The call is re-derived from correctness, naming the bug the alternative would cause.
  - It stays confident in the correct call even when the codebase already happens to do it.

- [`b0112b6`](https://github.com/CheckPickerUpper/skills/commit/b0112b652b588a1523ae7c5933480f859ad51526) Ship **`antimatter-code-quality-review`** in the **Engineering** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

  `antimatter-code-quality-review` (model-invoked) is a deep pre-merge review of a commit, PR, branch or diff. It audits correctness, intent, naming, cohesion, types, boundaries, control flow, duplication, cost and allocation, and it checks predictability: does this change add a second way to do something the codebase already does? Every finding needs evidence, a concrete before-and-after and proof that behavior is preserved, and it is reported only if it survives an adversarial attempt to refute it. It draws from Cursor's Thermo-Nuclear Code Quality Review.

- [#7](https://github.com/CheckPickerUpper/skills/pull/7) [`8683b9c`](https://github.com/CheckPickerUpper/skills/commit/8683b9c44c181c4021eddf332db8effc556d9e19) Ship **`antimatter-codebase-structure-review`** in the **Engineering** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

  `antimatter-codebase-structure-review` (model-invoked) is the structural sibling of the code-quality review. Point it at a commit, PR, branch, directory, module or a whole codebase and it audits hierarchy, nesting, naming, ownership, dependency boundaries and readiness to grow. Use it when a change may distort the repository's shape or before reorganizing ahead of expansion. Each finding names a concrete current-to-proposed change and must survive the same refutation pass.

- [`10304e8`](https://github.com/CheckPickerUpper/skills/commit/10304e898356a57d1a8fe992e55d29340a135d5d) Ship **`readonly`** in the **Engineering** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

  `readonly` (user-invoked) is a modifier: append `/readonly` to a question or to another skill and the agent proves the answer instead of guessing it. It freezes the working tree state, traces the question to the code that owns it, and treats every other instruction as diagnostic only, so nothing is edited, filed, committed or pushed. "Likely" and "probably" are not allowed for anything the codebase can answer; the result is proved, not found, or unknown after checking.

- [`7b90480`](https://github.com/CheckPickerUpper/skills/commit/7b9048001b3cdcbf3f2bee9b5b453ddb2b553201) Ship **`zen-of-checkpickerupper`** in the **Engineering** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

  `zen-of-checkpickerupper` (model-invoked) is twenty-one lines for judging designs, fixes, abstractions, types, structure and questions, starting with "Unrepresentable is better than validated." Each line is expanded and traced to the skill it comes from, so the agent reads the line, then its expansion, and opens the source skill only when that line decides the case.

- [#5](https://github.com/CheckPickerUpper/skills/pull/5) [`d83de68`](https://github.com/CheckPickerUpper/skills/commit/d83de6884ee5076ec1a9ed207f0c572c368c71a5) Ship **`compose-goal`** in the **Productivity** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

  `compose-goal` (user-invoked) turns a task or a set of GitHub issues into one executable goal for another agent, published as a gist, or pulls an existing goal and runs it. Every goal states a human outcome, references live issues, demands proof of real behavior, and spells out what counts as a hard blocker. Material ambiguity is settled with the user before anything is published.

- [`5b923bc`](https://github.com/CheckPickerUpper/skills/commit/5b923bc56ab1b527b0fd8789b5cfe6bab55a7454) Ship **`dependency-trace`** in the **Productivity** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

  `dependency-trace` (model-invoked) asks what must exist rather than what can be built first. It loads when you ask for dependency order, foundations, what a feature uses or what its dependencies use. It clarifies scope, closes the full recursive capability graph, then derives the order to build it from the lowest foundation up.

- [`ef67d3b`](https://github.com/CheckPickerUpper/skills/commit/ef67d3b250d71b55cde81a827e91d769407b6550) Ship **`grill-with-docs-requiem`** in the **Productivity** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

  `grill-with-docs-requiem` (user-invoked) is a design interview that presses hard enough to expose the real decisions without making you answer what an expert could infer. It leads with "I lean toward X because Y", asks independent questions together in one batch, and records settled domain language in `CONTEXT.md` and decisions as ADRs as the conversation goes.

- [`22af453`](https://github.com/CheckPickerUpper/skills/commit/22af45370553436d64921350fd410795ffb42dde) Ship **`to-issues-clearly`** in the **Productivity** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

  `to-issues-clearly` (model-invoked) turns a plan, bug, audit or PRD into GitHub issues whose titles and bodies a stranger can act on:

  - Each issue is written in its verifier's language as an Outcome plus Done when; an unresolved decision becomes a plain-language Question, Why, Questions, Done when issue instead.
  - Issue sets are sized into independent slices, labelled by kind, and bugs carry a priority.
  - Relationships use real sub-issue, blocked-by and duplicate links rather than prose, and a milestone is offered when the issues serve one deliverable.

- [`8fc56bc`](https://github.com/CheckPickerUpper/skills/commit/8fc56bcdaa7b2550f436cefe93b50f6b9bf8bb61) Version the collection. `.claude-plugin/plugin.json` now carries a `version` that tracks these releases, and each release is listed here and on the GitHub Releases page.

  Install everything with `npx skills@latest add CheckPickerUpper/skills` (add `--all` to skip the prompts), or try one skill without installing it with `npx skills@latest use CheckPickerUpper/skills@<skill>`.

  A skill can limit which agents discover it with a `clients` allow-list in its `SKILL.md` front matter, for example `clients: [claude, codex]`. The registered clients are `claude`, `codex`, `gemini`, `antigravity`, `antigravity-cli` and `pi`, listed in `scripts/agent-targets.json`; leaving `clients` out makes a skill universal.
