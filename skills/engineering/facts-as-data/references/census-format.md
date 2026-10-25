# Census format

A census is a tab-separated file with this exact header:

```text
site	group	meaning	decision	table	readers	check	reason
```

One row per lead site. `buried_facts.py --record <file>` settles a lead when a row's `site` is the lead's file (`src/rules/pause.rs`, settling every lead in it) or its file and line (`src/rules/pause.rs:14`). Every field is filled; write `-` for none.

| Field | Holds |
| --- | --- |
| `site` | the file, or `file:line`, the lead was found at |
| `group` | a short name shared by every row of one meaning |
| `meaning` | what the fact is, in domain words |
| `decision` | `table`, `is-table` or `not-data` |
| `table` | where the table lives or will live |
| `readers` | the logic sites that read it |
| `check` | the completeness check that fails on a missing case |
| `reason` | for `not-data`, why the variation has no real form |

| Decision | Required | Must be `-` |
| --- | --- | --- |
| `table`: the fact moves into a table | `table`, `readers`, `check` | |
| `is-table`: the site already is the shared table | `table`, `readers`, `check` | |
| `not-data`: code stays code | `reason` | `table`, `readers`, `check` |

Example:

```text
site	group	meaning	decision	table	readers	check	reason
rules/deadline_polling_loop.rs:15	pause	calls that pause the thread	table	catalogue/<language>/pause.rs	deadline_polling_loop, hand_rolled_retry	build fails when a supported language has no pause entry	-
cli/flags.py:40	output modes	the two output formats of one command	not-data	-	-	-	one command reads it and no second format is planned; no axis of variation
```
