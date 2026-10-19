# Audit plan format

`audit_issues.py plan` and `apply` read one plan file and any number of
verdict files, all JSON. Batch agents each write a verdict file; the plan file
holds what spans batches.

```json
{
  "milestone": "Launch",
  "new_causes": {
    "import-writer": {
      "title": "The import writes rows without the server's validation",
      "body": "## Outcome\n...\n\n## Done when\n\n- [ ] ...",
      "milestone": "Launch"
    }
  },
  "milestone_reasons": {
    "Launch": "each of the 12 venues has its own payment provider"
  },
  "verdicts": {
    "101": {"verdict": "cause", "reason": "the only issue about refunds"},
    "102": {"verdict": "slice", "cause": 101, "as": "checkbox", "line": "Refunds reach the original card"},
    "103": {"verdict": "slice", "cause": "import-writer", "as": "sub-issue"},
    "104": {"verdict": "duplicate", "of": 101},
    "105": {"verdict": "done", "proof": ["https://github.com/o/r/commit/abc123", "test_refund passes"]},
    "106": {"verdict": "wrong-premise", "title": "Import validates each row as the server does",
            "fix": "Validate in the shared writer instead of retrying rejected rows.", "under": "import-writer"},
    "107": {"verdict": "out-of-date", "evidence": "0.1.170 replaced the release this describes"},
    "108": {"verdict": "still-real", "evidence": "reproduced: the import drops row 40"},
    "109": {"verdict": "unsure", "check": "replay the June import against production",
            "impossible_because": "production data is not reachable from this machine"}
  }
}
```

A verdict file is just the `verdicts` object: `{"110": {...}, "111": {...}}`.
An issue with verdicts in two files is refused.

| Field | Meaning |
|---|---|
| `milestone` | Optional scope: only open issues in this milestone need verdicts. |
| `new_causes` | Causes no issue holds yet, keyed by a name the verdicts use. `apply` creates them first. |
| `milestone_reasons` | Why a milestone ends with more than 10 causes. |
| `cause` / `under` / `of` | An issue number, or a `new_causes` key. It must stay open: a cause, still-real or unsure issue, or one outside the scope. |

| Verdict | Needs | What apply does |
|---|---|---|
| `done` | `proof` (a list) | `close_issue.py completed` with each proof |
| `duplicate` | `of` | copies its details into `of` under `(was #N)`, then `close_issue.py duplicate` |
| `slice`, as `checkbox` | `cause`, `line` | adds `- [ ] line (was #N)` to the cause's `## Done when`, copies its details under `## Folded in`, then closes it as a duplicate of the cause |
| `slice`, as `sub-issue` | `cause` | makes it a sub-issue of the cause |
| `cause` | `reason` | nothing; it stays open at the top |
| `wrong-premise` | `title`, `fix`, `under` | retitles it, writes `## Proper fix`, makes it a sub-issue of `under` |
| `out-of-date` | `evidence` | `close_issue.py out-of-date` with the evidence |
| `still-real` | `evidence` | nothing |
| `unsure` | `check`, `impossible_because` | nothing; the page lists it |

A slice with open sub-issues stays a sub-issue, and an issue that closes may
not leave open sub-issues under it; `plan` refuses both.
