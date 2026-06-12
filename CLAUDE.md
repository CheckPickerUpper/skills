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
- an entry in `.claude-plugin/plugin.json`

Skills in `personal/`, `in-progress/`, and `deprecated/` must not appear in `.claude-plugin/plugin.json`.
