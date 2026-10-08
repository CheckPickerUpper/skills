"""Behavioral tests of issues_check.py at its command line and the `gh` boundary.

`fixtures/gh` stands in for the gh CLI on PATH and serves responses captured
from a real repository by `fixtures/capture.py`. Constructed cases start from
a captured response and change only the fields the case is about.
"""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "issues_check.py"
CAPTURED = HERE / "fixtures"
REPOSITORY = "example-org/example-app"


def reasons(*lines):
    return "## Outcome\nRedacted line.\n\n## Blocked by\n" + "\n".join(lines) + "\n\n## Done when\n- [ ] Redacted.\n"


class IssuesCheckTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="issues-check-")
        self.addCleanup(temp.cleanup)
        self.fixtures = Path(temp.name)
        for captured in CAPTURED.glob("*.json"):
            shutil.copy(captured, self.fixtures)

    def edit(self, number, change):
        path = self.fixtures / f"{number}.json"
        response = json.loads(path.read_text())
        change(response["data"]["repository"]["issue"])
        path.write_text(json.dumps(response))

    def run_check(self, *arguments, repository=REPOSITORY):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--repo", repository, *arguments],
            env={**os.environ, "PATH": f"{CAPTURED}{os.pathsep}{os.environ['PATH']}",
                 "ISSUES_CHECK_FIXTURES": str(self.fixtures), "ISSUES_CHECK_REPOSITORY": REPOSITORY},
            capture_output=True, text=True, timeout=30,
        )

    def findings(self, *numbers):
        result = self.run_check(*map(str, numbers), "--json")
        return result, sorted((f["kind"], f["issue"], f["blocker"]) for f in json.loads(result.stdout)["findings"])

    def test_closed_blockers_without_reasons_are_stale_and_missing(self):
        result, found = self.findings(830)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(found, [("missing-reason", 830, 812), ("missing-reason", 830, 1173),
                                 ("stale-blocker", 830, 812), ("stale-blocker", 830, 1173)])

    def test_closed_blocker_is_stale_even_with_a_reason(self):
        self.edit(830, lambda issue: issue.update(body=reasons(
            "- #1173 Issue 1173: cannot start until it lands, because it owns the schema.",
            "- #812 Issue 812: cannot meet the query criterion until it lands, because the crate is missing.")))
        result, found = self.findings(830)
        self.assertEqual(found, [("stale-blocker", 830, 812), ("stale-blocker", 830, 1173)])

    def test_open_blockers_with_valid_reasons_pass(self):
        self.edit(1224, lambda issue: issue.update(body=reasons(
            "- #1284 Issue 1284: cannot meet \"the observation saves\" until it lands, because the writer is unscoped.",
            "- #830 Issue 830: cannot start until it lands, because it replaces the query layer this fix edits.")))
        result = self.run_check("1224")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("No findings across 1 issues.", result.stdout)

    def test_reason_line_without_cannot_is_missing(self):
        self.edit(1224, lambda issue: issue.update(body=reasons(
            "- #1284 Issue 1284: cleaner after it lands.")))
        result, found = self.findings(1224)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(found, [("missing-reason", 1224, 830), ("missing-reason", 1224, 1284)])

    def test_reason_for_a_non_edge_is_orphan(self):
        self.edit(1224, lambda issue: issue.update(body=
            "## Outcome\n- #777 Issue 777: cannot start, outside the section.\n\n" + reasons(
                "- #1284 Issue 1284: cannot meet the save criterion until it lands, because the writer is unscoped.",
                "- #830 Issue 830: cannot start until it lands, because it replaces the query layer.",
                "```",
                "- #888 Issue 888: cannot start, inside a code fence.",
                "```",
                "- #999 Issue 999: cannot start until it lands, because it was once planned.")))
        result, found = self.findings(1224)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(found, [("orphan-reason", 1224, 999)])

    def test_parent_edges_without_reasons_are_parent_and_missing(self):
        result, found = self.findings(1279)
        self.assertEqual(result.returncode, 1)
        blockers = [1265, 1266, 1267, 1268, 1269, 1270, 1271, 1272, 1273, 1274]
        self.assertEqual(found, sorted([("missing-reason", 1279, b) for b in blockers]
                                       + [("parent-blocker", 1279, b) for b in blockers]))

    def test_parent_reason_must_say_the_whole_issue_cannot_start(self):
        def change(issue):
            for node in issue["blockedBy"]["nodes"]:
                node["state"] = "OPEN"
            issue["body"] = reasons(
                "- #1201 Issue 1201: cannot start until it lands, because every child edits its columns.",
                "- #1199 Issue 1199: cannot meet \"money is exact\" until it lands, because the type is missing.")
        self.edit(1187, change)
        result, found = self.findings(1187)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(found, [("parent-blocker", 1187, 1199)])

    def test_reason_line_cannot_cover_a_blocker_in_another_repository(self):
        def change(issue):
            issue["blockedBy"]["nodes"][1]["repository"]["nameWithOwner"] = "other-org/other-app"
            issue["body"] = reasons(
                "- #1284 Issue 1284: cannot meet the save criterion until it lands, because the writer is unscoped.",
                "- #830 Issue 830: cannot start until it lands, because it replaces the query layer.")
        self.edit(1224, change)
        result, found = self.findings(1224)
        self.assertEqual(found, [("missing-reason", 1224, 830), ("orphan-reason", 1224, 830)])
        self.assertIn("other-org/other-app#830", json.loads(result.stdout)["findings"][0]["detail"])

    def test_text_report_names_issues_and_summarises_what_exists(self):
        result = self.run_check("318", "1224")
        self.assertEqual(result.returncode, 1)
        self.assertIn("example-org/example-app#318 Issue 318 [OPEN]", result.stdout)
        self.assertIn("labels: task, ready-for-agent, kind:bug, bug:high", result.stdout)
        self.assertIn("milestone: Milestone 5", result.stdout)
        self.assertIn("#597 Issue 597 [CLOSED] (no reason line)", result.stdout)
        self.assertIn("stale-blocker: #318 Issue 318: blocked by #597 Issue 597, which is closed", result.stdout)
        self.assertIn("missing-reason: #1224 Issue 1224: blocked by #1284 Issue 1284", result.stdout)
        self.assertIn("The rule: an issue is blocked by X only when", result.stdout)

    def test_json_summary_reports_labels_milestone_and_edges(self):
        result = self.run_check("830", "--json")
        issue = json.loads(result.stdout)["issues"][0]
        self.assertEqual(issue["labels"], ["ready-for-agent", "kind:tech-debt", "area:foundation"])
        self.assertEqual(issue["milestone"], "Milestone 5")
        self.assertEqual(issue["sub_issues"], 0)
        self.assertEqual([(b["number"], b["state"]) for b in issue["blocked_by"]], [(1173, "CLOSED"), (812, "CLOSED")])

    def test_missing_issue_is_a_read_failure_even_after_good_reads(self):
        result = self.run_check("830", "4242")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("gh api graphql issue example-org/example-app#4242", result.stderr)
        self.assertIn("Could not resolve to an Issue with the number of 4242", result.stderr)

    def test_unknown_repository_is_a_read_failure(self):
        result = self.run_check("830", repository="example-org/other-app")
        self.assertEqual(result.returncode, 2)
        self.assertIn("example-org/other-app#830", result.stderr)

    def test_unpaged_edges_are_a_read_failure(self):
        self.edit(1279, lambda issue: issue["blockedBy"].update(totalCount=101))
        result = self.run_check("1279")
        self.assertEqual(result.returncode, 2)
        self.assertIn("more than 100 blockedBy", result.stderr)


if __name__ == "__main__":
    unittest.main()
