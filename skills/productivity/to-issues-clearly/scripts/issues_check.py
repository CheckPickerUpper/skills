"""Check published issues' blocked-by edges against their recorded reasons.

Reads each named issue fresh from GitHub through `gh`: its native blocked-by
edges and each blocking issue's state, its sub-issue count, the reason lines
under its `## Blocked by` heading, its labels and its milestone. Prints every
finding and a summary of the edges, labels and milestones that exist.

Exit 0 with no findings, 1 with findings, 2 when a read fails.
"""

import argparse
from dataclasses import asdict, dataclass
import json
import re
import subprocess
import sys
from typing import Literal

EXIT_FINDINGS = 1
EXIT_READ_FAILED = 2
PAGE = 100

QUERY = """
query($owner: String!, $name: String!, $number: Int!) {
  repository(owner: $owner, name: $name) {
    issue(number: $number) {
      number title state url body
      labels(first: 100) { totalCount nodes { name } }
      milestone { number title }
      subIssuesSummary { total }
      blockedBy(first: 100) {
        totalCount
        nodes { number title state repository { nameWithOwner } }
      }
    }
  }
}
"""

RULE = """\
The rule: an issue is blocked by X only when doing it now would duplicate or
conflict with work in X that must land first: it cannot start at all, or it
cannot meet one of its acceptance criteria, until X lands. Merge order,
rebase-time checks, "cleaner after X", "extra work if done now", and anything
already merged or closed are never blockers. When only one piece of an issue
depends on X, the edge goes on that piece's own issue, never on its parent.

Each blocked-by edge needs one reason line under `## Blocked by` in the
blocked issue's body:
  - #N <title>: cannot <what this issue cannot start or meet> until it lands, because <why>.
A reason line on an issue with sub-issues must say the whole issue `cannot start`.

Fix each finding: remove a stale or unreal edge together with its reason
line, move a parent's edge onto the sub-issue that depends on X, or write the
missing reason line. Then run this check again until it exits 0."""

BLOCKED_BY_HEADING = re.compile(r"^##\s+Blocked by\s*$", re.IGNORECASE)
HEADING = re.compile(r"^#{1,2}\s")
FENCE = re.compile(r"^\s*(```|~~~)")
REASON_LINE = re.compile(r"^- #(\d+)\b")

FindingKind = Literal["stale-blocker", "parent-blocker", "missing-reason", "orphan-reason"]


class ReadFailed(Exception):
    pass


@dataclass(frozen=True)
class Blocker:
    number: int
    title: str
    state: str
    repository: str
    reason: str | None


@dataclass(frozen=True)
class Issue:
    repository: str
    number: int
    title: str
    state: str
    url: str
    labels: list[str]
    milestone: str | None
    sub_issues: int
    blocked_by: list[Blocker]
    reason_lines: list[str]


@dataclass(frozen=True)
class Finding:
    kind: FindingKind
    issue: int
    title: str
    blocker: int
    detail: str


def reason_lines(body: str) -> list[str]:
    """Return the `- #N` lines under every `## Blocked by` heading, outside code fences."""
    lines: list[str] = []
    in_section = False
    in_fence = False
    for line in body.splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if HEADING.match(line):
            in_section = bool(BLOCKED_BY_HEADING.match(line.strip()))
            continue
        stripped = line.strip()
        if in_section and REASON_LINE.match(stripped):
            lines.append(stripped)
    return lines


def named_issue(line: str) -> int:
    return int(REASON_LINE.match(line).group(1))


def is_valid_reason(line: str) -> bool:
    return "cannot" in line.lower()


def says_cannot_start(line: str) -> bool:
    return "cannot start" in line.lower()


def run_gh(repository: str, number: int) -> dict:
    owner, name = repository.split("/", 1)
    read = f"gh api graphql issue {repository}#{number}"
    try:
        completed = subprocess.run(
            ["gh", "api", "graphql", "-f", f"query={QUERY}",
             "-F", f"owner={owner}", "-F", f"name={name}", "-F", f"number={number}"],
            capture_output=True, text=True, timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ReadFailed(f"{read}: {error}") from error
    if completed.returncode != 0:
        raise ReadFailed(f"{read}: exit {completed.returncode}: {completed.stderr.strip()}")
    try:
        response = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise ReadFailed(f"{read}: response is not JSON: {error}") from error
    if response.get("errors"):
        raise ReadFailed(f"{read}: {'; '.join(e.get('message', str(e)) for e in response['errors'])}")
    issue = ((response.get("data") or {}).get("repository") or {}).get("issue")
    if issue is None:
        raise ReadFailed(f"{read}: no such issue")
    for connection in ("labels", "blockedBy"):
        if issue[connection]["totalCount"] > len(issue[connection]["nodes"]):
            raise ReadFailed(f"{read}: more than {PAGE} {connection}, which this check does not page through")
    return issue


def read_issue(repository: str, number: int) -> Issue:
    raw = run_gh(repository, number)
    lines = reason_lines(raw["body"] or "")
    valid: dict[int, str] = {}
    for line in lines:
        if is_valid_reason(line):
            valid.setdefault(named_issue(line), line)
    blocked_by = []
    for node in raw["blockedBy"]["nodes"]:
        same_repository = node["repository"]["nameWithOwner"].lower() == repository.lower()
        blocked_by.append(Blocker(
            number=node["number"], title=node["title"], state=node["state"],
            repository=node["repository"]["nameWithOwner"],
            reason=valid.get(node["number"]) if same_repository else None,
        ))
    return Issue(
        repository=repository, number=raw["number"], title=raw["title"], state=raw["state"],
        url=raw["url"], labels=[label["name"] for label in raw["labels"]["nodes"]],
        milestone=raw["milestone"]["title"] if raw["milestone"] else None,
        sub_issues=raw["subIssuesSummary"]["total"], blocked_by=blocked_by, reason_lines=lines,
    )


def blocker_name(issue: Issue, blocker: Blocker) -> str:
    prefix = "" if blocker.repository.lower() == issue.repository.lower() else blocker.repository
    return f"{prefix}#{blocker.number} {blocker.title}"


def findings(issue: Issue) -> list[Finding]:
    found: list[Finding] = []

    def add(kind: FindingKind, blocker: int, detail: str) -> None:
        found.append(Finding(kind, issue.number, issue.title, blocker, detail))

    edges = {b.number for b in issue.blocked_by if b.repository.lower() == issue.repository.lower()}
    for blocker in issue.blocked_by:
        name = blocker_name(issue, blocker)
        if blocker.state == "CLOSED":
            add("stale-blocker", blocker.number,
                f"blocked by {name}, which is closed; a closed issue blocks nothing.")
        if blocker.reason is None:
            add("missing-reason", blocker.number,
                f"blocked by {name} with no reason line: no `- #{blocker.number} ...: cannot ...` line under `## Blocked by`.")
        if issue.sub_issues and (blocker.reason is None or not says_cannot_start(blocker.reason)):
            add("parent-blocker", blocker.number,
                f"has {issue.sub_issues} sub-issues and is blocked by {name}, but no reason line says the whole issue "
                "cannot start; put the edge on the sub-issue that depends on it.")
    for line in issue.reason_lines:
        if named_issue(line) not in edges:
            add("orphan-reason", named_issue(line),
                f"reason line names #{named_issue(line)}, which is not a blocked-by edge: {line}")
    return found


def print_text(issues: list[Issue], found: list[Finding]) -> None:
    for issue in issues:
        print(f"{issue.repository}#{issue.number} {issue.title} [{issue.state}]")
        print(f"  {issue.url}")
        print(f"  labels: {', '.join(issue.labels) if issue.labels else '(none)'}")
        print(f"  milestone: {issue.milestone or '(none)'}")
        print(f"  sub-issues: {issue.sub_issues}")
        if issue.blocked_by:
            print("  blocked by:")
            for blocker in issue.blocked_by:
                reason = "reason recorded" if blocker.reason else "no reason line"
                print(f"    {blocker_name(issue, blocker)} [{blocker.state}] ({reason})")
        else:
            print("  blocked by: (none)")
    print()
    if not found:
        print(f"No findings across {len(issues)} issues.")
        return
    print(f"{len(found)} findings across {len(issues)} issues:")
    for finding in found:
        print(f"  {finding.kind}: #{finding.issue} {finding.title}: {finding.detail}")
    print()
    print(RULE)


def parse_issue_number(text: str) -> int:
    try:
        return int(text.lstrip("#"))
    except ValueError:
        raise argparse.ArgumentTypeError(f"not an issue number: {text}") from None


def parse_repository(text: str) -> str:
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", text):
        raise argparse.ArgumentTypeError(f"expected OWNER/REPO, got {text}")
    return text


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", required=True, type=parse_repository, help="OWNER/REPO")
    parser.add_argument("issues", nargs="+", type=parse_issue_number, metavar="ISSUE")
    parser.add_argument("--json", action="store_true", help="print one JSON object")
    arguments = parser.parse_args()
    try:
        issues = [read_issue(arguments.repo, number) for number in arguments.issues]
    except ReadFailed as error:
        print(f"read failed: {error}", file=sys.stderr)
        sys.exit(EXIT_READ_FAILED)
    found = [finding for issue in issues for finding in findings(issue)]
    if arguments.json:
        print(json.dumps({
            "issues": [asdict(issue) for issue in issues],
            "findings": [asdict(finding) for finding in found],
            "rule": RULE if found else None,
        }, indent=2))
    else:
        print_text(issues, found)
    sys.exit(EXIT_FINDINGS if found else 0)


if __name__ == "__main__":
    main()
