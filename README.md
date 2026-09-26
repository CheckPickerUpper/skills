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

### Engineering

Skills for code, architecture, APIs, and design decisions, with an emphasis on correctness and simplicity.

- **[antimatter-code-quality-review](./skills/engineering/antimatter-code-quality-review/SKILL.md)** — Total annihilation: no finding survives unless it survives refutation. Inspired by Cursor's [Thermo-Nuclear review](https://github.com/cursor/plugins/blob/main/cursor-team-kit/skills/thermo-nuclear-code-quality-review/SKILL.md), [Matt Pocock's skills](https://github.com/mattpocock/skills), and correctness-first design philosophy; pins the diff frame, checks intent and repo standards, and only reports provable findings.
- **[antimatter-codebase-structure-review](./skills/engineering/antimatter-codebase-structure-review/SKILL.md)** — Audits hierarchy, naming, ownership, dependency boundaries, and growth readiness; every finding must survive refutation and specify an evidence-backed change.
- **[pizza1](./skills/engineering/pizza1/SKILL.md)** — Justify by correctness, never by convention. Use when a design is defended by "it's what the codebase does", "the canonical lane does it", ergonomics, churn, transition size, compatibility, legacy paths, or scope.
- **[readonly](./skills/engineering/readonly/SKILL.md)** — Prove, don't guess. A user-invoked modifier for codebase questions and other skills: exhaust read-only evidence, avoid "likely" answers when facts can be checked, and stop before implementation, issues, commits, or remote changes.

### Productivity

General workflow tools.

- **[compose-goal](./skills/productivity/compose-goal/SKILL.md)** — Compose or retrieve a gist-backed agent goal with a human outcome, live issue references, traceable implementation scope, and real behavior proof.
- **[dependency-trace](./skills/productivity/dependency-trace/SKILL.md)** — Derive a correctness dependency graph before implementation. Use when determining foundations, dependency order, or a lowest-to-highest flow for a feature.
- **[grill-with-docs-requiem](./skills/productivity/grill-with-docs-requiem/SKILL.md)** — A design interview that asks useful batches, infers obvious answers, and records settled domain language and ADRs as the conversation progresses. Use when sharpening a plan while maintaining docs.
- **[to-issues-clearly](./skills/productivity/to-issues-clearly/SKILL.md)** — Create GitHub issues whose titles a stranger can act on. Refuses rhetoric, sarcasm, personified code, and type vocabulary dressed as domain language; splits issues by whether anything visibly breaks; errs granular, demands watchable acceptance criteria, and wires real GitHub sub-issue edges rather than prose references. Use when turning a plan, audit or bug report into tracked work.

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

Publish skills, catalog entries, and plugin registrations directly to `main`
from a task worktree after validation. Routine releases do not use GitHub issues
or pull requests. If GitHub rejects a direct push, report the exact restriction
instead of routing the change through an issue or pull request.
