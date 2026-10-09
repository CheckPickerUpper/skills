"""Read an effort's board from GitHub, git, herdr and Codex, and print what needs action.

`check-in` reads the effort's open issues (sub-issues of --parent, recursively,
or the open issues of --milestone), their native blocked-by edges and
`## Blocked by` reason lines, the repository's open PRs, the herdr agents
running in the checkout's worktrees, and the Codex threads (Desktop, TUI and
exec, which herdr does not list) whose rollouts start in the checkout or one of
its worktrees, fresh on every run. A thread works in the worktree its latest
tool call names, not where it started. It prints one line per finding plus, once per
kind, the rule that says what to do about it.
Exit 0: nothing needs action. Exit 1: something does. Exit 2: a read failed.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import NoReturn

import conductor_config

EXIT_CLEAR, EXIT_ACTION, EXIT_READ_FAILED = 0, 1, 2
READ_WORKERS = 8
PASSED_CONCLUSIONS = {"SUCCESS", "NEUTRAL", "SKIPPED"}
PENDING_STATES = {"PENDING", "EXPECTED", "QUEUED", "IN_PROGRESS", "WAITING", "REQUESTED"}
WORKING_STATUS = "working"
CODEX_RUNNING_WINDOW = timedelta(minutes=10)
CODEX_TURN_STARTED = "task_started"
CODEX_TURN_ENDED = {"task_complete", "turn_aborted"}

BLOCKED_BY_HEADING = re.compile(r"^##\s+Blocked by\s*$", re.IGNORECASE)
ANY_HEADING = re.compile(r"^#{1,6}\s")
# "- #N ..." names an issue in the effort's repository; "- owner/repo#N ..." names one in another repository.
REASON_LINE = re.compile(r"^- (?:([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+))?#(\d+)\b")
WHOLE_ISSUE_CANNOT_START = re.compile(r"\bcannot start(?: at all)?(?:\s+until\b|[.,;:]|$)", re.IGNORECASE)
NUMBER_TOKEN = re.compile(r"(?<![0-9])[0-9]+(?![0-9])")
PATH_END = r"""(?=$|[/\s"'`;,:)}\]\\])"""

RULES = {
    "stale-blocker": "A closed issue blocks nothing: remove the edge and its reason line, then start the issue.",
    "parent-blocker": "A blocker on an issue with sub-issues holds every piece under it: move the edge down to the "
                      "sub-issue that truly needs it, unless its reason says the whole issue \"cannot start until it lands\".",
    "missing-reason": "Every blocked-by edge needs a \"- #N <title>: cannot ... until it lands, because ...\" line under "
                      "\"## Blocked by\" in the blocked issue's body (\"- owner/repo#N\" for a blocker in another "
                      "repository): record it, or drop the edge when no such reason exists.",
    "orphan-reason": "A reason line must name a native blocked-by edge: add the edge when the block is real, "
                     "otherwise delete the line.",
    "ready": "Start this issue now; the board lists at most as many as there are free slots under max_implementers.",
    "review": "Review this PR's head and record the result as a PR review on that commit (gh pr review), "
              "which clears this line.",
    "idle": "This implementer is not working and has no PR waiting on you: prompt it with its next step, or release it.",
    "unmapped": "A worktree whose branch and path name no issue cannot be tracked: put the issue number in its branch, "
                "or release the agent and remove the worktree when its work is done.",
}
KIND_ORDER = tuple(RULES)


class ReadFailed(Exception):
    def __init__(self, read: str, detail: str):
        super().__init__(f"{read}: {detail}")
        self.read = read


@dataclass(frozen=True)
class Ref:
    number: int
    title: str
    # None for an issue in the effort's own repository; "owner/name" for one in another repository.
    repository: str | None = None

    def __str__(self) -> str:
        return f"{self.repository or ''}#{self.number} {self.title}"


@dataclass(frozen=True)
class Edge:
    blocker: Ref
    closed_at: str | None


@dataclass
class Issue:
    ref: Ref
    body: str
    has_sub_issues: bool
    blocked_by_total: int
    parent: int | None
    children: list[int] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)


@dataclass(frozen=True)
class Worktree:
    path: str
    branch: str
    issue: int | None


@dataclass(frozen=True)
class CodexThread:
    id: str
    works_in: str
    originator: str
    parent: str | None
    written: datetime
    last_turn_event: str | None


@dataclass(frozen=True)
class Implementer:
    place: str
    worktree: Worktree
    working: bool
    status: str
    detail: dict


@dataclass(frozen=True)
class Finding:
    kind: str
    line: str
    issue: int | None
    detail: dict


def run_json(argv: list[str], read: str) -> object:
    try:
        done = subprocess.run(argv, capture_output=True, text=True)
    except OSError as error:
        raise ReadFailed(read, f"{argv[0]} could not run: {error}") from error
    if done.returncode != 0:
        raise ReadFailed(read, f"`{' '.join(argv)}` exited {done.returncode}: {done.stderr.strip()}")
    try:
        return json.loads(done.stdout)
    except json.JSONDecodeError as error:
        raise ReadFailed(read, f"`{' '.join(argv)}` printed no JSON: {error}") from error


def run_text(argv: list[str], read: str) -> str:
    try:
        done = subprocess.run(argv, capture_output=True, text=True)
    except OSError as error:
        raise ReadFailed(read, f"{argv[0]} could not run: {error}") from error
    if done.returncode != 0:
        raise ReadFailed(read, f"`{' '.join(argv)}` exited {done.returncode}: {done.stderr.strip()}")
    return done.stdout


def gh_pages(path: str, read: str) -> list[dict]:
    pages = run_json(["gh", "api", "--paginate", "--slurp", path], read)
    return [item for page in pages for item in page]


def parent_number(raw: dict) -> int | None:
    url = raw.get("parent_issue_url")
    return int(url.rsplit("/", 1)[1]) if url else None


def issue_from(raw: dict) -> Issue:
    subs = raw.get("sub_issues_summary") or {}
    deps = raw.get("issue_dependencies_summary")
    return Issue(
        ref=Ref(raw["number"], raw["title"]),
        body=raw.get("body") or "",
        has_sub_issues=subs.get("total", 0) > 0,
        # Without a summary the edges are unknown, so they are read rather than assumed absent.
        blocked_by_total=deps["total_blocked_by"] if deps else -1,
        parent=parent_number(raw),
    )


def read_parent_effort(repo: str, parent: int) -> tuple[dict[int, Issue], list[int]]:
    issues: dict[int, Issue] = {}

    def children_of(number: int) -> list[dict]:
        return gh_pages(f"repos/{repo}/issues/{number}/sub_issues?per_page=100", f"sub-issues of #{number}")

    level = [parent]
    roots: list[int] = []
    with ThreadPoolExecutor(READ_WORKERS) as pool:
        while level:
            next_level = []
            for number, raws in zip(level, pool.map(children_of, level)):
                # A sub-issue in another repository has no edges, PRs or worktrees on this board.
                open_children = [raw for raw in raws if raw["state"] == "open"
                                 and raw["repository_url"].lower().endswith(f"/repos/{repo.lower()}")]
                for raw in open_children:
                    issue = issue_from(raw)
                    issue.parent = number
                    issues[issue.ref.number] = issue
                    if issue.has_sub_issues:
                        next_level.append(issue.ref.number)
                ids = [raw["number"] for raw in open_children]
                if number == parent:
                    roots = ids
                else:
                    issues[number].children = ids
            level = next_level
    return issues, roots


def read_milestone_effort(repo: str, title: str) -> tuple[dict[int, Issue], list[int]]:
    milestones = gh_pages(f"repos/{repo}/milestones?state=all&per_page=100", "milestones")
    numbers = [m["number"] for m in milestones if m["title"] == title]
    if not numbers:
        raise ReadFailed("milestones", f"{repo} has no milestone titled {title!r}")
    raws = gh_pages(f"repos/{repo}/issues?milestone={numbers[0]}&state=open&per_page=100",
                    f"open issues in milestone {title!r}")
    issues = {raw["number"]: issue_from(raw) for raw in raws if "pull_request" not in raw}
    roots = []
    for number, issue in issues.items():
        if issue.parent in issues:
            issues[issue.parent].children.append(number)
        else:
            roots.append(number)
    return issues, roots


def read_edges(repo: str, issues: dict[int, Issue]) -> None:
    wanted = [issue for issue in issues.values() if issue.blocked_by_total != 0]

    def edges_of(issue: Issue) -> list[dict]:
        return gh_pages(f"repos/{repo}/issues/{issue.ref.number}/dependencies/blocked_by?per_page=100",
                        f"blocked-by edges of #{issue.ref.number}")

    with ThreadPoolExecutor(READ_WORKERS) as pool:
        for issue, raws in zip(wanted, pool.map(edges_of, wanted)):
            issue.edges = [Edge(Ref(raw["number"], raw["title"], other_repository(raw["repository_url"], repo)),
                                raw["closed_at"] if raw["state"] == "closed" else None) for raw in raws]


def other_repository(repository_url: str, repo: str) -> str | None:
    """The blocker's "owner/name" when it lives outside the effort's repository, otherwise None."""
    owner_name = repository_url.rstrip("/").split("/repos/", 1)[1]
    return None if owner_name.lower() == repo.lower() else owner_name


def read_prs(repo: str) -> list[dict]:
    fields = "number,title,isDraft,headRefOid,closingIssuesReferences,statusCheckRollup,reviews"
    return run_json(["gh", "pr", "list", "--repo", repo, "--state", "open", "--limit", "500", "--json", fields],
                    "open PRs")


def read_worktrees(checkout: str, repo: str) -> tuple[Worktree, list[Worktree]]:
    origin = run_text(["git", "-C", checkout, "remote", "get-url", "origin"], "checkout origin").strip()
    if not re.search(rf"[:/]{re.escape(repo)}(\.git)?/?$", origin):
        raise ReadFailed("checkout origin", f"{checkout} is a clone of {origin}, not {repo}; pass --checkout")
    porcelain = run_text(["git", "-C", checkout, "worktree", "list", "--porcelain"], "git worktrees")
    entries = []
    for block in porcelain.strip().split("\n\n"):
        values = dict(line.split(" ", 1) for line in block.splitlines() if " " in line)
        entries.append((values["worktree"], values.get("branch", "").removeprefix("refs/heads/")))
    # The first entry is the primary checkout, which maps to no issue.
    return Worktree(*entries[0], None), [Worktree(path, branch, None) for path, branch in entries[1:]]


def path_numbers(worktree: Worktree, primary: str) -> list[int]:
    return [int(token) for token in NUMBER_TOKEN.findall(Path(worktree.path).name.removeprefix(Path(primary).name))]


def issue_for(worktree: Worktree, primary: str, effort: dict[int, Issue]) -> int | None:
    # The branch is what is checked out now; a worktree's path keeps the name of whatever it was made for.
    for candidates in ([int(token) for token in NUMBER_TOKEN.findall(worktree.branch)],
                       path_numbers(worktree, primary)):
        if candidates:
            return next((number for number in candidates if number in effort), candidates[0])
    return None


def read_agents() -> list[dict]:
    listed = run_json(["herdr", "agent", "list"], "herdr agents")
    return listed["result"]["agents"]


def strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for item in value.values() for text in strings(item)]
    if isinstance(value, list):
        return [text for item in value for text in strings(item)]
    return []


def directory_named(payload: dict, worktree_path: re.Pattern) -> str | None:
    """The worktree a tool call runs in: its last `workdir` inside one, else the last worktree it names."""
    workdirs, named = [], []
    for text in strings(payload):
        for match in worktree_path.finditer(text):
            named.append(match.group("root"))
            if match.group("workdir"):
                workdirs.append(match.group("root"))
    return (workdirs or named or [None])[-1]


def read_rollout(path: Path, worktree_path: re.Pattern) -> tuple[str | None, str | None]:
    """Return the rollout's last turn event and the worktree its latest tool call ran in."""
    turn, works_in = None, None
    with path.open(encoding="utf-8", errors="replace") as rollout:
        for line in rollout:
            is_turn = '"task_' in line or '"turn_aborted"' in line
            if not is_turn and '_call"' not in line:
                continue
            try:
                payload = json.loads(line).get("payload")
            except json.JSONDecodeError:
                # The thread may be writing this line right now.
                continue
            kind = payload.get("type") if isinstance(payload, dict) else None
            if kind == CODEX_TURN_STARTED or kind in CODEX_TURN_ENDED:
                turn = kind
            elif isinstance(kind, str) and kind.endswith("_call"):
                works_in = directory_named(payload, worktree_path) or works_in
    return turn, works_in


def read_codex_threads(roots: list[str], since: datetime) -> list[CodexThread]:
    """Read every Codex rollout written since `since` whose thread started in one of `roots`.

    Rollouts are selected by when they were last written, not by their date
    folder, because a resumed thread keeps appending to the file of the day it started.
    A thread works in the root its latest tool call names, falling back to where it started.
    """
    # Longest first, so a worktree whose path extends the checkout's is not read as the checkout.
    alternatives = "|".join(re.escape(root.rstrip("/")) for root in sorted(roots, key=len, reverse=True))
    worktree_path = re.compile(rf"""(?P<workdir>workdir"?\s*:\s*")?(?P<root>{alternatives}){PATH_END}""")
    sessions = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex") / "sessions"
    threads = []
    for path in sorted(sessions.glob("*/*/*/rollout-*.jsonl")):
        try:
            written = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
            if written < since:
                continue
            with path.open(encoding="utf-8", errors="replace") as rollout:
                first = json.loads(rollout.readline())
        except (OSError, json.JSONDecodeError):
            # A rollout that vanished or has no complete first line yet names no thread to count.
            continue
        meta = first.get("payload") if first.get("type") == "session_meta" else None
        if not isinstance(meta, dict) or not any(under(meta.get("cwd", ""), root) for root in roots):
            continue
        source = meta.get("source")
        spawn = source.get("subagent", {}).get("thread_spawn", {}) if isinstance(source, dict) else {}
        try:
            turn, works_in = read_rollout(path, worktree_path)
        except OSError as error:
            raise ReadFailed("Codex rollouts", f"{path} could not be read: {error}") from error
        threads.append(CodexThread(meta["id"], works_in or meta["cwd"], meta.get("originator", "codex"),
                                   spawn.get("parent_thread_id"), written, turn))
    return threads


def read_max_implementers(checkout: str) -> int:
    try:
        settings, _, _ = conductor_config.resolve(checkout)
    except SystemExit as error:
        raise ReadFailed("conductor settings", str(error)) from error
    if "max_implementers" not in settings:
        raise ReadFailed("conductor settings", "max_implementers is not set; run conductor_config.py show")
    return settings["max_implementers"]


BlockerKey = tuple[str, int]


def blocker_key(repository: str | None, number: int, repo: str) -> BlockerKey:
    """Same-numbered issues in two repositories are different issues, so a key carries both."""
    return (repository or repo).lower(), number


def reason_lines(body: str, repo: str) -> dict[BlockerKey, str]:
    lines: dict[BlockerKey, str] = {}
    inside = False
    for line in body.splitlines():
        stripped = line.strip()
        if BLOCKED_BY_HEADING.match(stripped):
            inside = True
        elif ANY_HEADING.match(stripped):
            inside = False
        elif inside and (match := REASON_LINE.match(stripped)):
            lines.setdefault(blocker_key(match.group(1), int(match.group(2)), repo), stripped)
    return lines


def blocker_findings(issue: Issue, repo: str) -> list[Finding]:
    findings = []
    lines = reason_lines(issue.body, repo)
    edge_keys = {blocker_key(edge.blocker.repository, edge.blocker.number, repo) for edge in issue.edges}
    for edge in issue.edges:
        pair = f"{issue.ref} <- {edge.blocker}"
        detail = {"blocker": edge.blocker.number, "blocker_title": edge.blocker.title}
        if edge.blocker.repository:
            detail["blocker_repository"] = edge.blocker.repository
        if edge.closed_at is not None:
            findings.append(Finding("stale-blocker", f"{pair} (closed {edge.closed_at[:10]})", issue.ref.number,
                                    {**detail, "closed_at": edge.closed_at}))
            continue
        line = lines.get(blocker_key(edge.blocker.repository, edge.blocker.number, repo))
        valid = line is not None and "cannot" in line
        if not valid:
            why = "no reason line" if line is None else "its reason line says no \"cannot\""
            findings.append(Finding("missing-reason", f"{pair} ({why})", issue.ref.number, detail))
        if issue.has_sub_issues and not (valid and WHOLE_ISSUE_CANNOT_START.search(line)):
            findings.append(Finding("parent-blocker", f"{pair} (issue has sub-issues; reason does not say "
                                    "the whole issue cannot start)", issue.ref.number, detail))
    for key in sorted(set(lines) - edge_keys):
        repository, number = key
        named = f"#{number}" if repository == repo.lower() else f"{repository}#{number}"
        findings.append(Finding("orphan-reason", f"{issue.ref} <- {named} (reason line names no blocked-by edge)",
                                issue.ref.number, {"named": number, "reason_line": lines[key]}))
    return findings


def check_state(pr: dict) -> tuple[str, str]:
    """Return (outcome, latest completion time) for the head's checks: passed, pending, failed or none."""
    rollup = pr.get("statusCheckRollup") or []
    if not rollup:
        return "none", ""
    outcomes, times = [], []
    for check in rollup:
        if check.get("__typename") == "StatusContext":
            state = check.get("state", "")
            outcomes.append("pending" if state in PENDING_STATES else "passed" if state == "SUCCESS" else "failed")
            times.append(check.get("startedAt") or "")
        elif check.get("status") != "COMPLETED":
            outcomes.append("pending")
        else:
            outcomes.append("passed" if check.get("conclusion") in PASSED_CONCLUSIONS else "failed")
            times.append(check.get("completedAt") or "")
    for outcome in ("pending", "failed"):
        if outcome in outcomes:
            return outcome, max(times, default="")
    return "passed", max(times, default="")


def ago(stamp: str, now: datetime) -> str:
    if not stamp:
        return ""
    minutes = int((now - datetime.fromisoformat(stamp.replace("Z", "+00:00"))).total_seconds() // 60)
    if minutes < 60:
        return f" {minutes}m ago"
    return f" {minutes // 60}h ago" if minutes < 48 * 60 else f" {minutes // 1440}d ago"


def reviewed_on_head(pr: dict) -> bool:
    return any((review.get("commit") or {}).get("oid") == pr["headRefOid"] for review in pr.get("reviews") or [])


def closes(pr: dict, repo: str) -> list[int]:
    owner, name = repo.split("/")
    return [ref["number"] for ref in pr.get("closingIssuesReferences") or []
            if ref["repository"]["owner"]["login"].lower() == owner.lower()
            and ref["repository"]["name"].lower() == name.lower()]


def under(path: str, root: str) -> bool:
    return path == root or path.startswith(root.rstrip("/") + "/")


def tilde(path: str) -> str:
    home = str(Path.home())
    return "~" + path[len(home):] if under(path, home) else path


def subtree(issues: dict[int, Issue], number: int) -> list[int]:
    found = [number]
    for child in issues[number].children:
        found += subtree(issues, child)
    return found


def check_in(repo: str, checkout: str, effort: tuple[str, str], now: datetime) -> dict:
    max_implementers = read_max_implementers(checkout)
    kind, value = effort
    issues, roots = read_parent_effort(repo, int(value)) if kind == "parent" else read_milestone_effort(repo, value)
    read_edges(repo, issues)
    prs = read_prs(repo)
    primary, linked = read_worktrees(checkout, repo)
    worktrees = [Worktree(w.path, w.branch, issue_for(w, primary.path, issues)) for w in linked]
    agents = read_agents()
    local_midnight = now.astimezone().replace(hour=0, minute=0, second=0, microsecond=0)
    threads = read_codex_threads([primary.path] + [w.path for w in worktrees], local_midnight - timedelta(days=1))

    findings: list[Finding] = []
    for issue in issues.values():
        findings += blocker_findings(issue, repo)

    prs_by_issue: dict[int, list[dict]] = {}
    for pr in prs:
        for number in closes(pr, repo):
            prs_by_issue.setdefault(number, []).append(pr)
    worked = {w.issue for w in worktrees if w.issue is not None} | set(prs_by_issue)

    awaiting_review: set[int] = set()
    for pr in prs:
        effort_issues = [number for number in closes(pr, repo) if number in issues]
        if not effort_issues or pr["isDraft"] or reviewed_on_head(pr):
            continue
        outcome, stamp = check_state(pr)
        if outcome == "pending":
            continue
        awaiting_review.update(effort_issues)
        closed = ", ".join(f"#{n}" for n in effort_issues)
        checks = {"passed": "checks passed", "failed": "checks failed", "none": "no checks"}[outcome]
        findings.append(Finding(
            "review", f"PR #{pr['number']} {pr['title']} (closes {closed}), {checks} on {pr['headRefOid'][:7]}"
                      f"{ago(stamp, now)}, no review on this head",
            effort_issues[0], {"pr": pr["number"], "head": pr["headRefOid"], "checks": outcome}))

    def worktree_of(cwd: str) -> Worktree | None:
        return next((w for w in worktrees if under(cwd, w.path)), None)

    def located(worktree: Worktree) -> str:
        named_by_branch = worktree.issue is not None and worktree.issue not in path_numbers(worktree, primary.path)
        return f"worktree {tilde(worktree.path)}" + (f", branch {worktree.branch}" if named_by_branch else "")

    def on_board(worktree: Worktree | None) -> bool:
        return worktree is not None and (worktree.issue is None or worktree.issue in issues)

    implementers: list[Implementer] = []
    own_pane = os.environ.get("HERDR_PANE_ID")
    herdr_threads: set[str] = set()
    for agent in agents:
        worktree = worktree_of(agent["cwd"])
        if agent["pane_id"] == own_pane or not on_board(worktree):
            continue
        session = agent.get("agent_session") or {}
        if session.get("source") == "herdr:codex":
            herdr_threads.add(session.get("value"))
        status = agent["agent_status"]
        implementers.append(Implementer(
            f"pane {agent['pane_id']}, {located(worktree)}", worktree, status == WORKING_STATUS,
            f"agent_status {status}", {"pane_id": agent["pane_id"], "worktree": worktree.path, "agent_status": status}))

    # A thread that spawned sub-agents on this board is the conductor directing them, like the own pane.
    directing = {thread.parent for thread in threads} | {os.environ.get("CODEX_THREAD_ID")}
    for thread in threads:
        if thread.id in directing or thread.id in herdr_threads:
            continue
        worktree = worktree_of(thread.works_in) or primary
        running = thread.last_turn_event == CODEX_TURN_STARTED and now - thread.written <= CODEX_RUNNING_WINDOW
        ended = thread.last_turn_event in CODEX_TURN_ENDED
        # An ended thread holds a slot only while its worktree's issue is open on this board: it can be resumed there.
        if not (running and on_board(worktree) or ended and worktree.issue in issues):
            continue
        where = f"checkout {tilde(worktree.path)}" if worktree is primary else located(worktree)
        turn = "turn running" if running else f"{thread.last_turn_event}{ago(thread.written.isoformat(), now)}"
        implementers.append(Implementer(
            f"{thread.originator} thread {thread.id}, {where}", worktree, running, turn,
            {"thread_id": thread.id, "originator": thread.originator, "worktree": worktree.path,
             "last_turn_event": thread.last_turn_event}))

    for implementer in implementers:
        worktree = implementer.worktree
        if worktree.issue is None:
            findings.append(Finding("unmapped", f"{implementer.place}, branch {worktree.branch or '(detached)'}: "
                                    f"{implementer.status}, maps to no issue", None, implementer.detail))
            continue
        if implementer.working or worktree.issue in awaiting_review:
            continue
        open_prs = prs_by_issue.get(worktree.issue, [])
        outcomes = [check_state(pr)[0] for pr in open_prs]
        if "pending" in outcomes:
            continue
        pr_state = "no PR" if not open_prs else ", ".join(
            f"PR #{pr['number']} " + ("draft" if pr["isDraft"] else "reviewed on head, no new commit"
                                      if reviewed_on_head(pr) else f"checks {outcome}")
            for pr, outcome in zip(open_prs, outcomes))
        findings.append(Finding("idle", f"{issues[worktree.issue].ref} ({implementer.place}) {implementer.status}, "
                                f"{pr_state}", worktree.issue, implementer.detail))

    def blocked(number: int) -> bool:
        return any(edge.closed_at is None for edge in issues[number].edges)

    def in_flight(number: int) -> bool:
        return any(n in worked for n in subtree(issues, number))

    ready: list[int] = []

    def walk(number: int) -> None:
        if blocked(number) or number in worked:
            return
        if issues[number].children and in_flight(number):
            for child in issues[number].children:
                walk(child)
        else:
            ready.append(number)

    for root in roots:
        walk(root)
    running = len(implementers)
    free = max(0, max_implementers - running)
    for number in ready[:free]:
        issue = issues[number]
        under_it = f", {len(issue.children)} open sub-issues and none started" if issue.children else ""
        findings.append(Finding("ready", f"{issue.ref} (no open blockers, no PR, no implementer{under_it})",
                                number, {}))

    findings.sort(key=lambda finding: KIND_ORDER.index(finding.kind))
    return {
        "repo": repo,
        "effort": {kind: int(value) if kind == "parent" else value},
        "slots": {"running": running, "max_implementers": max_implementers, "free": free, "ready": len(ready)},
        "implementers": [{"issue": i.worktree.issue, "branch": i.worktree.branch, "working": i.working,
                          "line": f"implementer: {issues[i.worktree.issue].ref if i.worktree.issue in issues else 'no issue'}"
                                  f" ({i.place}) {i.status}", **i.detail} for i in implementers],
        "findings": [{"kind": f.kind, "issue": f.issue, "line": f"{f.kind}: {f.line}", **f.detail}
                     for f in findings],
        "rules": {kind: RULES[kind] for kind in KIND_ORDER if any(f.kind == kind for f in findings)},
    }


CLAIMED_RULE = ("Something already holds this issue: start no implementer. Review that work and send your findings "
                "through its own channel.")


def named_for(worktree: Worktree, primary: str, number: int) -> bool:
    return number in [int(token) for token in NUMBER_TOKEN.findall(worktree.branch)] + path_numbers(worktree, primary)


def claim_check(repo: str, checkout: str, number: int, now: datetime) -> dict:
    """List everything that already holds an issue: an open PR closing it, a worktree named for it, and who works there."""
    primary, linked = read_worktrees(checkout, repo)
    holders = [{"kind": "pr", "line": f"PR #{pr['number']} {pr['title']} closes #{number}", "pr": pr["number"]}
               for pr in read_prs(repo) if number in closes(pr, repo)]
    claimed = [worktree for worktree in linked if named_for(worktree, primary.path, number)]
    if claimed:
        agents = read_agents()
        threads = read_codex_threads([primary.path] + [w.path for w in linked], now - timedelta(days=1))
    for worktree in claimed:
        holders.append({"kind": "worktree", "line": f"{tilde(worktree.path)}, branch {worktree.branch}",
                        "worktree": worktree.path})
        for agent in agents:
            if under(agent["cwd"], worktree.path) and agent["pane_id"] != os.environ.get("HERDR_PANE_ID"):
                holders.append({"kind": "implementer", "pane_id": agent["pane_id"],
                                "line": f"pane {agent['pane_id']}, agent_status {agent['agent_status']}"})
        for thread in threads:
            if under(thread.works_in, worktree.path) and thread.id != os.environ.get("CODEX_THREAD_ID"):
                holders.append({"kind": "implementer", "thread_id": thread.id,
                                "line": f"{thread.originator} thread {thread.id}, "
                                        f"last written{ago(thread.written.isoformat(), now)}"})
    return {"repo": repo, "issue": number, "holders": holders, "rule": CLAIMED_RULE if holders else None}


def print_claim(claim: dict) -> None:
    if not claim["holders"]:
        print(f"free: #{claim['issue']} has no open PR, worktree or implementer")
        return
    for holder in claim["holders"]:
        print(f"{holder['kind']}: {holder['line']}")
    print(f"  rule (claimed): {claim['rule']}")


LEFTOVER_RULES = {
    "merged": "Its PR merged at this head and nothing local remains: remove the worktree and delete its local branch.",
    "merged-with-local-work": "Its PR merged, but work remains here that the merge does not hold: commit and push it "
                              "on a new branch, or discard it on purpose, before removing the worktree.",
    "closed": "Its PR closed without merging: push any unpushed commits, then remove the worktree when the job was "
              "dropped, or reopen the PR when it was not.",
}


def read_branch_prs(repo: str, branch: str) -> list[dict]:
    return run_json(["gh", "pr", "list", "--repo", repo, "--state", "all", "--head", branch, "--limit", "5",
                     "--json", "number,state,headRefOid,title"], f"PRs opened from {branch}")


def local_only_commits(worktree: str, merged_head: str) -> tuple[int, str]:
    """Count commits here that the merge does not hold, and say what they were counted against.

    A worktree behind its merged head holds nothing extra. When the merged head was never fetched, the
    commits are counted against every remote branch instead; this reads only what is already local.
    """
    have_head = subprocess.run(["git", "-C", worktree, "cat-file", "-e", f"{merged_head}^{{commit}}"],
                               capture_output=True).returncode == 0
    if have_head:
        count = run_text(["git", "-C", worktree, "rev-list", "--count", f"{merged_head}..HEAD"], f"commits of {worktree}")
        return int(count), "the merged head does not contain"
    count = run_text(["git", "-C", worktree, "rev-list", "--count", "HEAD", "--not", "--remotes"],
                     f"commits of {worktree}")
    return int(count), "no remote branch contains (the merged head is not fetched here)"


def leftovers(repo: str, checkout: str) -> dict:
    """Find worktrees whose PR is finished: merged (clean or still holding work) or closed without merging."""
    _, linked = read_worktrees(checkout, repo)
    findings = []
    for worktree in linked:
        if not worktree.branch:
            continue  # A detached worktree has no branch a PR could have been opened from.
        prs = read_branch_prs(repo, worktree.branch)
        if not prs or any(pr["state"] == "OPEN" for pr in prs):
            continue
        pr = next((pr for pr in prs if pr["state"] == "MERGED"), prs[0])
        where = f"{tilde(worktree.path)}, branch {worktree.branch}, PR #{pr['number']}"
        detail = {"worktree": worktree.path, "branch": worktree.branch, "pr": pr["number"]}
        if pr["state"] != "MERGED":
            findings.append({"kind": "closed", "line": f"{where} closed without merging", **detail})
            continue
        dirty = run_text(["git", "-C", worktree.path, "status", "--porcelain"], f"status of {worktree.path}").splitlines()
        local_only, against = local_only_commits(worktree.path, pr["headRefOid"])
        if dirty:
            count = f"{len(dirty)} uncommitted file{'' if len(dirty) == 1 else 's'}"
            findings.append({"kind": "merged-with-local-work", "line": f"{where} merged, {count}", **detail})
        elif local_only:
            count = f"{local_only} local commit{'' if local_only == 1 else 's'} {against}"
            findings.append({"kind": "merged-with-local-work", "line": f"{where} merged, {count}", **detail})
        else:
            findings.append({"kind": "merged", "line": f"{where} merged", **detail})
    return {"repo": repo, "findings": findings,
            "rules": {kind: LEFTOVER_RULES[kind] for kind in LEFTOVER_RULES if any(f["kind"] == kind for f in findings)}}


def print_leftovers(result: dict) -> None:
    if not result["findings"]:
        print("no leftover worktrees")
    for kind, rule in result["rules"].items():
        for finding in result["findings"]:
            if finding["kind"] == kind:
                print(f"{kind}: {finding['line']}")
        print(f"  rule ({kind}): {rule}")


def print_board(board: dict) -> None:
    slots = board["slots"]
    print(f"slots: {slots['running']} running, max {slots['max_implementers']} -> {slots['free']} free, "
          f"{slots['ready']} ready")
    for implementer in board["implementers"]:
        print(implementer["line"])
    for kind in KIND_ORDER:
        lines = [finding["line"] for finding in board["findings"] if finding["kind"] == kind]
        if lines:
            print("\n".join(lines))
            print(f"  rule ({kind}): {RULES[kind]}")
    if not board["findings"]:
        print("nothing needs action")


def fail(error: ReadFailed, as_json: bool) -> NoReturn:
    if as_json:
        print(json.dumps({"read_failed": error.read, "error": str(error)}))
    print(f"read failed: {error}", file=sys.stderr)
    sys.exit(EXIT_READ_FAILED)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)

    def command_for(name: str, help_text: str) -> argparse.ArgumentParser:
        command = commands.add_parser(name, help=help_text)
        command.add_argument("--repo", required=True, help="OWNER/REPO")
        command.add_argument("--checkout", help="a local checkout of the repository (default: the current repository)")
        command.add_argument("--json", action="store_true", help="print the result as one JSON object")
        return command

    board_command = command_for("check-in", "print what needs action on the effort's board")
    effort = board_command.add_mutually_exclusive_group(required=True)
    effort.add_argument("--parent", type=int, help="the effort's parent issue; its sub-issues are read recursively")
    effort.add_argument("--milestone", help="the effort's milestone title")
    claim_command = command_for("claim-check", "before assigning an issue, list what already holds it")
    claim_command.add_argument("issue", type=int, help="the issue about to be assigned")
    command_for("leftovers", "list worktrees whose PR merged or closed and that are still open")

    arguments = parser.parse_args()
    if not re.fullmatch(r"[^/\s]+/[^/\s]+", arguments.repo):
        parser.error("--repo must be OWNER/REPO")
    now = datetime.now(timezone.utc)
    try:
        checkout = arguments.checkout or run_text(["git", "rev-parse", "--show-toplevel"], "current checkout").strip()
        checkout = str(Path(checkout).resolve())
        if arguments.command == "check-in":
            result = check_in(arguments.repo, checkout, ("parent", str(arguments.parent))
                              if arguments.parent is not None else ("milestone", arguments.milestone), now)
            needs_action, show = bool(result["findings"]), print_board
        elif arguments.command == "claim-check":
            result = claim_check(arguments.repo, checkout, arguments.issue, now)
            needs_action, show = bool(result["holders"]), print_claim
        else:
            result = leftovers(arguments.repo, checkout)
            needs_action, show = bool(result["findings"]), print_leftovers
    except ReadFailed as error:
        fail(error, arguments.json)
    if arguments.json:
        print(json.dumps(result, indent=2))
    else:
        show(result)
    sys.exit(EXIT_ACTION if needs_action else EXIT_CLEAR)


if __name__ == "__main__":
    main()
