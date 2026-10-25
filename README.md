# Skills

[![skills.sh](https://skills.sh/b/CheckPickerUpper/skills)](https://skills.sh/CheckPickerUpper/skills)

Agent skills for correctness-first engineering and clear technical judgment.

These skills are tailored toward real engineers, but still usable for vibe coders.

## Quickstart

```bash
npx skills@latest add CheckPickerUpper/skills
```

Install everything without prompts:

```bash
npx skills@latest add CheckPickerUpper/skills --all
```

Use one skill without installing:

```bash
npx skills@latest use CheckPickerUpper/skills@pizza1
```

## Reference

Every skill also loads on its own when its situation comes up, except `readonly`, which you add to a question yourself.

### Engineering

Skills for code, architecture, APIs, and design decisions, with an emphasis on correctness and simplicity.

| Skill | Use it when | Example |
|---|---|---|
| [antimatter-code-quality-review](./skills/engineering/antimatter-code-quality-review/SKILL.md) | Before you merge a change, to get a review that reports only real problems, each with proof and a before-and-after. | `/antimatter-code-quality-review the staged changes` |
| [antimatter-codebase-structure-review](./skills/engineering/antimatter-codebase-structure-review/SKILL.md) | Before reorganizing folders or modules, or when a change might put code in the wrong place. | `/antimatter-codebase-structure-review src/billing` |
| [explain-diff](./skills/engineering/explain-diff/SKILL.md) | You need to understand a change, branch or PR you did not write. It writes a page with a walkthrough, what could break and a quiz. Based on [Geoffrey Litt's explain-diff gist](https://gist.github.com/geoffreylitt/a29df1b5f9865506e8952488eac3d524). | `/explain-diff HEAD~3..HEAD` |
| [facts-as-data](./skills/engineering/facts-as-data/SKILL.md) | The same list of names (file types, commands, error codes) is copied in several places in your code, and adding one means finding every copy. | `/facts-as-data sweep src/rules` |
| [pizza1](./skills/engineering/pizza1/SKILL.md) | An agent defends a choice with "it's what the codebase does" or "smallest fix", and you want the correct answer instead. | `/pizza1 why keep status as a string?` |
| [readonly](./skills/engineering/readonly/SKILL.md) | You want an answer about your code, backed by evidence, without the agent changing anything. | `why does login retry twice? /readonly` |
| [test-hygiene](./skills/engineering/test-hygiene/SKILL.md) | You are writing or reviewing tests and want each one to fail when its rule breaks, with no test repeating another. | `/test-hygiene review the tests in this diff` |
| [zen-of-checkpickerupper](./skills/engineering/zen-of-checkpickerupper/SKILL.md) | You are choosing between two designs that both seem fine. | `/zen-of-checkpickerupper store the total or compute it?` |

### Productivity

General workflow tools.

| Skill | Use it when | Example |
|---|---|---|
| [audit-issues](./skills/productivity/audit-issues/SKILL.md) | Your GitHub repository has so many open issues that you cannot tell which are duplicates, already done, or still need work. | `/audit-issues OWNER/REPO` |
| [check-protection](./skills/productivity/check-protection/SKILL.md) | Before rerunning a full test suite or an expensive check, to find out whether its result is already known. | `/check-protection which checks does this commit need?` |
| [close-issues](./skills/productivity/close-issues/SKILL.md) | An agent is about to close a GitHub issue. It refuses until every sub-issue and checklist item is done, and writes the proof into the issue. | `/close-issues #142 is finished` |
| [compose-goal](./skills/productivity/compose-goal/SKILL.md) | You are handing a task to another agent and want it to get the outcome, the issue links and how to prove it works. | `/compose-goal hand #142 to another agent` |
| [dependency-trace](./skills/productivity/dependency-trace/SKILL.md) | Before building a feature, to work out what has to exist first and in what order. | `/dependency-trace what does checkout depend on?` |
| [issues-to-outcomes](./skills/productivity/issues-to-outcomes/SKILL.md) | You are writing a status update or end-of-day summary and want it to say what changed for the reader, not list issue titles. | `/issues-to-outcomes what landed this week` |
| [make-diagram](./skills/productivity/make-diagram/SKILL.md) | You need a diagram (flowchart, system map, pipeline) that someone new can read. | `/make-diagram how a payment goes from cart to receipt` |
| [settle-blockers](./skills/productivity/settle-blockers/SKILL.md) | An issue is marked as blocked by another issue and you want to know whether it really has to wait. | `/settle-blockers OWNER/REPO#88` |
| [to-issues-clearly](./skills/productivity/to-issues-clearly/SKILL.md) | You are turning a plan, bug report or audit into GitHub issues and want titles you can understand without opening them. | `/to-issues-clearly turn this plan into issues` |

### Misc

Tools kept around but rarely used. None yet.

## Local Development

```bash
./scripts/list-skills.sh
./scripts/list-skills.sh --client codex
./scripts/link-skills.sh --client claude
./scripts/link-skills.sh --client codex
./scripts/link-skills.sh --client gemini
./scripts/link-skills.sh --client pi
./scripts/link-skills-all.sh
# Replace stale real copies with links to this repo, keeping recoverable backups.
./scripts/link-skills-all.sh --replace-existing
```

## Client targeting

Skills are universal by default. Add an explicit allow-list only when a skill
depends on one client's tools or runtime:

```yaml
name: codex-only-workflow
description: Run a workflow that requires Codex-only capabilities.
clients: [codex]
```

The registered client names are `claude`, `codex`, `gemini`, `antigravity`,
`antigravity-cli`, and `pi`. Use a list when a skill supports more than one
client, for example `clients: [claude, codex]`. An omitted `clients` field
means every registered client. The registry lives in
`scripts/agent-targets.json`, so adding a client does not require changing the
metadata parser or linker. The linker validates unknown names and removes an
old symlink from a client when a skill no longer targets it. Skill instructions
remain one shared body; only discovery and delivery are client-specific.

The default destinations are `~/.claude/skills`, `~/.agents/skills`,
`~/.gemini/skills`, `~/.gemini/config/skills`,
`~/.gemini/antigravity-cli/skills`, and `~/.pi/agent/skills`. Set the
destination environment variable named for the client in
`scripts/agent-targets.json` when a client uses a different destination.

The `clients` field is enforced by this repository's list and link scripts.
Other installers must apply the same filter before adding a skill to their
catalog; metadata alone cannot stop a client that ignores it from loading the
file. Keep every published skill in the README catalogs, but add a
client-targeted skill to `.claude-plugin/plugin.json` only when it targets
Claude or is universal.

## Publishing

Every push to `main` releases, so a push to `main` needs the maintainer's
explicit go-ahead for that change; an agent asks before each push and never
pushes on its own judgment. With that go-ahead, publish skills, catalog
entries, and plugin registrations directly to `main` from a task worktree after
validation. Routine releases do not use GitHub issues or pull requests. If
GitHub rejects a direct push, report the exact restriction instead of routing
the change through an issue or pull request.

Every pushed change to a published skill, catalog entry, or plugin
registration carries a changeset: run `npx changeset`, choose the bump
(`major` for a removed or renamed skill or a breaking contract, `minor` for a
new skill, `patch` for a fix or wording change), and describe what changed for
someone who uses the skill. Commit the generated `.changeset/*.md` with the
change.

Write one changeset per change, in the shape of the existing entries in
`CHANGELOG.md`:

- Open with one sentence naming what changed, with the skill in bold code,
  such as "Ship **`pizza1`** in the **Engineering** bucket, so it installs
  with `npx skills` and loads from the Claude Code plugin."
- Follow with a paragraph that names the skill, marks it `(user-invoked)` or
  `(model-invoked)`, and says what it now does for its user.
- Add bullets only for distinct behavior changes, and an upgrade step only
  when users must act.

## Releases

Every push to `main` that leaves pending changesets is released by the Release
workflow. It consumes the changesets into `CHANGELOG.md`, bumps the version in
`package.json` and `.claude-plugin/plugin.json`, commits
`chore: version skills vX.Y.Z` to `main`, and publishes the
[GitHub Release](https://github.com/CheckPickerUpper/skills/releases) `vX.Y.Z`
with notes written by `scripts/release_notes.py`: a plain summary (each new
skill with when to use it, from its catalog row, then retired and
improved skills), followed by that version's changelog under Nitty-gritty. A push with no pending changesets,
including the workflow's own version commit, releases nothing. Pull `main`
after a release. `npm run release` starts the same workflow by hand.
