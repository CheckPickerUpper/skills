---
"checkpickerupper-skills": minor
---

Ship **`facts-as-data`** in the **Engineering** bucket, so it installs with `npx skills` and loads from the Claude Code plugin.

`facts-as-data` (model-invoked) moves knowledge buried in logic into one table every reader shares, before a second copy of it exists. It covers four jobs: a census of a codebase, the design of each table, the review of one diff, and a counter-test that keeps code as code when its variation has no real form.

- `scripts/buried_facts.py <paths>` lists leads (regex alternations of names, `||` chains, literal name lists, runs of branches keyed by a literal) and, with `--record <census.tsv>`, exits non-zero until every lead site has a recorded decision: `table`, `is-table` or `not-data`.
