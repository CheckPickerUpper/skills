# checkpickerupper-skills

## 1.0.0

### Major Changes

- [`2efa3c0`](https://github.com/CheckPickerUpper/skills/commit/2efa3c0e31668407db006fa829cf13221e9ecdbf) Thanks [@CheckPickerUpper](https://github.com/CheckPickerUpper)! - Ship **`pizza1`** in the **Engineering** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

  `pizza1` (model-invoked) justifies by correctness, never by convention. If a codebase named every variable `pizza1`, `pizza2`, `pizza3`, that would not make those names good. It loads the moment a design, fix, API or name is defended by "it's what the codebase already does", "the established pattern", "the canonical lane does it", ergonomics, churn, compatibility or scope:

  - Those justifications are banned from the next response. Prevalence and transition size are not evidence.
  - The call is re-derived from correctness, naming the bug the alternative would cause.
  - It stays confident in the correct call even when the codebase already happens to do it.

- [`b0112b6`](https://github.com/CheckPickerUpper/skills/commit/b0112b652b588a1523ae7c5933480f859ad51526) Thanks [@CheckPickerUpper](https://github.com/CheckPickerUpper)! - Ship **`antimatter-code-quality-review`** in the **Engineering** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

  `antimatter-code-quality-review` (model-invoked) is a deep pre-merge review of a commit, PR, branch or diff. It audits correctness, intent, naming, cohesion, types, boundaries, control flow, duplication, cost and allocation, and it checks predictability: does this change add a second way to do something the codebase already does? Every finding needs evidence, a concrete before-and-after and proof that behavior is preserved, and it is reported only if it survives an adversarial attempt to refute it. It draws from Cursor's Thermo-Nuclear Code Quality Review.

- [#7](https://github.com/CheckPickerUpper/skills/pull/7) [`8683b9c`](https://github.com/CheckPickerUpper/skills/commit/8683b9c44c181c4021eddf332db8effc556d9e19) Thanks [@CheckPickerUpper](https://github.com/CheckPickerUpper)! - Ship **`antimatter-codebase-structure-review`** in the **Engineering** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

  `antimatter-codebase-structure-review` (model-invoked) is the structural sibling of the code-quality review. Point it at a commit, PR, branch, directory, module or a whole codebase and it audits hierarchy, nesting, naming, ownership, dependency boundaries and readiness to grow. Use it when a change may distort the repository's shape or before reorganizing ahead of expansion. Each finding names a concrete current-to-proposed change and must survive the same refutation pass.

- [`10304e8`](https://github.com/CheckPickerUpper/skills/commit/10304e898356a57d1a8fe992e55d29340a135d5d) Thanks [@CheckPickerUpper](https://github.com/CheckPickerUpper)! - Ship **`readonly`** in the **Engineering** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

  `readonly` (user-invoked) is a modifier: append `/readonly` to a question or to another skill and the agent proves the answer instead of guessing it. It freezes the working tree state, traces the question to the code that owns it, and treats every other instruction as diagnostic only, so nothing is edited, filed, committed or pushed. "Likely" and "probably" are not allowed for anything the codebase can answer; the result is proved, not found, or unknown after checking.

- [`7b90480`](https://github.com/CheckPickerUpper/skills/commit/7b9048001b3cdcbf3f2bee9b5b453ddb2b553201) Thanks [@CheckPickerUpper](https://github.com/CheckPickerUpper)! - Ship **`zen-of-checkpickerupper`** in the **Engineering** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

  `zen-of-checkpickerupper` (model-invoked) is twenty-one lines for judging designs, fixes, abstractions, types, structure and questions, starting with "Unrepresentable is better than validated." Each line is expanded and traced to the skill it comes from, so the agent reads the line, then its expansion, and opens the source skill only when that line decides the case.

- [#5](https://github.com/CheckPickerUpper/skills/pull/5) [`d83de68`](https://github.com/CheckPickerUpper/skills/commit/d83de6884ee5076ec1a9ed207f0c572c368c71a5) Thanks [@CheckPickerUpper](https://github.com/CheckPickerUpper)! - Ship **`compose-goal`** in the **Productivity** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

  `compose-goal` (user-invoked) turns a task or a set of GitHub issues into one executable goal for another agent, published as a gist, or pulls an existing goal and runs it. Every goal states a human outcome, references live issues, demands proof of real behavior, and spells out what counts as a hard blocker. Material ambiguity is settled with the user before anything is published.

- [`5b923bc`](https://github.com/CheckPickerUpper/skills/commit/5b923bc56ab1b527b0fd8789b5cfe6bab55a7454) Thanks [@CheckPickerUpper](https://github.com/CheckPickerUpper)! - Ship **`dependency-trace`** in the **Productivity** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

  `dependency-trace` (model-invoked) asks what must exist rather than what can be built first. It loads when you ask for dependency order, foundations, what a feature uses or what its dependencies use. It clarifies scope, closes the full recursive capability graph, then derives the order to build it from the lowest foundation up.

- [`ef67d3b`](https://github.com/CheckPickerUpper/skills/commit/ef67d3b250d71b55cde81a827e91d769407b6550) Thanks [@CheckPickerUpper](https://github.com/CheckPickerUpper)! - Ship **`grill-with-docs-requiem`** in the **Productivity** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

  `grill-with-docs-requiem` (user-invoked) is a design interview that presses hard enough to expose the real decisions without making you answer what an expert could infer. It leads with "I lean toward X because Y", asks independent questions together in one batch, and records settled domain language in `CONTEXT.md` and decisions as ADRs as the conversation goes.

- [`22af453`](https://github.com/CheckPickerUpper/skills/commit/22af45370553436d64921350fd410795ffb42dde) Thanks [@CheckPickerUpper](https://github.com/CheckPickerUpper)! - Ship **`to-issues-clearly`** in the **Productivity** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

  `to-issues-clearly` (model-invoked) turns a plan, bug, audit or PRD into GitHub issues whose titles and bodies a stranger can act on:

  - Each issue is written in its verifier's language as an Outcome plus Done when; an unresolved decision becomes a plain-language Question, Why, Questions, Done when issue instead.
  - Issue sets are sized into independent slices, labelled by kind, and bugs carry a priority.
  - Relationships use real sub-issue, blocked-by and duplicate links rather than prose, and a milestone is offered when the issues serve one deliverable.

- [`8fc56bc`](https://github.com/CheckPickerUpper/skills/commit/8fc56bcdaa7b2550f436cefe93b50f6b9bf8bb61) Thanks [@CheckPickerUpper](https://github.com/CheckPickerUpper)! - Version the collection. `.claude-plugin/plugin.json` now carries a `version` that tracks these releases, and each release is listed here and on the GitHub Releases page.

  Install everything with `npx skills@latest add CheckPickerUpper/skills` (add `--all` to skip the prompts), or try one skill without installing it with `npx skills@latest use CheckPickerUpper/skills@<skill>`.

  A skill can limit which agents discover it with a `clients` allow-list in its `SKILL.md` front matter, for example `clients: [claude, codex]`. The registered clients are `claude`, `codex`, `gemini`, `antigravity`, `antigravity-cli` and `pi`, listed in `scripts/agent-targets.json`; leaving `clients` out makes a skill universal.
