"""Behavioral tests of check_report.py at its command line."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parent / "check_report.py"

TITLE_LIST = """\
- #1407 test harness raises only real engine events
  - #1417 full verification works on the declared runner image
  - #1422 and #1423, two cue leaks
"""

NOTICED = """\
What you can see in the game from today's work: almost nothing.

- A looped ability sound no longer gets stuck on forever when part of that
  ability's effect fails to load ([#1422](https://example.com/1422)).
- Nothing could be verified on the current test machines. It can now (#1417).
"""


def check(report, *arguments):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *arguments], input=report,
        capture_output=True, text=True, timeout=10,
    )


class CheckReport(unittest.TestCase):
    def test_title_list_is_refused_with_each_line_named(self):
        result = check(TITLE_LIST)
        self.assertEqual(result.returncode, 1)
        self.assertIn("3 lines open with a tracker reference", result.stdout)
        self.assertIn("line 1: - #1407 test harness", result.stdout)
        self.assertIn("line 3: - #1422 and #1423", result.stdout)

    def test_report_with_trailing_references_passes(self):
        result = check(NOTICED)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_every_way_of_opening_with_a_reference_is_refused(self):
        for line in (
            "[#1407 Test harness raises real events](https://example.com/1407) landed",
            "**#1407** harness",
            "1. PR #1407 harness",
            "| owner/repo#1407 | harness |",
            "https://github.com/owner/repo/pull/1407 harness",
            "* [x] NRO-1407 harness",
            "## #1407 harness",
            "- pr #1407 harness",
        ):
            with self.subTest(line=line):
                self.assertEqual(check(line + "\n").returncode, 1)

    def test_ordinary_openings_pass(self):
        for line in (
            "## What changed in play",
            "utf-8 output is now readable in the log",
            "Two things changed (#1422, #1423).",
        ):
            with self.subTest(line=line):
                self.assertEqual(check(line + "\n").returncode, 0)

    def test_quoted_material_in_a_fence_is_not_judged(self):
        result = check("The old report read:\n\n~~~md\n- #1407 harness\n~~~\n")
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_report_is_read_from_a_file(self):
        with tempfile.TemporaryDirectory() as folder:
            draft = Path(folder) / "report.md"
            draft.write_text(TITLE_LIST, encoding="utf-8")
            self.assertEqual(check("", str(draft)).returncode, 1)

    def test_empty_report_is_an_error_not_a_pass(self):
        self.assertEqual(check("  \n").returncode, 2)


if __name__ == "__main__":
    unittest.main()
