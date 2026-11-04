"""Tests of close_issue.py's reading of issue bodies and GitHub issue state.

Run with: python3 -m unittest test_close_issue
"""

import contextlib
import io
import json
import unittest
from unittest import mock

import os
import subprocess
import tempfile

import close_issue
from checklist_proof import Evidence, closed_issues, line_findings, removed_findings, with_derived_ticks
from close_issue import (
    commits_of,
    evidence_for,
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


REPO = "example/app"


def ev(item, commits=()):
    return evidence_for(item, REPO, commits)


def ready(item, commits=()):
    return ready_findings(item, ev(item, commits))


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
        item = issue(body="- [ ] migrate", children=[(8, "OPEN"), (9, "CLOSED")])
        found = open_pieces(item, ev(item))
        self.assertEqual(kinds(found), ["open-sub-issue", "unticked"])
        self.assertIn("#8", found[0][1])

    def test_decision_without_its_answer_cannot_close(self):
        self.assertEqual(kinds(ready(issue(labels=["needs-decision"]))), ["no-decision"])
        self.assertEqual(ready(issue(labels=["needs-decision"], body="## Decision\n\nYes.")), [])


REPRO = ("## Steps to reproduce\n\n```sh\n# start from a clean checkout\n"
         "example-app import fixtures/empty.csv\n```\n\nIt crashes with KeyError.\n\n## Done when\n\n- [x] imports: it imports\n")
IMPORT_FIX = [("a1b2c3d4e5f6", "Import an empty CSV\n\nPart of #7: imports")]


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
        self.assertEqual(kinds(ready(issue(body=body), IMPORT_FIX)), ["no-rerun"])

    def test_a_rerun_that_still_fails_blocks_even_with_green_tests(self):
        body = REPRO + "\n## Proof\n\n- pytest: 212 passed\n" + rerun(
            "example-app import fixtures/empty.csv", "still fails", saw="KeyError: 'id'")
        found = ready(issue(body=body), IMPORT_FIX)
        self.assertEqual(kinds(found), ["repro-still-fails"])
        self.assertIn("KeyError: 'id'", found[0][1])

    def test_an_unrelated_green_test_is_not_a_rerun(self):
        body = REPRO + rerun("pytest tests/test_export.py", "fixed", saw="4 passed")
        self.assertEqual(kinds(ready(issue(body=body), IMPORT_FIX)), ["rerun-unrelated"])

    def test_a_fixed_rerun_of_the_reproduction_lets_it_close(self):
        body = REPRO + rerun("`example-app import fixtures/empty.csv` on 3f2a1c9", "fixed")
        self.assertEqual(ready(issue(body=body), IMPORT_FIX), [])

    def test_a_prose_reproduction_takes_any_recorded_rerun(self):
        body = "## Reproduction\n\nOpen settings, then press Save twice.\n"
        self.assertEqual(kinds(ready(issue(body=body), IMPORT_FIX)), ["no-rerun"])
        self.assertEqual(ready(issue(body=body + rerun("pressed Save twice", "fixed")), IMPORT_FIX), [])

    def test_an_issue_without_a_reproduction_needs_no_rerun(self):
        self.assertEqual(ready(issue(body="## Outcome\n\nFaster import.\n")), [])


class StandInGitHub:
    """Answers the gh calls `completed` makes for one issue with no checklist."""

    def __init__(self, item):
        self.item = item

    def __call__(self, *args, stdin=None):
        match args[:2]:
            case ("api", "graphql"):
                if "userContentEdits" in args[3]:
                    edits = {"nodes": [], "pageInfo": {"hasNextPage": False, "endCursor": None}}
                    return json.dumps({"data": {"repository": {"issue": {"userContentEdits": edits}}}})
                return json.dumps({"data": {"repository": {"issue": self.item}}})
            case ("issue", "edit"):
                self.item["body"] = stdin
            case ("issue", "close"):
                self.item.update(state="CLOSED", stateReason="COMPLETED")
        return ""


class CompletedProof(unittest.TestCase):
    def complete(self, github, proof):
        argv = ["completed", "--repo", REPO, "--issue", "7", "--proof", proof]
        with mock.patch.object(close_issue, "gh", github), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(close_issue.main(argv), 0)

    def test_closing_again_keeps_earlier_proof_and_adds_no_duplicate(self):
        github = StandInGitHub(issue(body="Fix it.\n\n## Proof\n\n- first close: c0ffee1\n"))
        self.complete(github, "second close: deadbee")
        self.complete(github, "second close: deadbee")
        self.assertEqual(close_issue.section_lines(github.item["body"], "## Proof"),
                         ["", "- first close: c0ffee1", "- second close: deadbee"])


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


def lines_issue(body, labels=()):
    return issue(number=1962, body=body, labels=labels)


CLEANSE = "## Done when\n\n- [x] cleanse: Cleanse effects\n- [ ] heal: Heal a fighter\n"


class EarnedTicks(unittest.TestCase):
    def test_a_box_ticked_by_hand_proves_nothing(self):
        found = line_findings(ev(lines_issue(CLEANSE)))
        self.assertEqual(kinds(found), ["ticked-unproven", "unticked"])
        self.assertIn("Part of #1962: cleanse", found[0][1])

    def test_a_landed_commit_naming_the_line_proves_it_even_unticked(self):
        commits = [("c0ffee1234", "Cleanse effects\n\nPart of #1962: cleanse, heal")]
        self.assertEqual(line_findings(ev(lines_issue(CLEANSE), commits)), [])

    def test_a_commit_for_another_issue_number_proves_nothing(self):
        commits = [("c0ffee1234", "Part of #19620: cleanse\nPart of other/repo#1962: heal")]
        self.assertEqual(kinds(line_findings(ev(lines_issue(CLEANSE), commits))), ["ticked-unproven", "unticked"])

    def test_a_line_ending_in_a_hash_needs_that_commit_to_name_the_issue(self):
        body = "- [x] Cleanse effects (c0ffee1)\n"
        named = [("c0ffee1234", "Cleanse effects\n\nCloses #1962")]
        unnamed = [("c0ffee1234", "Cleanse effects")]
        other_issue = [("c0ffee1234", "Cleanse effects\n\nCloses #19620")]
        self.assertEqual(line_findings(ev(lines_issue(body), named)), [])
        self.assertEqual(kinds(line_findings(ev(lines_issue(body), unnamed))), ["ticked-unproven"])
        self.assertEqual(kinds(line_findings(ev(lines_issue(body), other_issue))), ["ticked-unproven"])

    def test_a_proof_line_with_a_link_proves_its_line(self):
        body = CLEANSE + "\n## Proof\n\n- cleanse: walked it https://example.com/clip\n- heal: it works\n"
        self.assertEqual(kinds(line_findings(ev(lines_issue(body)))), ["unticked"])

    def test_a_decision_proves_its_own_lines(self):
        body = "## Decision\n\nShip it.\n\n## Done when\n\n- [x] chosen: One option is chosen\n"
        self.assertEqual(line_findings(ev(lines_issue(body, labels=["decision"]))), [])
        self.assertEqual(kinds(line_findings(ev(lines_issue(body)))), ["ticked-unproven"])

    def test_derived_ticks_untick_hand_ticks_and_tick_proved_lines(self):
        commits = [("c0ffee1234", "Part of #1962: heal")]
        self.assertEqual(with_derived_ticks(ev(lines_issue(CLEANSE), commits)),
                         "## Done when\n\n- [ ] cleanse: Cleanse effects\n- [x] heal: Heal a fighter\n")


class RemovedLines(unittest.TestCase):
    EARLIER = ["- [ ] cleanse: Cleanse effects\n- [ ] Show the heal number above the fighter\n"]

    def removed(self, body, commits=(), others=None):
        return removed_findings(ev(lines_issue(body), commits), self.EARLIER, lambda n: (others or {})[n])

    def test_a_line_deleted_without_a_record_blocks(self):
        found = self.removed("- [ ] Show the heal number above the fighter\n")
        self.assertEqual(kinds(found), ["removed-unrecorded"])
        self.assertIn("cleanse", found[0][1])

    def test_a_dropped_line_with_its_reason_is_allowed(self):
        body = "- [ ] Show the heal number above the fighter\n\n## Checklist changes\n\n- cleanse: dropped, the owner cut it\n"
        self.assertEqual(self.removed(body), [])
        bare = body.replace("dropped, the owner cut it", "dropped")
        self.assertEqual(kinds(self.removed(bare)), ["removed-unrecorded"])

    def test_a_moved_line_must_arrive_in_its_new_issue(self):
        body = "- [ ] Show the heal number above the fighter\n\n## Checklist changes\n\n- cleanse: moved to #9\n"
        self.assertEqual(self.removed(body, others={9: "- [ ] cleanse: Cleanse effects (was #1962)\n"}), [])
        self.assertEqual(kinds(self.removed(body, others={9: "- [ ] heal: Heal\n"})), ["moved-missing"])

    def test_a_moved_line_that_gains_an_id_in_its_new_issue_arrives(self):
        body = ("- [ ] cleanse: Cleanse effects\n\n## Checklist changes\n\n"
                "- Show the heal number above the fighter: moved to #9\n")
        carried = "- [ ] number: Show the heal number above the fighter (was #1962)\n"
        self.assertEqual(self.removed(body, others={9: carried}), [])
        unmarked = carried.replace(" (was #1962)", "")
        self.assertEqual(kinds(self.removed(body, others={9: unmarked})), ["moved-missing"])

    def test_a_reworded_line_without_an_id_is_not_a_removal(self):
        body = "- [ ] cleanse: Cleanse effects\n- [ ] Show the healed amount above the fighter\n"
        self.assertEqual(self.removed(body), [])

    def test_a_line_that_gains_an_id_is_not_a_removal(self):
        same = "- [ ] cleanse: Cleanse effects\n- [ ] number: Show the heal number above the fighter\n"
        self.assertEqual(self.removed(same), [])
        reworded = same.replace("heal number", "healed amount")
        self.assertEqual(self.removed(reworded), [])
        self.assertEqual(kinds(self.removed("- [ ] cleanse: Cleanse effects\n")), ["removed-unrecorded"])

    def test_a_line_removed_after_its_commit_landed_is_fine(self):
        body = "- [ ] Show the heal number above the fighter\n"
        self.assertEqual(self.removed(body, [("c0ffee1234", "Part of #1962: cleanse")]), [])


class ClosingKeywords(unittest.TestCase):
    def test_only_closing_keywords_for_this_repository_count(self):
        message = "Closes #7\nfixes example/app#8\nResolves other/repo#9\nPart of #10: x\nfix: tidy #11"
        self.assertEqual(closed_issues(message, REPO), {7, 8})


class Commits(unittest.TestCase):
    def test_commit_messages_are_read_whole_from_git(self):
        root = os.environ.get("TEST_SCRATCH") or tempfile.gettempdir()
        with tempfile.TemporaryDirectory(dir=root) as checkout:
            run = lambda *a: subprocess.run(["git", "-C", checkout, *a], check=True, capture_output=True,
                                            text=True).stdout.strip()
            run("init", "-q")
            # Plumbing makes the commit without running any commit hooks a machine adds.
            commit = run("-c", "user.name=t", "-c", "user.email=t@example.com", "commit-tree", run("write-tree"),
                         "-m", "Cleanse effects", "-m", "Part of #1962: cleanse\nPart of #1962: heal")
            run("update-ref", "HEAD", commit)
            [(sha, message)] = commits_of(checkout, "HEAD")
            self.assertEqual(len(sha), 40)
            self.assertEqual(message.strip(), "Cleanse effects\n\nPart of #1962: cleanse\nPart of #1962: heal")
