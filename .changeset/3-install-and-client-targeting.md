---
"checkpickerupper-skills": major
---

Install the collection with `npx skills@latest add CheckPickerUpper/skills` (add `--all` to skip the prompts), or try one skill without installing it with `npx skills@latest use CheckPickerUpper/skills@<skill>`. The **`checkpickerupper-skills`** Claude Code plugin (`.claude-plugin/plugin.json`) registers every published skill, and its `version` now tracks these releases.

A skill can limit which agents discover it with a `clients` allow-list in its `SKILL.md` front matter, for example `clients: [claude, codex]`. The registered clients are `claude`, `codex`, `gemini`, `antigravity`, `antigravity-cli` and `pi`, listed in `scripts/agent-targets.json`. Leaving out `clients` makes a skill universal. For local development, `scripts/list-skills.sh --client <client>` lists a client's skills, and `scripts/link-skills.sh --client <client>` symlinks them into that client's skill directory.
