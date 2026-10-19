"""Read a GitHub tracker and list the open work no view of it shows.

    audit_issues.py --repo OWNER/REPO

Lists open issues under closed parents, issues closed as completed while
sub-issues or checklist lines under them are open, duplicates of nothing,
decisions closed with no '## Decision', and decisions waiting on the owner.
Exits 1 while any but the last remain, 0 when none do, and 2 when the tracker
cannot be read. It only reads; every close goes through close-issues.
"""

import argparse
import json
import re
import subprocess
import sys

EXIT_FINDINGS = 1
EXIT_UNREADABLE = 2

RULE = (
    "Open work stays visible: an issue closes as completed only when nothing under it"
    " is open, a duplicate names its original, a decision closes with its answer in the"
    " body, and an open issue sits under an open parent."
)
FENCE = re.compile(r"^\s*(```|~~~)")
UNTICKED = re.compile(r"^\s*[-*+] \[ \] (?P<text>.+)")
DECISION_LABEL = re.compile(r"decision", re.IGNORECASE)
ISSUE_FIELDS = """
  number title url state stateReason body
  labels(first: 30) { nodes { name } }
  parent { number title url state }
  subIssues(first: 100) { nodes { number title url state } }
  duplicateOf { number url }
"""
FIXES = {
    "closed-parent": "Move each under an open parent, or reopen the parent if its work is not done.",
    "hidden": "Reopen each: it closed with work still open under it.",
    "no-original": "Reopen each and close it again through close-issues' duplicate command.",
    "no-decision": "Write each decision under '## Decision' in the body, or reopen it.",
}
WAITING = "Waiting on the owner (report these; an audit never answers them):"


def unticked_lines(body):
    """The text of each '- [ ]' line outside code fences."""
    found, fenced = [], False
    for line in (body or "").splitlines():
        if FENCE.match(line):
            fenced = not fenced
            continue
        match = None if fenced else UNTICKED.match(line)
        if match:
            found.append(match["text"].strip())
    return found


def has_section(body, heading):
    return any(line.strip().lower() == heading.lower() for line in (body or "").splitlines())


def is_decision(issue):
    return any(DECISION_LABEL.search(label["name"]) for label in issue["labels"]["nodes"])


def findings(issue):
    """(kind, message) pairs for one issue: structural findings and decisions waiting on the owner."""
    me = f"#{issue['number']} {issue['title']}"
    found = []
    if issue["state"] == "OPEN":
        parent = issue["parent"]
        if parent and parent["state"] != "OPEN":
            found.append(("closed-parent", f"{me} is open under closed parent #{parent['number']}"))
        if is_decision(issue) and not has_section(issue["body"], "## Decision"):
            found.append(("waiting", f"{me} waits on the owner's decision"))
        return found
    if issue["stateReason"] == "COMPLETED":
        for child in issue["subIssues"]["nodes"]:
            if child["state"] == "OPEN":
                found.append(("hidden", f"closed {me} has open sub-issue #{child['number']} {child['title']}"))
        for text in unticked_lines(issue["body"]):
            found.append(("hidden", f"closed {me} has an unticked line: {text}"))
        if is_decision(issue) and not has_section(issue["body"], "## Decision"):
            found.append(("no-decision", f"{me} closed as decided with no '## Decision' section"))
    if issue["stateReason"] == "DUPLICATE" and not issue["duplicateOf"]:
        found.append(("no-original", f"{me} closed as a duplicate of nothing"))
    return found


def all_issues(repo):
    owner, name = repo.split("/")
    query = f"""query($owner: String!, $name: String!, $after: String) {{
      repository(owner: $owner, name: $name) {{
        issues(first: 50, after: $after) {{
          pageInfo {{ hasNextPage endCursor }}
          nodes {{ {ISSUE_FIELDS} }}
        }}
      }}
    }}"""
    issues, after = [], None
    while True:
        args = ["api", "graphql", "-f", f"query={query}", "-f", f"owner={owner}", "-f", f"name={name}"]
        if after:
            args += ["-f", f"after={after}"]
        result = subprocess.run(["gh", *args], capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise RuntimeError(f"gh api graphql: {result.stderr.strip()}")
        page = json.loads(result.stdout)["data"]["repository"]["issues"]
        issues += page["nodes"]
        if not page["pageInfo"]["hasNextPage"]:
            return issues
        after = page["pageInfo"]["endCursor"]


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", required=True)
    args = parser.parse_args()
    try:
        issues = all_issues(args.repo)
    except RuntimeError as error:
        print(error, file=sys.stderr)
        return EXIT_UNREADABLE
    found = [f for issue in issues for f in findings(issue)]
    print(RULE)
    for kind, fix in FIXES.items():
        messages = [m for k, m in found if k == kind]
        if messages:
            print(f"\n{fix}")
            for message in messages:
                print(f"  - {message}")
    waiting = [m for k, m in found if k == "waiting"]
    if waiting:
        print(f"\n{WAITING}")
        for message in waiting:
            print(f"  - {message}")
    if any(k != "waiting" for k, _ in found):
        return EXIT_FINDINGS
    print(f"\n{args.repo}: {len(issues)} issues read; no open work hides under a closed issue.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
