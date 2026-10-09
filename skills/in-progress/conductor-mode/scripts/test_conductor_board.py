"""Run `conductor_board.py check-in` at its command line against recorded GitHub and herdr responses.

`board_fixtures/bin` puts stand-ins for `gh` and `herdr` first on PATH; they
replay responses recorded from a real repository (redacted, see replay.py).
git is real: each test builds a checkout whose worktrees the board reads.
Codex threads are rollouts under a test CODEX_HOME, built from the lines of
real rollouts that board_fixtures/record_rollouts.py recorded; the directories
their tool calls name are moved from ~/dev to the test's root.
"""

from datetime import datetime
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "conductor_board.py"
FIXTURES = HERE / "board_fixtures"
REPO = "example-org/example-app"
PR_LIST = ("gh_pr_list_repo_example_org_example_app_state_open_limit_500_json_number_title_isDraft_headRefOid_"
           "closingIssuesReferences_statusCheckRollup_reviews")
PASSED_PR, PENDING_PR, FAILED_PR = 1288, 1289, 1285
DESKTOP_CONDUCTOR = "01a117b0-3760-7061-b886-57e213128bd8"
DESKTOP_RUNNING = "01a117b9-0986-7093-9e2b-62937838f0bc"
DESKTOP_MOVED = "01a117b3-2e94-71a2-8464-af65d33acda4"
DESKTOP_COMPLETE = "01a117b1-f8cf-7cc0-a32f-6772965fb745"
TUI_RUNNING = "01a1191d-d8f3-7a40-9de5-495916fdf3bb"
TUI_COMPLETE_THEN_SETTINGS = "01a11607-71fb-7282-8924-ed187ea62ce9"


def git(cwd, *arguments):
    subprocess.run(["git", "-C", str(cwd), *arguments], check=True, capture_output=True)


class CheckInTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="board-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.responses = self.root / "responses"
        shutil.copytree(FIXTURES / "responses", self.responses)
        self.checkout = self.root / "example-app"
        self.checkout.mkdir()
        git(self.checkout, "init", "-q", "-b", "main")
        git(self.checkout, "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-q", "--allow-empty",
            "-m", "start")
        git(self.checkout, "remote", "add", "origin", f"https://github.com/{REPO}.git")
        self.agents = []
        self.settings(max_implementers=9)

    def settings(self, max_implementers):
        folder = self.root / "config" / "checkpickerupper"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "conductor-mode.toml").write_text(f"max_implementers = {max_implementers}\n")

    def response(self, key):
        return self.responses / f"{key}.json"

    def edit(self, key, change):
        path = self.response(key)
        recorded = json.loads(path.read_text())
        change(recorded["stdout"])
        path.write_text(json.dumps(recorded))

    def sub_issues(self, parent):
        return f"gh_api_paginate_slurp_repos_example_org_example_app_issues_{parent}_sub_issues_per_page_100"

    def blocked_by(self, number):
        return f"gh_api_paginate_slurp_repos_example_org_example_app_issues_{number}_dependencies_blocked_by_per_page_100"

    def set_body(self, parent, number, body):
        def change(pages):
            [issue] = [issue for page in pages for issue in page if issue["number"] == number]
            issue["body"] = body
        self.edit(self.sub_issues(parent), change)

    def reopen_blocker(self, number, blocker):
        def change(pages):
            [edge] = [edge for page in pages for edge in page if edge["number"] == blocker]
            edge["state"], edge["closed_at"] = "open", None
        self.edit(self.blocked_by(number), change)

    def point_pr_at(self, pr_number, issue, **fields):
        def change(prs):
            [pr] = [pr for pr in prs if pr["number"] == pr_number]
            pr["closingIssuesReferences"][0]["number"] = issue
            pr.update(fields)
        self.edit(PR_LIST, change)

    def worktree(self, name, branch, status=None, pane="wQ:p6", codex_thread=None):
        path = self.root / name
        git(self.checkout, "worktree", "add", "-q", "-b", branch, str(path))
        if status is not None:
            template = json.loads((FIXTURES / "responses" / "herdr_agent_list.json").read_text())
            row = template["stdout"]["result"]["agents"][0]
            if codex_thread is not None:
                row = {**row, "agent": "codex", "agent_session": {"agent": "codex", "kind": "id",
                                                                  "source": "herdr:codex", "value": codex_thread}}
            self.agents.append({**row, "pane_id": pane, "cwd": str(path / "src"), "foreground_cwd": str(path),
                                "agent_status": status})
        return path

    def rollout(self, thread, cwd, minutes_ago=0):
        [recorded] = (FIXTURES / "rollouts").glob(f"*-{thread}.jsonl")
        rows = [json.loads(line) for line in recorded.read_text().splitlines()]
        rows[0]["payload"]["cwd"] = str(cwd)
        for row in rows[1:]:
            payload = row.get("payload", {})
            for carrier in ("input", "arguments"):
                if carrier in payload:
                    payload[carrier] = payload[carrier].replace("~/dev/", f"{self.root}/")
        today = datetime.now()
        path = self.root / "codex" / "sessions" / f"{today:%Y/%m/%d}" / f"rollout-{today:%Y-%m-%d}T00-00-00-{thread}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(json.dumps(row) + "\n" for row in rows))
        written = time.time() - minutes_ago * 60
        os.utime(path, (written, written))

    def check_in(self, *effort, as_json=False):
        self.edit("herdr_agent_list", lambda listed: listed["result"].update(agents=self.agents))
        env = {**os.environ, "PATH": f"{FIXTURES / 'bin'}{os.pathsep}{os.environ['PATH']}",
               "BOARD_RESPONSES": str(self.responses), "XDG_CONFIG_HOME": str(self.root / "config"),
               "CODEX_HOME": str(self.root / "codex")}
        env.pop("HERDR_PANE_ID", None)
        env.pop("CODEX_THREAD_ID", None)
        env.pop("BOARD_RECORD", None)
        arguments = [sys.executable, str(SCRIPT), "check-in", "--repo", REPO, *(effort or ("--parent", "1266")),
                     "--checkout", str(self.checkout), *(["--json"] if as_json else [])]
        return subprocess.run(arguments, env=env, capture_output=True, text=True, timeout=60)

    def board(self, command, *arguments):
        self.edit("herdr_agent_list", lambda listed: listed["result"].update(agents=self.agents))
        env = {**os.environ, "PATH": f"{FIXTURES / 'bin'}{os.pathsep}{os.environ['PATH']}",
               "BOARD_RESPONSES": str(self.responses), "XDG_CONFIG_HOME": str(self.root / "config"),
               "CODEX_HOME": str(self.root / "codex")}
        for name in ("HERDR_PANE_ID", "CODEX_THREAD_ID", "BOARD_RECORD"):
            env.pop(name, None)
        return subprocess.run([sys.executable, str(SCRIPT), command, "--repo", REPO, "--checkout", str(self.checkout),
                               *map(str, arguments)], env=env, capture_output=True, text=True, timeout=60)

    def shown(self, name):
        return str(self.root / name).replace(str(Path.home()), "~", 1)

    def lines(self, done, kind):
        return [line for line in done.stdout.splitlines() if line.startswith(f"{kind}: ")]

    def ready(self, done):
        return [int(line.split("#")[1].split()[0]) for line in self.lines(done, "ready")]

    def test_closed_blocker_is_stale_its_issue_is_ready_and_each_rule_prints_once(self):
        done = self.check_in()
        self.assertEqual(done.returncode, 1, done.stderr)
        stale = self.lines(done, "stale-blocker")
        self.assertIn("stale-blocker: #1187 Issue 1187 <- #1201 Issue 1201 (closed 2026-10-08)", stale)
        self.assertIn("stale-blocker: #820 Issue 820 <- #812 Issue 812 (closed 2026-10-01)", stale)
        self.assertEqual(len(stale), 6)
        self.assertEqual(done.stdout.count("rule (stale-blocker):"), 1)
        self.assertFalse([line for line in self.lines(done, "missing-reason") if "<- #812" in line or "<- #597" in line])
        self.assertIn(819, self.ready(done))
        self.assertNotIn(318, self.ready(done))

    def test_open_edge_on_issue_with_sub_issues_is_parent_blocker_unless_the_whole_issue_cannot_start(self):
        self.reopen_blocker(820, 812)
        self.set_body(1266, 820, "## Blocked by\n- #812 Scope: cannot meet \"queries run in scope\" until it lands, "
                                 "because nothing sets the scope yet.\n")
        done = self.check_in()
        self.assertEqual(self.lines(done, "parent-blocker"), [
            "parent-blocker: #820 Issue 820 <- #812 Issue 812 (issue has sub-issues; reason does not say the whole "
            "issue cannot start)"])
        self.assertFalse([line for line in self.lines(done, "missing-reason") if line.startswith("missing-reason: #820")])
        self.assertNotIn(820, self.ready(done))
        self.assertNotIn(1187, self.ready(done))

        self.set_body(1266, 820, "## Blocked by\n- #812 Scope: cannot start until it lands, because every query "
                                 "needs the scope.\n")
        self.assertEqual(self.lines(self.check_in(), "parent-blocker"), [])

    def test_reason_lines_are_matched_to_edges_within_their_section(self):
        self.set_body(1266, 878, "\n".join([
            "## Outcome", "- #822 Money: cannot start until it lands, because this line is before the section.",
            "## Blocked by",
            "- #820 Queries: cannot start until it lands, because the price query is rewritten there.",
            "- #999 Gone: cannot start until it lands, because it was never an edge."]))
        self.set_body(1266, 318, "\n".join([
            "## Blocked by", "- #814 Outbox: needs it first.",
            "## Done when", "- #820 Queries: cannot start until it lands, because this line is after the section."]))
        done = self.check_in()
        missing = [line for line in self.lines(done, "missing-reason") if line.startswith(("missing-reason: #878",
                                                                                          "missing-reason: #318"))]
        self.assertEqual(missing, [
            "missing-reason: #878 Issue 878 <- #822 Issue 822 (no reason line)",
            "missing-reason: #318 Issue 318 <- #820 Issue 820 (no reason line)",
            "missing-reason: #318 Issue 318 <- #814 Issue 814 (its reason line says no \"cannot\")"])
        self.assertEqual(self.lines(done, "orphan-reason"), [
            "orphan-reason: #878 Issue 878 <- #999 (reason line names no blocked-by edge)"])

    def move_blocker_to(self, number, blocker, repository):
        def change(pages):
            [edge] = [edge for page in pages for edge in page if edge["number"] == blocker]
            edge["repository_url"] = f"https://api.github.com/repos/{repository}"
            edge["html_url"] = f"https://github.com/{repository}/issues/{blocker}"
        self.edit(self.blocked_by(number), change)

    def test_a_blocker_in_another_repository_matches_only_its_qualified_reason_line(self):
        self.move_blocker_to(878, 820, "other-org/tools")
        self.set_body(1266, 878, "\n".join([
            "## Blocked by",
            "- other-org/tools#820 Tool: cannot start until it lands, because the build needs it.",
            "- #822 Money: cannot start until it lands, because the price query is rewritten there."]))
        done = self.check_in()
        self.assertFalse([line for line in self.lines(done, "missing-reason") if line.startswith("missing-reason: #878")],
                         done.stdout)
        self.assertFalse([line for line in self.lines(done, "orphan-reason") if line.startswith("orphan-reason: #878")],
                         done.stdout)

        # A local issue with the same number is a different issue: its line must not cover the other repository's.
        self.set_body(1266, 878, "\n".join([
            "## Blocked by",
            "- #820 Queries: cannot start until it lands, because the price query is rewritten there.",
            "- #822 Money: cannot start until it lands, because the price query is rewritten there."]))
        done = self.check_in()
        self.assertIn("missing-reason: #878 Issue 878 <- other-org/tools#820 Issue 820 (no reason line)",
                      self.lines(done, "missing-reason"))
        self.assertIn("orphan-reason: #878 Issue 878 <- #820 (reason line names no blocked-by edge)",
                      self.lines(done, "orphan-reason"))

    def test_ready_skips_issues_with_work_and_fills_only_free_slots(self):
        self.settings(max_implementers=2)
        self.worktree("example-app-1190-valuation", "codex/1190-valuation", status="working")
        self.point_pr_at(PASSED_PR, 819, isDraft=True)
        done = self.check_in()
        self.assertIn("slots: 1 running, max 2 -> 1 free, 2 ready", done.stdout)
        self.assertEqual(self.ready(done), [820])

        self.worktree("example-app-1187-persistence", "1187-persistence")
        self.assertEqual(self.ready(self.check_in()), [320])

    def test_review_is_due_until_a_review_is_recorded_on_the_head(self):
        self.point_pr_at(PASSED_PR, 1190)
        done = self.check_in()
        [line] = self.lines(done, "review")
        self.assertRegex(line, r"^review: PR #1288 Issue 1288 \(closes #1190\), checks passed on [0-9a-f]{7} \d+[mhd] "
                               r"ago, no review on this head$")
        self.assertNotIn(1190, self.ready(done))

        head = json.loads(self.response(PR_LIST).read_text())["stdout"]
        [pr] = [pr for pr in head if pr["number"] == PASSED_PR]
        self.point_pr_at(PASSED_PR, 1190, reviews=[{"state": "COMMENTED", "commit": {"oid": "0" * 40}}])
        self.assertEqual(len(self.lines(self.check_in(), "review")), 1)
        self.point_pr_at(PASSED_PR, 1190, reviews=[{"state": "COMMENTED", "commit": {"oid": pr["headRefOid"]}}])
        self.assertEqual(self.lines(self.check_in(), "review"), [])

    def test_review_waits_for_pending_checks_and_reports_failed_ones(self):
        self.point_pr_at(PENDING_PR, 1190)
        self.assertEqual(self.lines(self.check_in(), "review"), [])
        self.point_pr_at(FAILED_PR, 320)
        [line] = self.lines(self.check_in(), "review")
        self.assertIn("(closes #320), checks failed on", line)

    def test_idle_implementer_without_pr_is_reported_and_a_working_one_is_not(self):
        self.worktree("example-app-1190-valuation", "valuation", status="done")
        done = self.check_in()
        self.assertEqual(self.lines(done, "idle"), [
            f"idle: #1190 Issue 1190 (pane wQ:p6, worktree {self.shown('example-app-1190-valuation')}) "
            "agent_status done, no PR"])
        self.assertIn("slots: 1 running", done.stdout)

        self.agents[0]["agent_status"] = "working"
        self.assertEqual(self.lines(self.check_in(), "idle"), [])

    def test_idle_implementer_whose_pr_waits_on_review_is_not_idle(self):
        self.worktree("example-app-1190-valuation", "1190-valuation", status="done")
        self.point_pr_at(PASSED_PR, 1190)
        done = self.check_in()
        self.assertEqual(self.lines(done, "idle"), [])
        self.assertEqual(len(self.lines(done, "review")), 1)

    def test_worktree_naming_no_issue_is_unmapped_and_holds_a_slot(self):
        self.settings(max_implementers=1)
        self.worktree("example-app-lane-shared", "lane-shared", status="working")
        done = self.check_in()
        self.assertEqual(self.lines(done, "unmapped"), [
            f"unmapped: pane wQ:p6, worktree {self.shown('example-app-lane-shared')}, branch lane-shared: agent_status working, maps to no issue"])
        self.assertIn("slots: 1 running, max 1 -> 0 free", done.stdout)
        self.assertEqual(self.ready(done), [])

    def test_running_desktop_thread_takes_a_slot_and_the_thread_directing_it_does_not(self):
        self.settings(max_implementers=2)
        self.rollout(DESKTOP_CONDUCTOR, self.checkout)
        self.rollout(DESKTOP_RUNNING, self.checkout, minutes_ago=3)
        done = self.check_in()
        self.assertIn("slots: 1 running, max 2 -> 1 free", done.stdout)
        self.assertEqual(self.lines(done, "unmapped"), [
            f"unmapped: Codex Desktop thread {DESKTOP_RUNNING}, checkout {self.shown('example-app')}, branch main: "
            "turn running, maps to no issue"])
        self.assertEqual(len(self.ready(done)), 1)

        self.rollout(DESKTOP_RUNNING, self.checkout, minutes_ago=11)
        self.assertIn("slots: 0 running, max 2 -> 2 free", self.check_in().stdout)

    def test_thread_started_in_the_checkout_maps_to_the_worktree_its_commands_run_in(self):
        self.worktree("example-app-lane-signin", "codex/1190-better-auth-service")
        self.rollout(DESKTOP_RUNNING, self.checkout, minutes_ago=3)
        done = self.check_in()
        self.assertEqual(self.lines(done, "unmapped"), [])
        self.assertEqual(self.lines(done, "implementer"), [
            f"implementer: #1190 Issue 1190 (Codex Desktop thread {DESKTOP_RUNNING}, worktree "
            f"{self.shown('example-app-lane-signin')}, branch codex/1190-better-auth-service) turn running"])

    def test_thread_whose_commands_moved_between_worktrees_maps_to_the_latest_workdir(self):
        self.worktree("example-app-lane-shared", "codex/1187-idempotency-claim-binding")
        self.worktree("example-app-1284-program-only-server", "codex/1190-program-only-server")
        self.worktree("example-app-1287-fly-gate-runner", "820-fly-gate-runner")
        self.rollout(DESKTOP_MOVED, self.checkout, minutes_ago=3)
        self.assertEqual(self.lines(self.check_in(), "implementer"), [
            f"implementer: #1190 Issue 1190 (Codex Desktop thread {DESKTOP_MOVED}, worktree "
            f"{self.shown('example-app-1284-program-only-server')}, branch codex/1190-program-only-server) "
            "turn running"])

    def test_thread_whose_commands_name_no_worktree_stays_unmapped_in_the_checkout(self):
        self.worktree("example-app-lane", "1190-lane")
        self.rollout(DESKTOP_RUNNING, self.checkout, minutes_ago=3)
        self.assertEqual(self.lines(self.check_in(), "unmapped"), [
            f"unmapped: Codex Desktop thread {DESKTOP_RUNNING}, checkout {self.shown('example-app')}, branch main: "
            "turn running, maps to no issue"])

    def test_branch_number_wins_over_the_path_number_and_both_are_shown(self):
        self.worktree("example-app-1187-persistence", "codex/1190-valuation", status="done")
        self.assertEqual(self.lines(self.check_in(), "idle"), [
            f"idle: #1190 Issue 1190 (pane wQ:p6, worktree {self.shown('example-app-1187-persistence')}, "
            "branch codex/1190-valuation) agent_status done, no PR"])

    def test_ended_thread_in_an_issue_worktree_is_idle_until_its_pr_waits_on_review(self):
        valuation = self.worktree("example-app-1190-valuation", "1190-valuation")
        persistence = self.worktree("example-app-1187-persistence", "1187-persistence")
        self.rollout(DESKTOP_COMPLETE, valuation / "src", minutes_ago=30)
        self.rollout(TUI_COMPLETE_THEN_SETTINGS, persistence)
        done = self.check_in()
        self.assertEqual(self.lines(done, "idle"), [
            f"idle: #1187 Issue 1187 (codex-tui thread {TUI_COMPLETE_THEN_SETTINGS}, worktree "
            f"{self.shown('example-app-1187-persistence')}) task_complete 0m ago, no PR",
            f"idle: #1190 Issue 1190 (Codex Desktop thread {DESKTOP_COMPLETE}, worktree "
            f"{self.shown('example-app-1190-valuation')}) task_complete 30m ago, no PR"])
        self.assertIn("slots: 2 running", done.stdout)

        self.point_pr_at(PASSED_PR, 1190)
        self.assertEqual([line for line in self.lines(self.check_in(), "idle") if "#1190" in line], [])

    def test_thread_in_another_repository_is_ignored(self):
        self.settings(max_implementers=1)
        for name in ("example-app-other-repo", "dotfiles-1364-admission-shutdown"):
            (self.root / name).mkdir()
            self.rollout(TUI_RUNNING, self.root / name)
            done = self.check_in()
            self.assertIn("slots: 0 running, max 1 -> 1 free", done.stdout)
            self.assertEqual(self.lines(done, "unmapped"), [])

    def test_codex_thread_that_herdr_also_lists_counts_once(self):
        path = self.worktree("example-app-1190-valuation", "1190-valuation", status="working",
                             codex_thread=TUI_RUNNING)
        self.rollout(TUI_RUNNING, path)
        self.assertIn("slots: 1 running", self.check_in().stdout)

    def test_claim_check_passes_an_issue_nothing_holds(self):
        self.worktree("example-app-820-queries", "codex/820-queries", status="working")
        done = self.board("claim-check", 819)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(done.stdout.strip(), "free: #819 has no open PR, worktree or implementer")

    def test_claim_check_names_the_open_pr_that_closes_the_issue(self):
        done = self.board("claim-check", 858)
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(self.lines(done, "pr"), [f"pr: PR #{PASSED_PR} Issue {PASSED_PR} closes #858"])
        self.assertEqual(done.stdout.count("rule (claimed):"), 1)

    def test_claim_check_names_the_worktree_and_whoever_works_in_it(self):
        path = self.worktree("example-app-lane-queries", "codex/819-endpoint", status="done", pane="wQ:p9")
        self.rollout(DESKTOP_RUNNING, path)
        done = self.board("claim-check", 819)
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(self.lines(done, "worktree"),
                         [f"worktree: {self.shown('example-app-lane-queries')}, branch codex/819-endpoint"])
        self.assertEqual(self.lines(done, "implementer"), [
            "implementer: pane wQ:p9, agent_status done",
            f"implementer: Codex Desktop thread {DESKTOP_RUNNING}, last written 0m ago"])

    def test_claim_check_ignores_a_worktree_whose_number_only_contains_the_issue(self):
        self.worktree("example-app-8190-other", "codex/8190-other")
        self.assertEqual(self.board("claim-check", 819).returncode, 0)

    def branch_pr(self, branch, state, head, number=1285):
        """Record the answer GitHub gives for the PRs opened from one branch (shape captured from a real merged PR)."""
        argv = ["gh", "pr", "list", "--repo", REPO, "--state", "all", "--head", branch, "--limit", "5",
                "--json", "number,state,headRefOid,title"]
        key = re.sub(r"[^A-Za-z0-9]+", "_", " ".join(argv)).strip("_")
        found = [] if state is None else [{"headRefOid": head, "number": number, "state": state,
                                           "title": f"Issue {number}"}]
        self.response(key).write_text(json.dumps({"argv": argv, "stdout": found}))

    def head_of(self, path):
        return subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"], check=True, capture_output=True,
                              text=True).stdout.strip()

    def test_leftovers_lists_a_clean_worktree_whose_pr_merged_at_its_head(self):
        merged = self.worktree("example-app-1212-claims", "codex/1212-claims")
        self.branch_pr("codex/1212-claims", "MERGED", self.head_of(merged))
        still_open = self.worktree("example-app-819-endpoint", "codex/819-endpoint")
        self.branch_pr("codex/819-endpoint", "OPEN", self.head_of(still_open), number=1290)
        self.worktree("example-app-820-queries", "codex/820-queries")
        self.branch_pr("codex/820-queries", None, None)
        done = self.board("leftovers")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual([line for line in done.stdout.splitlines() if not line.startswith("  rule")],
                         [f"merged: {self.shown('example-app-1212-claims')}, branch codex/1212-claims, PR #1285 merged"])

    def test_leftovers_keeps_a_merged_worktree_that_still_holds_work(self):
        dirty = self.worktree("example-app-1212-claims", "codex/1212-claims")
        self.branch_pr("codex/1212-claims", "MERGED", self.head_of(dirty))
        (dirty / "notes.txt").write_text("not committed\n")
        ahead = self.worktree("example-app-819-endpoint", "codex/819-endpoint")
        self.branch_pr("codex/819-endpoint", "MERGED", self.head_of(ahead), number=1290)
        git(ahead, "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-q", "--allow-empty", "-m", "more")
        done = self.board("leftovers")
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(self.lines(done, "merged"), [])
        self.assertEqual(self.lines(done, "merged-with-local-work"), [
            f"merged-with-local-work: {self.shown('example-app-1212-claims')}, branch codex/1212-claims, PR #1285 "
            "merged, 1 uncommitted file",
            f"merged-with-local-work: {self.shown('example-app-819-endpoint')}, branch codex/819-endpoint, PR #1290 "
            "merged, 1 local commit the merged head does not contain"])

    def test_leftovers_counts_a_worktree_behind_its_merged_head_as_merged(self):
        behind = self.worktree("example-app-1212-claims", "codex/1212-claims")
        git(behind, "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-q", "--allow-empty", "-m", "pushed")
        self.branch_pr("codex/1212-claims", "MERGED", self.head_of(behind))
        git(behind, "reset", "-q", "--hard", "HEAD~1")
        done = self.board("leftovers")
        self.assertEqual(self.lines(done, "merged"), [
            f"merged: {self.shown('example-app-1212-claims')}, branch codex/1212-claims, PR #1285 merged"])
        self.assertEqual(self.lines(done, "merged-with-local-work"), [])

    def test_leftovers_reports_a_closed_unmerged_pr_and_exits_zero_when_nothing_is_left(self):
        dropped = self.worktree("example-app-1212-claims", "codex/1212-claims")
        self.branch_pr("codex/1212-claims", "CLOSED", self.head_of(dropped))
        done = self.board("leftovers")
        self.assertEqual(self.lines(done, "closed"), [
            f"closed: {self.shown('example-app-1212-claims')}, branch codex/1212-claims, PR #1285 closed without merging"])
        self.assertEqual(done.returncode, 1)
        self.branch_pr("codex/1212-claims", "OPEN", self.head_of(dropped))
        done = self.board("leftovers")
        self.assertEqual((done.returncode, done.stdout.strip()), (0, "no leftover worktrees"))

    # ---- land -------------------------------------------------------------------------------------------------

    PR_VIEW_FIELDS = "number,title,state,isDraft,mergeable,headRefOid,headRefName,baseRefName,statusCheckRollup"
    PASSED_CHECK = {"__typename": "CheckRun", "completedAt": "2026-10-08T17:28:18Z", "conclusion": "SUCCESS",
                    "name": "verify", "startedAt": "2026-10-08T17:28:03Z", "status": "COMPLETED",
                    "workflowName": "Pull request verification"}

    def respond(self, argv, **recorded):
        key = re.sub(r"[^A-Za-z0-9]+", "_", " ".join(argv)).strip("_")
        self.response(key).write_text(json.dumps({"argv": argv, **recorded}))
        self.response(key).with_suffix(".count").unlink(missing_ok=True)

    def calls(self, *prefix):
        log = self.responses / "calls.log"
        made = [json.loads(line) for line in log.read_text().splitlines()] if log.is_file() else []
        return [call for call in made if call[:len(prefix)] == list(prefix)]

    def pr_state(self, head, branch, **changes):
        return {"baseRefName": "main", "headRefName": branch, "headRefOid": head, "isDraft": False,
                "mergeable": "MERGEABLE", "number": 1285, "state": "OPEN", "statusCheckRollup": [self.PASSED_CHECK],
                "title": "Issue 1285", **changes}

    def landing(self, *states, methods=("squash",), queue=False, merge_exit=0):
        """Record what GitHub and herdr answer while PR 1285 lands: its state over time, the repository's merge
        methods, whether its base has a merge queue, and the merge call itself."""
        self.respond(["gh", "pr", "view", "1285", "--repo", REPO, "--json", self.PR_VIEW_FIELDS],
                     sequence=[{"stdout": state} for state in states])
        self.respond(["gh", "api", f"repos/{REPO}", "--jq",
                      "{allow_merge_commit,allow_squash_merge,allow_rebase_merge}"],
                     stdout={"allow_merge_commit": "merge" in methods, "allow_squash_merge": "squash" in methods,
                             "allow_rebase_merge": "rebase" in methods})
        owner, name = REPO.split("/")
        self.respond(["gh", "api", "graphql", "-f",
                      "query=query($o:String!,$n:String!,$b:String!){repository(owner:$o,name:$n)"
                      "{mergeQueue(branch:$b){id}}}", "-F", f"o={owner}", "-F", f"n={name}", "-F", "b=main"],
                     stdout={"data": {"repository": {"mergeQueue": {"id": "MQ_1"} if queue else None}}})
        self.respond(["herdr", "worktree", "list", "--cwd", str(self.checkout)],
                     stdout={"result": {"type": "worktree_list", "worktrees": []}})
        head = states[0]["headRefOid"]
        for flags in (["--squash"], ["--merge"], ["--rebase"], []):
            self.respond(["gh", "pr", "merge", "1285", "--repo", REPO, *flags, "--match-head-commit", head],
                         exit=merge_exit, stderr="merge refused by GitHub\n" if merge_exit else "")

    def land(self, *arguments):
        # A short wait, so a version that merges when it should refuse fails fast instead of polling for minutes.
        return self.board("land", 1285, "--base", "main", "--poll", 0, *(("--wait", 1) if "--wait" not in arguments else ()),
                          *arguments)

    def branches(self):
        return subprocess.run(["git", "-C", str(self.checkout), "branch", "--format=%(refname:short)"], check=True,
                              capture_output=True, text=True).stdout.split()

    def test_land_merges_at_the_checked_head_then_removes_the_worktree_and_branch(self):
        path = self.worktree("example-app-1212-claims", "codex/1212-claims")
        head = self.head_of(path)
        self.landing(self.pr_state(head, "codex/1212-claims"), self.pr_state(head, "codex/1212-claims", state="MERGED"))
        done = self.land()
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertEqual(self.calls("gh", "pr", "merge"),
                         [["gh", "pr", "merge", "1285", "--repo", REPO, "--squash", "--match-head-commit", head]])
        self.assertFalse(path.exists())
        self.assertNotIn("codex/1212-claims", self.branches())
        self.assertIn("merged: PR #1285 Issue 1285 at " + head[:7], done.stdout)

    def test_land_refuses_and_changes_nothing_when_the_pr_is_not_ready(self):
        path = self.worktree("example-app-1212-claims", "codex/1212-claims")
        head = self.head_of(path)
        pending = {**self.PASSED_CHECK, "status": "IN_PROGRESS", "conclusion": ""}
        failed = {**self.PASSED_CHECK, "conclusion": "FAILURE"}
        for changes, reason in (
                ({"baseRefName": "production"}, "refused: PR #1285 targets production, not main"),
                ({"isDraft": True}, "refused: PR #1285 is a draft"),
                ({"statusCheckRollup": [pending]}, "refused: checks are still running on " + head[:7]),
                ({"statusCheckRollup": [failed]}, "refused: checks failed on " + head[:7]),
                ({"mergeable": "CONFLICTING"}, "refused: GitHub reports the PR as CONFLICTING"),
                ({"state": "CLOSED"}, "refused: PR #1285 is closed without merging")):
            with self.subTest(reason=reason):
                self.landing(self.pr_state(head, "codex/1212-claims", **changes))
                done = self.land()
                self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
                self.assertIn(reason, done.stdout.splitlines())
                self.assertEqual(self.calls("gh", "pr", "merge"), [])
                self.assertTrue(path.exists())
                self.assertIn("codex/1212-claims", self.branches())

    def test_land_needs_a_method_when_the_repository_allows_several_and_uses_the_one_given(self):
        path = self.worktree("example-app-1212-claims", "codex/1212-claims")
        head = self.head_of(path)
        open_then_merged = (self.pr_state(head, "codex/1212-claims"),
                            self.pr_state(head, "codex/1212-claims", state="MERGED"))
        self.landing(*open_then_merged, methods=("squash", "rebase"))
        done = self.land()
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertIn("refused: this repository allows squash and rebase merges; pass --method", done.stdout.splitlines())
        self.assertEqual(self.calls("gh", "pr", "merge"), [])
        self.landing(*open_then_merged, methods=("squash", "rebase"))
        self.assertEqual(self.land("--method", "rebase").returncode, 0)
        self.assertEqual(self.calls("gh", "pr", "merge")[0][6:], ["--rebase", "--match-head-commit", head])

    def test_land_joins_a_merge_queue_without_a_method_and_cleans_up_nothing_until_merged(self):
        path = self.worktree("example-app-1212-claims", "codex/1212-claims")
        head = self.head_of(path)
        self.landing(self.pr_state(head, "codex/1212-claims"), queue=True)
        done = self.land("--wait", 0)
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        self.assertEqual(self.calls("gh", "pr", "merge"),
                         [["gh", "pr", "merge", "1285", "--repo", REPO, "--match-head-commit", head]])
        self.assertIn("queued: PR #1285 is not merged yet; run land again to finish. Nothing was cleaned up.",
                      done.stdout.splitlines())
        self.assertTrue(path.exists())
        self.assertIn("codex/1212-claims", self.branches())

    def test_land_on_a_merged_pr_only_cleans_up_and_keeps_a_worktree_that_holds_work(self):
        path = self.worktree("example-app-1212-claims", "codex/1212-claims")
        head = self.head_of(path)
        (path / "notes.txt").write_text("not committed\n")
        self.landing(self.pr_state(head, "codex/1212-claims", state="MERGED"))
        done = self.land()
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        self.assertEqual(self.calls("gh", "pr", "merge"), [])
        self.assertTrue(path.exists())
        self.assertIn("codex/1212-claims", self.branches())
        self.assertIn(f"kept: {self.shown('example-app-1212-claims')} holds 1 uncommitted file", done.stdout)
        (path / "notes.txt").unlink()
        self.landing(self.pr_state(head, "codex/1212-claims", state="MERGED"))
        self.assertEqual(self.land().returncode, 0)
        self.assertFalse(path.exists())
        self.assertNotIn("codex/1212-claims", self.branches())

    def test_land_stops_before_cleanup_when_the_merge_itself_fails(self):
        path = self.worktree("example-app-1212-claims", "codex/1212-claims")
        head = self.head_of(path)
        self.landing(self.pr_state(head, "codex/1212-claims"), self.pr_state(head, "codex/1212-claims", state="MERGED"),
                     merge_exit=1)
        done = self.land()
        self.assertEqual(done.returncode, 2, done.stdout + done.stderr)
        self.assertIn("merge refused by GitHub", done.stderr)
        self.assertTrue(path.exists())
        self.assertIn("codex/1212-claims", self.branches())

    def test_land_removes_a_herdr_workspace_through_herdr_and_checks_it_is_gone(self):
        path = self.worktree("example-app-1212-claims", "codex/1212-claims")
        head = self.head_of(path)
        self.landing(self.pr_state(head, "codex/1212-claims", state="MERGED"))
        self.respond(["herdr", "worktree", "list", "--cwd", str(self.checkout)],
                     stdout={"result": {"type": "worktree_list", "worktrees": [
                         {"branch": "codex/1212-claims", "open_workspace_id": "w9Z", "path": str(path)}]}})
        self.respond(["herdr", "worktree", "remove", "--workspace", "w9Z"], stdout={"result": {"type": "removed"}})
        done = self.land()
        self.assertEqual(self.calls("herdr", "worktree", "remove"), [["herdr", "worktree", "remove", "--workspace", "w9Z"]])
        # The stand-in removes nothing, so land must notice the checkout is still there and keep the branch.
        self.assertEqual(done.returncode, 2, done.stdout + done.stderr)
        self.assertIn("still exists", done.stderr)
        self.assertIn("codex/1212-claims", self.branches())

    def test_milestone_board_with_nothing_to_do_exits_zero(self):
        milestone = ("--milestone", "Milestone 3")
        done = self.check_in(*milestone)
        self.assertEqual((done.returncode, self.ready(done)), (1, [635]), done.stderr)
        self.worktree("example-app-635-walkthrough", "635-walkthrough", status="working")
        done = self.check_in(*milestone)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("nothing needs action", done.stdout)

    def test_json_carries_the_same_findings_and_their_rules(self):
        text = self.check_in()
        board = json.loads(self.check_in(as_json=True).stdout)
        self.assertEqual([finding["line"] for finding in board["findings"]],
                         [line for line in text.stdout.splitlines()
                          if not line.startswith(("slots:", "implementer:", "  rule"))])
        self.assertEqual(set(board["rules"]), {finding["kind"] for finding in board["findings"]})

    def test_failed_read_exits_two_and_names_the_read(self):
        self.response(self.blocked_by(878)).unlink()
        done = self.check_in()
        self.assertEqual(done.returncode, 2)
        self.assertIn("read failed: blocked-by edges of #878", done.stderr)
        self.assertEqual(done.stdout, "")

    def test_checkout_of_another_repository_is_a_read_failure(self):
        git(self.checkout, "remote", "set-url", "origin", "https://github.com/example-org/other-app.git")
        done = self.check_in()
        self.assertEqual(done.returncode, 2)
        self.assertIn("read failed: checkout origin", done.stderr)


if __name__ == "__main__":
    unittest.main()
