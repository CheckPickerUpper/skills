"""Tests of close_issue.py's reading of issue bodies and GitHub issue state.

Run with: python3 -m unittest test_close_issue
"""

import unittest

from close_issue import (
    finished_milestone,
    open_pieces,
    ready_findings,
    reproduction,
    reproduction_commands,
    uncarried_pieces,
    unticked_lines,
    with_section,
)


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


REPRO = ("## Steps to reproduce\n\n```sh\n# start from a clean checkout\n"
         "example-app import fixtures/empty.csv\n```\n\nIt crashes with KeyError.\n\n## Done when\n\n- [x] it imports\n")


def rerun(ran, result, saw="it printed 0 rows imported"):
    return f"\n## Reproduction rerun\n\n- Ran: {ran}\n- Saw: {saw}\n- Result: {result}\n"


class Reproduction(unittest.TestCase):
    def test_commands_come_from_shell_blocks_inline_code_and_dollar_lines(self):
        body = ("### Steps to reproduce\n\n1. Run `example-app sync`\n```\n$ example-app import a.csv\n"
                "Traceback (most recent call last):\n```\n```bash\n# a comment\nexample-app export\n```\n")
        self.assertEqual(reproduction_commands(reproduction(body)[1]),
                         ["example-app sync", "example-app import a.csv", "example-app export"])

    def test_a_heading_inside_a_fence_does_not_end_the_reproduction(self):
        heading, lines = reproduction(REPRO)
        self.assertEqual(heading, "## Steps to reproduce")
        self.assertIn("It crashes with KeyError.", lines)

    def test_passing_tests_without_a_rerun_cannot_close(self):
        body = REPRO + "\n## Proof\n\n- pytest: 212 passed\n"
        self.assertEqual(kinds(ready_findings(issue(body=body))), ["no-rerun"])

    def test_a_rerun_that_still_fails_blocks_even_with_green_tests(self):
        body = REPRO + "\n## Proof\n\n- pytest: 212 passed\n" + rerun(
            "example-app import fixtures/empty.csv", "still fails", saw="KeyError: 'id'")
        found = ready_findings(issue(body=body))
        self.assertEqual(kinds(found), ["repro-still-fails"])
        self.assertIn("KeyError: 'id'", found[0][1])

    def test_an_unrelated_green_test_is_not_a_rerun(self):
        body = REPRO + rerun("pytest tests/test_export.py", "fixed", saw="4 passed")
        self.assertEqual(kinds(ready_findings(issue(body=body))), ["rerun-unrelated"])

    def test_a_fixed_rerun_of_the_reproduction_lets_it_close(self):
        body = REPRO + rerun("`example-app import fixtures/empty.csv` on 3f2a1c9", "fixed")
        self.assertEqual(ready_findings(issue(body=body)), [])

    def test_a_prose_reproduction_takes_any_recorded_rerun(self):
        body = "## Reproduction\n\nOpen settings, then press Save twice.\n"
        self.assertEqual(kinds(ready_findings(issue(body=body))), ["no-rerun"])
        self.assertEqual(ready_findings(issue(body=body + rerun("pressed Save twice", "fixed"))), [])

    def test_an_issue_without_a_reproduction_needs_no_rerun(self):
        self.assertEqual(ready_findings(issue(body="## Outcome\n\nFaster import.\n")), [])


class Duplicate(unittest.TestCase):
    def test_unticked_lines_the_survivor_carries_do_not_block(self):
        survivor = issue(number=3, body="## Done when\n\n- [ ] migrate the table (was #7)\n")
        self.assertEqual(uncarried_pieces(issue(body="- [ ] migrate the table"), survivor), [])

    def test_lines_and_sub_issues_the_survivor_lacks_still_block(self):
        found = uncarried_pieces(issue(body="- [ ] migrate the table", children=[(8, "OPEN")]),
                                 issue(number=3, body="(was #7)"))
        self.assertEqual(kinds(found), ["open-sub-issue", "unticked"])


if __name__ == "__main__":
    unittest.main()


def milestoned(state="OPEN", open_issues=0):
    return {**issue(state="CLOSED", reason="COMPLETED"),
            "milestone": {"number": 2, "title": "Builds overflow", "state": state,
                          "issues": {"totalCount": open_issues}}}


class Milestone(unittest.TestCase):
    def test_closing_the_last_open_issue_finishes_its_milestone(self):
        self.assertEqual(finished_milestone(milestoned()), 2)

    def test_a_milestone_with_open_issues_stays_open(self):
        self.assertIsNone(finished_milestone(milestoned(open_issues=1)))

    def test_a_closed_milestone_or_no_milestone_needs_nothing(self):
        self.assertIsNone(finished_milestone(milestoned(state="CLOSED")))
        self.assertIsNone(finished_milestone({**issue(), "milestone": None}))
