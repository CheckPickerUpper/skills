"""Tests of audit_issues.py's reading of a tracker and of an audit plan.

Run with: python3 -m unittest test_audit_issues
"""

import contextlib
import io
import json
import os
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

import audit_issues

from audit_issues import (
    approval_code,
    clusters,
    draft_findings,
    findings,
    leads,
    milestone_sizes,
    operations,
    subject_leads,
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

    def test_a_plain_word_in_backticks_is_not_a_code_name(self):
        issues = [issue(1, body="run `master` then `deploy`"), issue(2, body="run `master` then `deploy`")]
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

    def plain_issues(self):
        return [issue(1, title="A chakra dash resolves movement and fighter contact outcomes",
                      body="The archived design describes a resource-gated high-speed attack."),
                issue(2, title="Hold C to charge chakra"), issue(3, title="Stop a fighter's chakra regaining"),
                issue(4, title="Show the shop prices"), issue(5, title="Save the outfit"),
                issue(6, title="Record each guess the player's machine made")]

    def test_a_plain_words_draft_sharing_a_rare_title_phrase_is_stopped(self):
        found = draft_findings(self.draft(title="Chakra dash on a double-tap of W"), self.plain_issues(), "")
        self.assertEqual(kinds(found), ["same-subject"])
        self.assertIn("#1 A chakra dash", found[0][1])

    def test_one_shared_title_word_is_a_lead_not_a_refusal(self):
        draft = self.draft(title="Open the shop cooldown")
        self.assertEqual(draft_findings(draft, self.plain_issues(), ""), [])
        self.assertEqual([n for _, n, _ in subject_leads(draft, self.plain_issues())], [4])

    def test_a_recorded_different_cause_clears_a_subject_match(self):
        body = "Different cause from #1: this is the input binding, not the dash itself."
        draft = self.draft(title="Chakra dash on a double-tap of W", body=body)
        self.assertEqual(draft_findings(draft, self.plain_issues(), ""), [])

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
        issues = [issue(n, body="see docs/setup.md and src/main.py") for n in range(1, 40)]
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
                    2: {"verdict": "slice", "cause": 1, "as": "checkbox", "line": "keep-rows: keep rows"},
                    3: {"verdict": "slice", "cause": "nowhere", "as": "sub-issue", "because": "parallel", "detail": "a second agent builds the editor"},
                    4: {"verdict": "out-of-date", "evidence": "0.2 replaced it"},
                    5: {"verdict": "still-real", "evidence": "read sync.py:40"}}
        self.assertEqual(kinds(plan_findings(plan_of(verdicts), self.issues)), ["cause", "cause"])

    def test_a_folded_line_carries_a_line_id_unique_in_its_cause(self):
        verdicts = {1: {"verdict": "cause", "reason": "sync"},
                    2: {"verdict": "slice", "cause": 1, "as": "checkbox", "line": "Keep rows"},
                    3: {"verdict": "slice", "cause": 1, "as": "checkbox", "line": "keep-rows: keep rows"},
                    4: {"verdict": "slice", "cause": 1, "as": "checkbox", "line": "keep-rows: and their order"},
                    5: {"verdict": "still-real", "evidence": "e"}}
        found = plan_findings(plan_of(verdicts), self.issues)
        self.assertEqual(kinds(found), ["line-id", "line-id"])
        self.assertIn("#2", found[0][1])
        self.assertIn("#4", found[1][1])
        self.issues[0] = issue(1, body="## Done when\n\n- [ ] keep-rows: keep rows\n")
        verdicts[3]["line"] = "keep-rows: keep rows again"
        del verdicts[2], verdicts[4]
        verdicts.update({2: {"verdict": "still-real", "evidence": "e"}, 4: {"verdict": "still-real", "evidence": "e"}})
        self.assertEqual(kinds(plan_findings(plan_of(verdicts), self.issues)), ["line-id"])

    def closing_with_lines(self, fates=None, verdict="out-of-date"):
        self.issues[0] = issue(1, title="Sync loses rows", body="## Done when\n\n- [ ] keep-rows: Keep rows\n")
        self.issues[1] = issue(2, body="## Done when\n\n- [ ] order: Keep row order\n- [ ] Write the import guide\n")
        verdicts = {n: {"verdict": "still-real", "evidence": "e"} for n in (1, 3, 4, 5)}
        verdicts[2] = {"verdict": verdict, "evidence": "0.2 replaced it", "proof": ["c1"]}
        if fates is not None:
            verdicts[2]["lines"] = fates
        return plan_of(verdicts)

    def test_a_closing_issue_gives_each_open_line_a_fate(self):
        found = plan_findings(self.closing_with_lines(), self.issues)
        self.assertEqual(kinds(found), ["line-fate", "line-fate"])
        self.assertIn("#2", found[0][1])
        self.assertIn("order: Keep row order", found[0][1])
        self.assertIn('"dropped"', found[0][1])
        self.assertIn("Write the import guide", found[1][1])
        self.assertEqual(kinds(plan_findings(self.closing_with_lines(verdict="done"), self.issues)),
                         ["line-fate", "line-fate"])

    def test_line_fates_name_real_lines_and_new_ids_in_a_cause_that_stays_open(self):
        fates = {"order": {"moved": 1}, "Write the import guide": {"dropped": "the guide moved to the wiki"}}
        self.assertEqual(plan_findings(self.closing_with_lines(fates), self.issues), [])
        cases = {
            "no-such-line": {**fates, "colour": {"dropped": "never mind"}},
            "id-taken": {**fates, "order": {"moved": 1, "id": "keep-rows"}},
            "no-id": {**fates, "Write the import guide": {"moved": 1}},
            "closing-target": {**fates, "order": {"moved": 2}},
            "no-reason": {**fates, "order": {"dropped": " "}},
        }
        for name, case in cases.items():
            with self.subTest(name):
                self.assertEqual(kinds(plan_findings(self.closing_with_lines(case), self.issues)), ["line-fate"])

    def test_a_line_a_landed_commit_proves_needs_no_fate(self):
        plan = self.closing_with_lines({"Write the import guide": {"dropped": "the guide moved to the wiki"}})
        proofs = audit_issues.closing_evidence(plan, self.issues, "example/app",
                                               lambda number: [("c0ffee1234", f"Part of #{number}: order")])
        self.assertEqual(plan_findings(plan, self.issues, proofs), [])

    def test_the_page_shows_each_closing_issues_line_fates(self):
        fates = {"order": {"moved": 1, "id": "row-order"},
                 "Write the import guide": {"dropped": "the guide moved to the wiki"}}
        text = page(self.closing_with_lines(fates), self.issues, "OWNER/REPO")
        self.assertIn("- #2 Issue 2: 'order: Keep row order' moves to #1 Sync loses rows as 'row-order'", text)
        self.assertIn("- #2 Issue 2: 'Write the import guide' is dropped: the guide moved to the wiki", text)

    def test_a_sub_issue_slice_names_why_it_is_not_a_checklist_line(self):
        verdicts = {1: {"verdict": "cause", "reason": "sync"},
                    2: {"verdict": "slice", "cause": 1, "as": "sub-issue"},
                    3: {"verdict": "slice", "cause": 1, "as": "sub-issue", "because": "same milestone",
                        "detail": "it was filed that way"},
                    4: {"verdict": "slice", "cause": 1, "as": "sub-issue", "because": "outside-wait",
                        "detail": "waits on the vendor's export API"},
                    5: {"verdict": "still-real", "evidence": "e"}}
        found = plan_findings(plan_of(verdicts), self.issues)
        self.assertEqual(kinds(found), ["incomplete", "sub-issue"])
        self.assertIn("#2", found[0][1])
        self.assertIn("#3", found[1][1])

    def test_a_checkbox_slice_with_open_sub_issues_must_stay_a_sub_issue(self):
        self.issues[1] = issue(2, children=[(9, "OPEN")])
        verdicts = {1: {"verdict": "cause", "reason": "sync"},
                    2: {"verdict": "slice", "cause": 1, "as": "checkbox", "line": "x: x"},
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
                    2: {"verdict": "slice", "cause": 1, "as": "checkbox", "line": "keep-rows: keep rows"},
                    3: {"verdict": "slice", "cause": 1, "as": "sub-issue", "because": "parallel", "detail": "a second agent builds the editor"},
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
                    4: {"verdict": "slice", "cause": 3, "as": "sub-issue", "because": "parallel", "detail": "a second agent builds the editor"},
                    5: {"verdict": "slice", "cause": "new", "as": "checkbox", "line": "x: x"}}
        plan = plan_of(verdicts, new_causes={"new": {"title": "T", "body": "B", "milestone": "v1"}})
        ops = [(op[0], op[1]) for op in operations(plan, self.issues)]
        self.assertEqual(ops, [("create", "new"), ("sub-issue", 4), ("done", 2),
                               ("done", 1), ("fold", 5)])

    def test_the_approval_code_changes_with_the_plan(self):
        self.assertNotEqual(approval_code([b"{}"]), approval_code([b"{ }"]))


class StandInGitHub:
    """Answers `gh api graphql` from a list of issues, the way GitHub would: a since-filter
    keeps issues updated at or after that time, oldest first. Records the kind of each query."""

    def __init__(self):
        self.issues, self.calls = [], []

    def __call__(self, *args, stdin=None):
        values = dict(a.split("=", 1) for flag, a in zip(args, args[1:]) if flag in ("-f", "-F"))
        query = values["query"]
        if "totalCount" in query and "nodes" not in query:
            kind = "count"
        elif "filterBy" in query:
            kind = "since"
        else:
            kind = "full"
        self.calls.append(kind)
        issues = self.issues
        if kind == "count":
            return json.dumps({"data": {"repository": {"issues": {"totalCount": len(issues)}}}})
        if kind == "since":
            issues = sorted((i for i in issues if i["updatedAt"] >= values["since"]),
                            key=lambda i: i["updatedAt"])
        start = int(values.get("after", "0"))
        more = start + 50 < len(issues)
        return json.dumps({"data": {"repository": {"issues": {
            "pageInfo": {"hasNextPage": more, "endCursor": str(start + 50)},
            "nodes": issues[start:start + 50]}}}})


class Result:
    """What one run printed and returned, read like a finished command."""

    def __init__(self, returncode, stdout, stderr):
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr


def tracked(number, updated, **fields):
    return {**issue(number, **fields), "updatedAt": updated}


class MirrorWrites(unittest.TestCase):
    def test_overlapping_writes_each_finish_and_leave_whole_json(self):
        folder = tempfile.TemporaryDirectory(prefix="audit-issues-test-")
        self.addCleanup(folder.cleanup)
        path = Path(folder.name) / "example__app.json"
        real_replace, lock = os.replace, threading.Lock()
        first_paused, second_done, calls = threading.Event(), threading.Event(), []

        def replace_after_the_other(source, target):
            with lock:
                calls.append(source)
                first = len(calls) == 1
            if first:
                first_paused.set()
                second_done.wait(timeout=5)
            real_replace(source, target)
            if not first:
                second_done.set()

        errors = []

        def first_write():
            try:
                audit_issues.write_mirror(path, {"1": issue(1)}, "first")
            except OSError as error:
                errors.append(error)

        with mock.patch("os.replace", replace_after_the_other):
            writer = threading.Thread(target=first_write)
            writer.start()
            first_paused.wait(timeout=5)
            audit_issues.write_mirror(path, {"2": issue(2)}, "second")
            writer.join(timeout=5)
        self.assertEqual(errors, [])
        self.assertEqual(json.loads(path.read_text())["synced_at"], "first")
        self.assertEqual([p.name for p in path.parent.iterdir()], [path.name])


class Mirror(unittest.TestCase):
    """Every command reads the tracker through a local copy that only fetches what changed."""

    def setUp(self):
        folder = tempfile.TemporaryDirectory(prefix="audit-issues-test-")
        self.addCleanup(folder.cleanup)
        self.folder = Path(folder.name)
        self.github = StandInGitHub()
        self.cache = self.folder / "cache"
        self.mirror = self.cache / "checkpickerupper" / "audit-issues" / "example__app.json"
        self.draft_body = self.folder / "draft.md"
        self.draft_body.write_text("error: row 40 rejected by the server")

    def tracker(self, *issues):
        self.github.issues = [json.loads(json.dumps(i)) for i in issues]

    def run_script(self, *args):
        self.github.calls = []
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(audit_issues.close_issue, "gh", self.github), \
                mock.patch.dict(os.environ, {"XDG_CACHE_HOME": str(self.cache)}), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = audit_issues.main([*args, "--repo", "example/app"])
        return Result(code, out.getvalue(), err.getvalue()), self.github.calls

    def draft(self):
        return self.run_script("draft", "--title", "Import drops rows", "--body-file", str(self.draft_body))

    def test_an_issue_edited_between_runs_is_read_as_edited(self):
        self.tracker(tracked(1, "2026-01-01T00:00:00Z", title="Sync stalls on large files", body="unrelated"),
                     tracked(2, "2026-01-02T00:00:00Z"))
        first, _ = self.draft()
        self.assertEqual(first.returncode, 0, first.stdout)
        self.tracker(tracked(1, "2026-01-03T00:00:00Z", title="Sync stalls on large files",
                             body="error: row 12 rejected by the server"),
                     tracked(2, "2026-01-02T00:00:00Z"))
        second, calls = self.draft()
        self.assertNotIn("full", calls)
        self.assertEqual(second.returncode, 1, second.stdout + second.stderr)
        self.assertIn("#1 Sync stalls on large files looks like the same cause", second.stdout)

    def test_a_deleted_issue_forces_a_full_resync(self):
        self.tracker(tracked(1, "2026-01-01T00:00:00Z"),
                     tracked(2, "2026-01-02T00:00:00Z", title="Export drops rows",
                             body="error: row 7 rejected by the server"))
        first, _ = self.draft()
        self.assertEqual(first.returncode, 1, first.stdout)
        self.tracker(tracked(1, "2026-01-01T00:00:00Z"))
        second, calls = self.draft()
        self.assertIn("full", calls)
        self.assertIn("1 issues", second.stderr)
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)

    def test_a_closed_sub_issue_updates_its_parents_view_of_it(self):
        # Closing #2 changes #2's updatedAt, not its parent's, so the parent's copy of its
        # sub-issue list is refreshed from the mirror's own record of #2.
        parent = {"number": 1, "title": "Issue 1", "url": "https://example.test/1", "state": "CLOSED"}
        closed_parent = {**tracked(1, "2026-01-01T00:00:00Z", state="CLOSED", reason="COMPLETED"),
                         "url": "https://example.test/1"}
        closed_parent["subIssues"]["nodes"] = [
            {"number": 2, "title": "Issue 2", "url": "https://example.test/2", "state": "OPEN"}]
        child = {**tracked(2, "2026-01-01T00:00:00Z", parent=parent), "url": "https://example.test/2"}
        self.tracker(closed_parent, child)
        first, _ = self.run_script("scan")
        self.assertEqual(first.returncode, 1, first.stdout)
        self.tracker(closed_parent, {**child, "state": "CLOSED", "stateReason": "COMPLETED",
                                     "updatedAt": "2026-01-05T00:00:00Z"})
        second, calls = self.run_script("scan")
        self.assertNotIn("full", calls)
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)

    def test_a_corrupt_mirror_is_reported_and_rebuilt(self):
        self.tracker(tracked(1, "2026-01-01T00:00:00Z"))
        self.mirror.parent.mkdir(parents=True)
        self.mirror.write_text("{not json")
        result, calls = self.draft()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(str(self.mirror), result.stderr)
        self.assertIn("Expecting property name", result.stderr)
        self.assertIn("full", calls)
        self.assertEqual(list(json.loads(self.mirror.read_text())["issues"]), ["1"])


class StandInTracker(StandInGitHub):
    """Also answers single-issue reads, body edit history, edits and closes, for apply and
    close-issues alike. Each edit keeps the earlier body, as GitHub's edit history does."""

    def __call__(self, *args, stdin=None):
        by_number = {i["number"]: i for i in self.issues}
        match args[:2]:
            case ("issue", "edit"):
                item = by_number[int(args[2])]
                item.setdefault("history", [item["body"]]).insert(0, stdin)
                item["body"] = stdin
                return ""
            case ("issue", "close"):
                reason = args[args.index("--reason") + 1]
                by_number[int(args[2])].update(
                    state="CLOSED", stateReason={"completed": "COMPLETED"}.get(reason, "NOT_PLANNED"))
                return ""
            case ("api", "graphql"):
                values = dict(a.split("=", 1) for flag, a in zip(args, args[1:]) if flag in ("-f", "-F"))
                if "issue(number" in values["query"]:
                    item = by_number[int(values["number"])]
                    if "userContentEdits" in values["query"]:
                        edits = {"nodes": [{"diff": text} for text in item.get("history", [])],
                                 "pageInfo": {"hasNextPage": False, "endCursor": None}}
                        return json.dumps({"data": {"repository": {"issue": {"userContentEdits": edits}}}})
                    fields = {k: v for k, v in item.items() if k != "history"}
                    return json.dumps({"data": {"repository": {"issue": fields}}})
        return super().__call__(*args, stdin=stdin)


class ApplyLineFates(unittest.TestCase):
    """apply settles each open line of a closing issue the way its page said, so close-issues
    accepts the close."""

    def setUp(self):
        folder = tempfile.TemporaryDirectory(prefix="audit-issues-test-")
        self.addCleanup(folder.cleanup)
        self.folder = Path(folder.name)
        self.github = StandInTracker()
        cause_body = "## Outcome\n\nRows survive a sync.\n\n## Done when\n\n- [ ] keep-rows: Keep rows\n"
        self.github.issues = [
            tracked(1, "2026-01-01T00:00:00Z", title="Sync loses rows", body=cause_body, milestone=None),
            tracked(2, "2026-01-01T00:00:00Z", milestone=None, body=(
                "Old importer.\n\n## Done when\n\n- [ ] order: Keep row order\n"
                "- [ ] Write the import guide\n- [ ] colour: Colour the progress bar\n")),
            tracked(3, "2026-01-01T00:00:00Z", milestone=None,
                    body="## Done when\n\n- [ ] retry: Retry a failed row\n"),
        ]
        self.plan = self.folder / "plan.json"
        self.plan.write_text(json.dumps(plan_of({
            1: {"verdict": "still-real", "evidence": "reproduced"},
            2: {"verdict": "out-of-date", "evidence": "0.2 replaced the importer", "lines": {
                "order": {"moved": 1},
                "Write the import guide": {"moved": 1, "id": "import-guide"},
                "colour": {"dropped": "the progress bar is gone"}}},
            3: {"verdict": "done", "proof": ["c0ffee1 rows go through the shared writer"], "lines": {
                "retry": {"dropped": "the shared writer never fails a row"}}},
        })))

    def run_script(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(audit_issues.close_issue, "gh", self.github), \
                mock.patch.object(audit_issues.close_issue, "landed_commits", lambda args, number: []), \
                mock.patch.dict(os.environ, {"XDG_CACHE_HOME": str(self.folder / "cache")}), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = audit_issues.main([*args, "--repo", "example/app"])
        return Result(code, out.getvalue(), err.getvalue())

    def body(self, number):
        return next(i for i in self.github.issues if i["number"] == number)["body"]

    def test_apply_moves_and_drops_open_lines_then_closes_on_the_first_run(self):
        code = audit_issues.approval_code([self.plan.read_bytes()])
        first = self.run_script("apply", "--plan", str(self.plan), "--approved", code)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        states = {i["number"]: (i["state"], i["stateReason"]) for i in self.github.issues}
        self.assertEqual(states, {1: ("OPEN", None), 2: ("CLOSED", "NOT_PLANNED"), 3: ("CLOSED", "COMPLETED")})
        self.assertIn("- [ ] keep-rows: Keep rows\n- [ ] order: Keep row order (was #2)\n"
                      "- [ ] import-guide: Write the import guide (was #2)\n", self.body(1))
        self.assertNotIn("[ ]", self.body(2))
        self.assertIn("## Checklist changes\n\n- order: moved to #1\n- Write the import guide: moved to #1\n"
                      "- colour: dropped, the progress bar is gone\n", self.body(2))
        self.assertIn("- retry: dropped, the shared writer never fails a row", self.body(3))
        for number in (2, 3):
            ready = io.StringIO()
            with mock.patch.object(audit_issues.close_issue, "gh", self.github), \
                    mock.patch.object(audit_issues.close_issue, "landed_commits", lambda args, n: []), \
                    contextlib.redirect_stdout(ready):
                self.assertEqual(audit_issues.close_issue.main(
                    ["ready", "--repo", "example/app", "--issue", str(number)]), 0, ready.getvalue())
        bodies = [self.body(n) for n in (1, 2, 3)]
        second = self.run_script("apply", "--plan", str(self.plan), "--approved", code)
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertEqual([self.body(n) for n in (1, 2, 3)], bodies)


if __name__ == "__main__":
    unittest.main()
