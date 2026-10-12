"""Exercise audit records through the script's public command line."""

from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_decisions.py"
HEADER = ["command", "protection", "cheaper", "decision", "reason", "evidence"]
REUSE = [
    "full repository verify",
    "broken integration between packages",
    "existing final-head full run",
    "reuse",
    "same commit and environment; repository accepts recorded proof",
    "run 42 on revision abc123, complete PASS",
]


class CheckDecisionTests(unittest.TestCase):
    def invoke(self, rows: list[list[str]]) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as scratch:
            record = Path(scratch) / "decisions.tsv"
            with record.open("w", encoding="utf-8", newline="") as stream:
                csv.writer(stream, delimiter="\t").writerows(rows)
            return subprocess.run(
                [sys.executable, str(SCRIPT), str(record)],
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
            )

    def test_complete_record_when_a_command_contains_tabs_is_accepted(self) -> None:
        row = REUSE.copy()
        row[0] = "verify\twith an embedded tab"
        result = self.invoke([HEADER, row])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("1 checks", result.stderr)

    def test_reuse_without_evidence_when_audited_is_refused(self) -> None:
        row = REUSE.copy()
        row[-1] = "   "
        result = self.invoke([HEADER, row])
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("evidence", result.stderr)

    def test_missing_column_when_audited_is_refused(self) -> None:
        result = self.invoke([HEADER, REUSE[:-1]])
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("found 5 fields; expected 6", result.stderr)

    def test_unknown_action_when_audited_is_refused(self) -> None:
        row = REUSE.copy()
        row[3] = "trust"
        result = self.invoke([HEADER, row])
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("'trust'", result.stderr)

    def test_duplicate_command_with_conflicting_choices_when_audited_is_refused(self) -> None:
        row = REUSE.copy()
        row[3] = "run"
        result = self.invoke([HEADER, REUSE, row])
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn(REUSE[0], result.stderr)

    def test_empty_inventory_when_audited_is_refused(self) -> None:
        result = self.invoke([HEADER])
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("no decisions", result.stderr)

    def test_swapped_column_names_when_audited_are_refused(self) -> None:
        header = HEADER.copy()
        header[1], header[2] = header[2], header[1]
        result = self.invoke([header, REUSE])
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("Header", result.stderr)


if __name__ == "__main__":
    unittest.main()
