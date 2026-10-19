"""Tests of audit_issues.py's reading of GitHub issue state.

Run with: python3 -m unittest test_audit_issues
"""

import unittest

from audit_issues import findings, unticked_lines


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


class Audit(unittest.TestCase):
    def test_unticked_lines_skip_ticked_lines_and_code_fences(self):
        body = "- [x] done\n- [ ] write the test\n```\n- [ ] example in a fence\n```\n* [ ] ship it\n"
        self.assertEqual(unticked_lines(body), ["write the test", "ship it"])

    def test_open_issue_under_closed_parent_is_found(self):
        found = findings(issue(parent={"number": 3, "title": "", "url": "", "state": "CLOSED"}))
        self.assertEqual(kinds(found), ["closed-parent"])

    def test_completed_issue_hiding_open_work_is_found(self):
        found = findings(issue(state="CLOSED", reason="COMPLETED", body="- [ ] migrate",
                               children=[(8, "OPEN"), (9, "CLOSED")]))
        self.assertEqual(kinds(found), ["hidden", "hidden"])
        self.assertIn("#8", found[0][1])

    def test_not_planned_issue_with_open_children_is_not_called_hidden(self):
        self.assertEqual(findings(issue(state="CLOSED", reason="NOT_PLANNED", body="- [ ] never")), [])

    def test_duplicate_of_nothing_is_found(self):
        self.assertEqual(kinds(findings(issue(state="CLOSED", reason="DUPLICATE"))), ["no-original"])
        self.assertEqual(findings(
            issue(state="CLOSED", reason="DUPLICATE", duplicate_of={"number": 2, "url": ""})), [])

    def test_decision_closed_without_its_answer_is_found(self):
        self.assertEqual(kinds(findings(
            issue(state="CLOSED", reason="COMPLETED", labels=["decision"]))), ["no-decision"])

    def test_open_decision_waits_on_the_owner(self):
        self.assertEqual(kinds(findings(issue(labels=["decision"]))), ["waiting"])


if __name__ == "__main__":
    unittest.main()
