Skills are organized into bucket folders under `skills/`:

- `engineering/` - code, architecture, API, macro, migration, and design-decision skills
- `productivity/` - non-code workflow skills
- `misc/` - rarely used utility skills
- `personal/` - local-only skills that are not promoted
- `in-progress/` - drafts not ready to ship
- `deprecated/` - retired skills

Every skill in `engineering/`, `productivity/`, or `misc/` must have:

- an entry in the top-level `README.md`
- an entry in its bucket `README.md`
- an entry in `.claude-plugin/plugin.json` when it targets Claude or is universal

Published skills are universal unless their `SKILL.md` declares a `clients`
allow-list. The registered values and local destinations live in
`scripts/agent-targets.json`; an unknown value is invalid. Keep one shared
skill body and use the allow-list only to control which client discovers it.

Skills in `personal/`, `in-progress/`, and `deprecated/` must not appear in `.claude-plugin/plugin.json`.
