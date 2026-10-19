"""Tests of close_issue.py's reading of issue bodies and GitHub issue state.

Run with: python3 -m unittest test_close_issue
"""

import unittest

from close_issue import (
    open_pieces, ready_findings, sweep_findings, unticked_lines, with_section)


def issue(number=7, state="OPEN", reason=None, body="", labels=(), parent=None,
          children=(), duplicate_of=None):
    return {
        "number": number, "title": f"Issue {number}", "url": "", "state": state,
        "stateReason": reason, "body": body,
        "labels": {"nodes": [{"name": name} for name in labels]},
        "parent": parent,
        "subIssues": {"nodes": [
            {"number": n, "title": f"Child {n}", "url": "", "state": s} for n, s in children]},
        "duplicateOf": duplicate_of,
    }


def kinds(found):
    return [kind for kind, _ in found]


class Body(unittest.TestCase):
    def test_unticked_lines_skip_ticked_lines_and_code_fences(self):
        body = "- [x] done\n- [ ] write the test\n```\n- [ ] example in a fence\n```\n* [ ] ship it\n"
        self.assertEqual(unticked_lines(body), ["write the test", "ship it"])

    def test_with_section_replaces_only_its_own_section(self):
        body = "## Outcome\n\nA\n\n## Proof\n\n- old\n\n## Evidence\n\nE\n"
        self.assertEqual(
            with_section(body, "## Proof", "- new"),
            "## Outcome\n\nA\n\n## Proof\n\n- new\n\n## Evidence\n\nE\n")

    def test_with_section_appends_when_missing(self):
        self.assertEqual(with_section("## Outcome\n\nA\n", "## Proof", "- c1"),
                         "## Outcome\n\nA\n\n## Proof\n\n- c1\n")


class Ready(unittest.TestCase):
    def test_open_sub_issue_and_unticked_line_block_closing(self):
        found = open_pieces(issue(body="- [ ] migrate", children=[(8, "OPEN"), (9, "CLOSED")]))
        self.assertEqual(kinds(found), ["open-sub-issue", "unticked"])
        self.assertIn("#8", found[0][1])

    def test_decision_without_its_answer_cannot_close(self):
        self.assertEqual(kinds(ready_findings(issue(labels=["needs-decision"]))), ["no-decision"])
        self.assertEqual(ready_findings(issue(labels=["needs-decision"], body="## Decision\n\nYes.")), [])


class Sweep(unittest.TestCase):
    def test_open_issue_under_closed_parent_is_found(self):
        found = sweep_findings(issue(parent={"number": 3, "title": "", "url": "", "state": "CLOSED"}))
        self.assertEqual(kinds(found), ["closed-parent"])

    def test_completed_issue_hiding_open_work_is_found(self):
        found = sweep_findings(issue(state="CLOSED", reason="COMPLETED", children=[(8, "OPEN")]))
        self.assertEqual(kinds(found), ["hidden"])

    def test_not_planned_issue_with_open_children_is_not_called_hidden(self):
        self.assertEqual(sweep_findings(
            issue(state="CLOSED", reason="NOT_PLANNED", body="- [ ] never")), [])

    def test_duplicate_of_nothing_is_found(self):
        self.assertEqual(kinds(sweep_findings(issue(state="CLOSED", reason="DUPLICATE"))), ["no-original"])
        self.assertEqual(sweep_findings(
            issue(state="CLOSED", reason="DUPLICATE", duplicate_of={"number": 2, "url": ""})), [])

    def test_open_decision_waits_on_the_owner(self):
        self.assertEqual(kinds(sweep_findings(issue(labels=["decision"]))), ["waiting"])


if __name__ == "__main__":
    unittest.main()
