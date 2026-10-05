# checkpickerupper-skills

## 1.0.0

### Major Changes

- [`8fc56bc`](https://github.com/CheckPickerUpper/skills/commit/8fc56bcdaa7b2550f436cefe93b50f6b9bf8bb61) Thanks [@CheckPickerUpper](https://github.com/CheckPickerUpper)! - Publish the **Engineering** skills, for code, architecture, APIs and design decisions:

  - **`antimatter-code-quality-review`**: a deep pre-merge review of a commit, PR, branch or diff covering correctness, naming, types, boundaries, duplication and cost. It also flags a change that adds a second way to do something the codebase already does. Every finding carries evidence and a concrete before-and-after, and must survive an attempt to refute it.
  - **`antimatter-codebase-structure-review`**: a structural audit of a change, a directory or a whole codebase covering hierarchy, naming, ownership, dependency boundaries and readiness to grow, with a current-to-proposed change for every finding.
  - **`pizza1`**: justify by correctness, never by convention. It loads when a decision is defended by "it's what the codebase does", ergonomics, churn, compatibility or scope, and re-derives the call from correctness.
  - **`readonly`** (user-invoked): append `/readonly` to a question or another skill to get an answer proved from read-only evidence, with no edits, issues or remote changes.
  - **`zen-of-checkpickerupper`**: twenty-one lines for judging designs, fixes, abstractions, types, structure and questions, each traced to the skill it comes from.

- [`8fc56bc`](https://github.com/CheckPickerUpper/skills/commit/8fc56bcdaa7b2550f436cefe93b50f6b9bf8bb61) Thanks [@CheckPickerUpper](https://github.com/CheckPickerUpper)! - Publish the **Productivity** skills, for planning and handing off work:

  - **`compose-goal`** (user-invoked): compose or retrieve a gist-backed agent goal from a task or GitHub issues. Each goal has a human outcome, live issue references, proof of real behavior and an explicit hard-blocker contract.
  - **`dependency-trace`**: close the dependency graph behind a feature and derive the order to build it, from foundations up.
  - **`grill-with-docs-requiem`** (user-invoked): a design interview that asks in useful batches and records the settled domain language and ADRs as it goes.
  - **`to-issues-clearly`**: turn a plan, bug, audit or PRD into GitHub issues a stranger can act on. Each issue has an Outcome and a Done when, labels by kind and bug priority, real sub-issue, blocked-by and duplicate links, and a milestone when one fits.

- [`8fc56bc`](https://github.com/CheckPickerUpper/skills/commit/8fc56bcdaa7b2550f436cefe93b50f6b9bf8bb61) Thanks [@CheckPickerUpper](https://github.com/CheckPickerUpper)! - Install the collection with `npx skills@latest add CheckPickerUpper/skills` (add `--all` to skip the prompts), or try one skill without installing it with `npx skills@latest use CheckPickerUpper/skills@<skill>`. The **`checkpickerupper-skills`** Claude Code plugin (`.claude-plugin/plugin.json`) registers every published skill, and its `version` now tracks these releases.

  A skill can limit which agents discover it with a `clients` allow-list in its `SKILL.md` front matter, for example `clients: [claude, codex]`. The registered clients are `claude`, `codex`, `gemini`, `antigravity`, `antigravity-cli` and `pi`, listed in `scripts/agent-targets.json`. Leaving out `clients` makes a skill universal. For local development, `scripts/list-skills.sh --client <client>` lists a client's skills, and `scripts/link-skills.sh --client <client>` symlinks them into that client's skill directory.
