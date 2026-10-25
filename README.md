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

| Skill | The problem it fixes | Example |
|---|---|---|
| [antimatter-code-quality-review](./skills/engineering/antimatter-code-quality-review/SKILL.md) | Reviews pad the list with style nitpicks and inflated severities, and miss a change that adds a second way to do something the code already does. Every finding here must survive an attempt to disprove it and come with a before-and-after. | `/antimatter-code-quality-review the staged changes` |
| [antimatter-codebase-structure-review](./skills/engineering/antimatter-codebase-structure-review/SKILL.md) | Folders and modules drift into a shape nobody chose, and it is only noticed once a reorganization is expensive. | `/antimatter-codebase-structure-review src/billing` |
| [explain-diff](./skills/engineering/explain-diff/SKILL.md) | You are reviewing or have merged a change you do not really understand. It writes a page with a walkthrough in execution order, what could break and a quiz. Based on [Geoffrey Litt's explain-diff gist](https://gist.github.com/geoffreylitt/a29df1b5f9865506e8952488eac3d524). | `/explain-diff HEAD~3..HEAD` |
| [facts-as-data](./skills/engineering/facts-as-data/SKILL.md) | The same list of names is copied across files, so a case missing from one copy breaks one check silently. It moves the list into one table with a check that fails on a missing case. | `/facts-as-data sweep src/rules` |
| [pizza1](./skills/engineering/pizza1/SKILL.md) | An agent defends a choice with "it's what the codebase does" or "smallest fix" instead of whether it is correct. | `/pizza1 why keep status as a string?` |
| [readonly](./skills/engineering/readonly/SKILL.md) | You ask a question and the agent starts changing code, or answers with "probably". It answers from evidence and changes nothing. | `why does login retry twice? /readonly` |
| [test-hygiene](./skills/engineering/test-hygiene/SKILL.md) | Tests pass when nothing was checked, or check what another test already checks. It breaks each rule on purpose to see which tests fail. | `/test-hygiene review the tests in this diff` |
| [zen-of-checkpickerupper](./skills/engineering/zen-of-checkpickerupper/SKILL.md) | Two designs both look fine and the choice comes down to taste. Twenty-one short principles settle it. | `/zen-of-checkpickerupper store the total or compute it?` |

### Productivity

General workflow tools.

| Skill | The problem it fixes | Example |
|---|---|---|
| [audit-issues](./skills/productivity/audit-issues/SKILL.md) | The tracker has hundreds of issues, many duplicated or already done, and nobody knows which are still real. You approve a before-and-after page before anything changes. | `/audit-issues OWNER/REPO` |
| [check-protection](./skills/productivity/check-protection/SKILL.md) | Agents rerun full suites and checks whose result is already known, and the time goes nowhere. | `/check-protection which checks does this commit need?` |
| [close-issues](./skills/productivity/close-issues/SKILL.md) | Agents close issues that are not done, and later nobody can tell why one closed. A script refuses the close until the proof is written into the issue. | `/close-issues #142 is finished` |
| [compose-goal](./skills/productivity/compose-goal/SKILL.md) | Handing work to another agent loses the outcome, the issue links and how to prove it works. | `/compose-goal hand #142 to another agent` |
| [dependency-trace](./skills/productivity/dependency-trace/SKILL.md) | You build a feature in the wrong order because nobody mapped what it needs to exist first. | `/dependency-trace what does checkout depend on?` |
| [issues-to-outcomes](./skills/productivity/issues-to-outcomes/SKILL.md) | Status reports are lists of issue titles that mean nothing to the person reading them. | `/issues-to-outcomes what landed this week` |
| [make-diagram](./skills/productivity/make-diagram/SKILL.md) | Agent-drawn diagrams overlap, use jargon and leave out how the thing actually works. A script renders the drawing and refuses those defects. | `/make-diagram how a payment goes from cart to receipt` |
| [settle-blockers](./skills/productivity/settle-blockers/SKILL.md) | Issues get marked blocked over a shared file or a merge conflict, so work waits for no reason. | `/settle-blockers OWNER/REPO#88` |
| [to-issues-clearly](./skills/productivity/to-issues-clearly/SKILL.md) | Agent-filed issues have vague titles you must open to understand, and no clear point at which they are done. | `/to-issues-clearly turn this plan into issues` |

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
