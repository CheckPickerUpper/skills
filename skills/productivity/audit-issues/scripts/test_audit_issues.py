"""Tests of audit_issues.py's reading of a tracker and of an audit plan.

Run with: python3 -m unittest test_audit_issues
"""

import unittest

from audit_issues import (
    approval_code,
    clusters,
    draft_findings,
    findings,
    leads,
    milestone_sizes,
    operations,
    page,
    plan_findings,
    unticked_lines,
    workaround_hints,
)


def issue(number=7, state="OPEN", reason=None, body="", labels=(), parent=None,
          children=(), duplicate_of=None, title=None, milestone="v1"):
    return {
        "id": f"I_{number}", "number": number, "title": title or f"Issue {number}", "url": "",
        "state": state, "stateReason": reason, "body": body,
        "labels": {"nodes": [{"name": name} for name in labels]},
        "milestone": {"title": milestone} if milestone else None,
        "parent": parent,
        "subIssues": {"nodes": [
            {"number": n, "title": f"Child {n}", "url": "", "state": s} for n, s in children]},
        "duplicateOf": duplicate_of,
    }


def kinds(found):
    return [kind for kind, _ in found]


class Structure(unittest.TestCase):
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

    def test_open_decision_waits_on_the_owner(self):
        self.assertEqual(kinds(findings(issue(labels=["decision"]))), ["waiting"])


class Suggestions(unittest.TestCase):
    def test_issues_sharing_error_text_or_two_weaker_signals_are_one_cluster(self):
        issues = [
            issue(1, body="Fails in src/sync/push.py inside `push_rows`"),
            issue(2, body="src/sync/push.py: `push_rows` drops the last row"),
            issue(3, body="error: connection reset by peer (attempt 3)"),
            issue(4, body="Error: connection reset by peer (attempt 7)"),
            issue(5, body="unrelated"),
        ]
        self.assertEqual([members for members, _ in clusters(issues)], [[1, 2], [3, 4]])

    def test_one_shared_file_or_a_plain_word_does_not_chain_issues(self):
        issues = [issue(1, body="edit src/a.py on `master`"),
                  issue(2, body="edit src/a.py and src/b.py"),
                  issue(3, body="edit src/b.py on `master`")]
        self.assertEqual(clusters(issues), [])

    def test_one_shared_file_is_a_weaker_lead_shown_without_chaining(self):
        issues = [issue(1, body="edit src/a.py"), issue(2, body="edit src/a.py and src/b.py"),
                  issue(3, body="edit src/b.py")]
        self.assertEqual(leads(issues), [([1, 2], "file: src/a.py"), ([2, 3], "file: src/b.py")])


class Draft(unittest.TestCase):
    def setUp(self):
        self.issues = [issue(1, title="Sync drops rows", body="error: row 12 rejected by the server")]

    def draft(self, title="Import drops rows", body="", milestone="v1", parent=None):
        return {"title": title, "body": body, "milestone": milestone, "parent": parent}

    def test_a_draft_sharing_a_cause_with_an_open_issue_is_stopped(self):
        found = draft_findings(self.draft(body="error: row 40 rejected by the server"), self.issues, "")
        self.assertEqual(kinds(found), ["same-cause"])
        self.assertIn("#1 Sync drops rows", found[0][1])

    def test_a_recorded_different_cause_lets_it_through(self):
        body = "error: row 40 rejected by the server\n\nDifferent cause from #1: the import has its own writer."
        self.assertEqual(draft_findings(self.draft(body=body), self.issues, ""), [])

    def test_a_sub_issue_may_share_its_declared_parents_cause_but_no_other_issues(self):
        issues = [*self.issues, issue(2, title="Export drops rows", body="error: row 7 rejected by the server")]
        found = draft_findings(self.draft(body="error: row 40 rejected by the server", parent=1), issues, "")
        self.assertEqual(kinds(found), ["same-cause"])
        self.assertIn("#2 Export drops rows", found[0][1])

    def test_a_workaround_draft_is_stopped_until_its_premise_is_settled(self):
        self.assertEqual(kinds(draft_findings(self.draft(title="Retry the import"), [], "")), ["workaround"])
        body = "Not a workaround: the remote API documents retry as the contract."
        self.assertEqual(draft_findings(self.draft(title="Retry the import", body=body), [], ""), [])

    def test_a_draft_that_takes_its_milestone_over_ten_causes_needs_the_reason(self):
        issues = [issue(n, title=f"Separate thing {n}") for n in range(1, 11)]
        self.assertEqual(kinds(draft_findings(self.draft(), issues, "Launch")), ["milestone"])
        self.assertEqual(draft_findings(
            self.draft(), issues, "Launch.\nMore than 10 causes because: each venue differs."), [])

    def test_one_bug_in_several_languages_is_one_cluster(self):
        issues = [issue(1, title="Date parser drops time zone (Python)"),
                  issue(2, title="Date parser drops time zone in Rust"),
                  issue(3, title="Date parser is slow (Python)")]
        self.assertEqual([members for members, _ in clusters(issues)], [[1, 2]])

    def test_a_path_most_issues_mention_joins_nothing(self):
        issues = [issue(n, body="see README.md and docs/setup.md") for n in range(1, 40)]
        self.assertEqual(clusters(issues), [])

    def test_workaround_premises_are_hinted(self):
        hints = workaround_hints([issue(1, title="Raise the import timeout to 120s"),
                                  issue(2, title="Import drops rows", body="- [ ] retry each failed row"),
                                  issue(3, title="Import drops rows", body="It fails after a timeout.")])
        self.assertEqual([n for n, _ in hints], [1, 2])

    def test_milestone_size_counts_top_level_open_issues(self):
        issues = [issue(n) for n in range(1, 13)]
        issues.append(issue(20, parent={"number": 1, "title": "", "url": "", "state": "OPEN"}))
        issues.append(issue(21, state="CLOSED", reason="COMPLETED"))
        self.assertEqual(milestone_sizes(issues), {"v1": 12})


def plan_of(verdicts, **extra):
    return {"verdicts": {str(n): v for n, v in verdicts.items()}, **extra}


class Plan(unittest.TestCase):
    def setUp(self):
        self.issues = [issue(1, title="Sync loses rows"), issue(2), issue(3), issue(4), issue(5)]

    def test_every_open_issue_needs_a_verdict(self):
        found = plan_findings(plan_of({1: {"verdict": "cause", "reason": "its own fix"}}), self.issues)
        self.assertEqual(kinds(found), ["missing"] * 4)

    def test_unsure_needs_the_check_and_why_it_cannot_run_here(self):
        verdicts = {n: {"verdict": "still-real", "evidence": "reproduced"} for n in (1, 2, 3, 4)}
        verdicts[5] = {"verdict": "unsure", "check": "run the import against prod"}
        self.assertEqual(kinds(plan_findings(plan_of(verdicts), self.issues)), ["incomplete"])

    def test_a_slice_needs_a_cause_that_stays_open(self):
        verdicts = {1: {"verdict": "done", "proof": ["c1"]},
                    2: {"verdict": "slice", "cause": 1, "as": "checkbox", "line": "keep rows"},
                    3: {"verdict": "slice", "cause": "nowhere", "as": "sub-issue"},
                    4: {"verdict": "out-of-date", "evidence": "0.2 replaced it"},
                    5: {"verdict": "still-real", "evidence": "read sync.py:40"}}
        self.assertEqual(kinds(plan_findings(plan_of(verdicts), self.issues)), ["cause", "cause"])

    def test_a_checkbox_slice_with_open_sub_issues_must_stay_a_sub_issue(self):
        self.issues[1] = issue(2, children=[(9, "OPEN")])
        verdicts = {1: {"verdict": "cause", "reason": "sync"},
                    2: {"verdict": "slice", "cause": 1, "as": "checkbox", "line": "x"},
                    3: {"verdict": "still-real", "evidence": "e"},
                    4: {"verdict": "still-real", "evidence": "e"},
                    5: {"verdict": "still-real", "evidence": "e"}}
        self.assertEqual(kinds(plan_findings(plan_of(verdicts), self.issues)), ["checkbox"])

    def test_a_milestone_over_ten_causes_needs_a_reason(self):
        issues = [issue(n) for n in range(1, 13)]
        verdicts = {n: {"verdict": "still-real", "evidence": "e"} for n in range(1, 13)}
        self.assertEqual(kinds(plan_findings(plan_of(verdicts), issues)), ["milestone"])
        self.assertEqual(plan_findings(
            plan_of(verdicts, milestone_reasons={"v1": "twelve separate subsystems"}), issues), [])

    def test_the_page_leads_with_counts_and_lists_each_cause_with_its_slices(self):
        verdicts = {1: {"verdict": "cause", "reason": "sync"},
                    2: {"verdict": "slice", "cause": 1, "as": "checkbox", "line": "keep rows"},
                    3: {"verdict": "slice", "cause": 1, "as": "sub-issue"},
                    4: {"verdict": "duplicate", "of": 1},
                    5: {"verdict": "out-of-date", "evidence": "0.2 replaced it"}}
        text = page(plan_of(verdicts), self.issues, "OWNER/REPO")
        self.assertIn("Open issues: 5 → 2", text.splitlines()[2])
        self.assertIn("| v1 | 5 | 1 | 5 | 2 |", text)
        self.assertIn("#1 Sync loses rows: 2 slices (1 checkbox, 1 sub-issue)", text)

    def test_operations_move_before_they_close_and_close_children_first(self):
        self.issues[0] = issue(1, children=[(2, "OPEN")])
        self.issues[1] = issue(2, parent={"number": 1, "title": "", "url": "", "state": "OPEN"})
        verdicts = {1: {"verdict": "done", "proof": ["c1"]},
                    2: {"verdict": "done", "proof": ["c2"]},
                    3: {"verdict": "cause", "reason": "r"},
                    4: {"verdict": "slice", "cause": 3, "as": "sub-issue"},
                    5: {"verdict": "slice", "cause": "new", "as": "checkbox", "line": "x"}}
        plan = plan_of(verdicts, new_causes={"new": {"title": "T", "body": "B", "milestone": "v1"}})
        ops = [(op[0], op[1]) for op in operations(plan, self.issues)]
        self.assertEqual(ops, [("create", "new"), ("sub-issue", 4), ("done", 2),
                               ("done", 1), ("fold", 5)])

    def test_the_approval_code_changes_with_the_plan(self):
        self.assertNotEqual(approval_code([b"{}"]), approval_code([b"{ }"]))


if __name__ == "__main__":
    unittest.main()
