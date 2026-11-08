# Contributing

## Local development

```bash
./scripts/list-skills.sh
./scripts/list-skills.sh --client codex
./scripts/link-skills.sh --client claude
./scripts/link-skills.sh --client codex
./scripts/link-skills.sh --client gemini
./scripts/link-skills.sh --client pi
uv run --with pytest==8.4.2 --with playwright==1.58.0 pytest
```

The root `conftest.py` fails any test, or the whole run, over the limits in
`pytest.ini`.

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
