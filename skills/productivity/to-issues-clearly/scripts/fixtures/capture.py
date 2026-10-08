"""Capture real `gh api graphql` responses for issues_check.py's tests.

Runs the check's own query read-only against a private repository and writes
one redacted response per issue to this folder as <number>.json. This
repository is public, so titles, body text and milestone titles are replaced
and the repository is renamed; numbers, states, labels, sub-issue counts,
edges and the response shape stay as GitHub returned them.

    python3 fixtures/capture.py --repo OWNER/REPO 830 1279 ...
"""

import argparse
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from issues_check import QUERY

HERE = Path(__file__).resolve().parent
FIXTURE_REPOSITORY = "example-org/example-app"


def redact_body(body: str) -> str:
    lines = []
    for line in body.splitlines():
        if line.startswith("#"):
            lines.append("## Section")
        elif line.strip():
            lines.append("Redacted line.")
        else:
            lines.append("")
    return "\n".join(lines)


def redact(response: dict, repository: str) -> dict:
    issue = response["data"]["repository"]["issue"]
    issue["title"] = f"Issue {issue['number']}"
    issue["body"] = redact_body(issue["body"])
    issue["url"] = issue["url"].replace(repository, FIXTURE_REPOSITORY)
    if issue["milestone"]:
        issue["milestone"]["title"] = f"Milestone {issue['milestone']['number']}"
    for node in issue["blockedBy"]["nodes"]:
        node["title"] = f"Issue {node['number']}"
        if node["repository"]["nameWithOwner"] == repository:
            node["repository"]["nameWithOwner"] = FIXTURE_REPOSITORY
    return response


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", required=True)
    parser.add_argument("issues", nargs="+", type=int)
    arguments = parser.parse_args()
    owner, name = arguments.repo.split("/", 1)
    for number in arguments.issues:
        output = subprocess.run(
            ["gh", "api", "graphql", "-f", f"query={QUERY}",
             "-F", f"owner={owner}", "-F", f"name={name}", "-F", f"number={number}"],
            capture_output=True, text=True, check=True,
        ).stdout
        response = redact(json.loads(output), arguments.repo)
        (HERE / f"{number}.json").write_text(json.dumps(response, indent=2) + "\n")


if __name__ == "__main__":
    main()
