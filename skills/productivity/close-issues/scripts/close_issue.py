"""Close a GitHub issue only when nothing open hides under it, and record why.

An issue closes for one of four reasons, each recorded in its body:
completed (the proof a person can check), a duplicate (after the survivor
carries every detail under "(was #N)"), out of date (the evidence that the
code or release it describes moved on), or not planned (the owner's decision,
quoted). Open sub-issues and unticked checklist lines block every close; a
duplicate's unticked lines may close once the survivor carries them.

    close_issue.py ready --repo OWNER/REPO --issue N
        Lists what stops N closing. Exits 1 while anything does.
    close_issue.py completed --repo OWNER/REPO --issue N --proof TEXT [--proof TEXT ...]
        Writes the proof under '## Proof' and closes N as completed. Also
        records proof on an issue a 'Closes #N' commit already closed.
    close_issue.py duplicate --repo OWNER/REPO --issue N --of M
        Closes N as a duplicate of M once M is open and its body holds "(was #N)"
        and every unticked line of N.
    close_issue.py out-of-date --repo OWNER/REPO --issue N --evidence TEXT
        Writes the evidence under '## Out of date' and closes N as not planned.
    close_issue.py not-planned --repo OWNER/REPO --issue N --owner-said TEXT
        Writes the owner's decision under '## Not planned' and closes N.

Every closing command reads the issue back and exits 1 unless it closed for
the stated reason with its record in the body.
"""

import argparse
import json
import os
import re
import subprocess
import sys

EXIT_FINDINGS = 1
EXIT_UNREADABLE = 2

RULE = (
    "An issue closes as completed with proof, as a duplicate once the survivor"
    " holds its details, or as not planned on the owner's word. Nothing closes"
    " while it has open sub-issues or unticked checklist lines: finish them, move"
    " them under an open parent, or close each with its own reason first."
)
HEADING = re.compile(r"^#{1,6} ")
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
REASONS = {"completed": "COMPLETED", "duplicate": "DUPLICATE", "out-of-date": "NOT_PLANNED",
           "not-planned": "NOT_PLANNED"}


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


def with_section(body, heading, content):
    """The body with the section under heading replaced by content, or appended."""
    lines = (body or "").splitlines()
    for start, line in enumerate(lines):
        if line.strip().lower() == heading.lower():
            end = start + 1
            while end < len(lines) and not HEADING.match(lines[end]):
                end += 1
            tail = lines[end:]
            lines = lines[:start] + [heading, "", *content.splitlines()] + ([""] + tail if tail else [])
            return "\n".join(lines).rstrip("\n") + "\n"
    trimmed = (body or "").rstrip("\n")
    return f"{trimmed}\n\n{heading}\n\n{content}\n".lstrip("\n")


def is_decision(issue):
    return any(DECISION_LABEL.search(label["name"]) for label in issue["labels"]["nodes"])


def open_pieces(issue):
    """What open work sits under the issue: (kind, message) pairs."""
    me = f"#{issue['number']}"
    found = []
    for child in issue["subIssues"]["nodes"]:
        if child["state"] == "OPEN":
            found.append(("open-sub-issue", f"{me} has open sub-issue #{child['number']} {child['title']}"))
    for text in unticked_lines(issue["body"]):
        found.append(("unticked", f"{me} has an unticked line: {text}"))
    return found


def uncarried_pieces(issue, survivor):
    """Open pieces of a duplicate that its survivor does not carry: an unticked line
    the survivor's body repeats travels with it; an open sub-issue never does."""
    carried = survivor["body"] or ""
    me = f"#{issue['number']}"
    found = [("open-sub-issue", f"{me} has open sub-issue #{child['number']} {child['title']}")
             for child in issue["subIssues"]["nodes"] if child["state"] == "OPEN"]
    found += [("unticked", f"{me} has an unticked line #{survivor['number']} does not carry: {text}")
              for text in unticked_lines(issue["body"]) if text not in carried]
    return found


def ready_findings(issue):
    found = open_pieces(issue)
    if is_decision(issue) and not has_section(issue["body"], "## Decision"):
        found.append(("no-decision", f"#{issue['number']} is a decision issue with no '## Decision' section"))
    return found


# Plain gh ignores this; a gh wrapper that refuses hand-typed closes reads it to let this script's closes through.
CLOSE_PASS = {"CLOSE_ISSUES_SCRIPT": "close_issue.py"}


def gh(*args, stdin=None):
    result = subprocess.run(["gh", *args], input=stdin, capture_output=True, text=True,
                            env={**os.environ, **CLOSE_PASS}, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args[:3])}: {result.stderr.strip()}")
    return result.stdout


def graphql(query, **variables):
    args = ["api", "graphql", "-f", f"query={query}"]
    for name, value in variables.items():
        args += ["-F" if isinstance(value, int) else "-f", f"{name}={value}"]
    return json.loads(gh(*args))["data"]


def read_issue(repo, number):
    owner, name = repo.split("/")
    query = f"""query($owner: String!, $name: String!, $number: Int!) {{
      repository(owner: $owner, name: $name) {{ issue(number: $number) {{ {ISSUE_FIELDS} }} }}
    }}"""
    issue = graphql(query, owner=owner, name=name, number=number)["repository"]["issue"]
    if issue is None:
        raise RuntimeError(f"{repo}#{number} is not an issue")
    return issue


def print_findings(found):
    for kind, message in found:
        print(f"  - {message}")


def ready(args):
    issue = read_issue(args.repo, args.issue)
    found = ready_findings(issue)
    print(RULE)
    if not found:
        print(f"\n#{args.issue} has nothing open under it and can close.")
        return 0
    print(f"\n#{args.issue} cannot close yet:")
    print_findings(found)
    return EXIT_FINDINGS


def write_body(args, issue, heading, content):
    updated = with_section(issue["body"], heading, content)
    if updated != (issue["body"] or ""):
        gh("issue", "edit", str(args.issue), "--repo", args.repo, "--body-file", "-", stdin=updated)


def read_back(args, reason, heading):
    issue = read_issue(args.repo, args.issue)
    problems = []
    if issue["state"] != "CLOSED" or issue["stateReason"] != REASONS[reason]:
        problems.append(f"it is {issue['state'].lower()} ({issue['stateReason']}), not closed as {reason}")
    if heading and not has_section(issue["body"], heading):
        problems.append(f"its body has no '{heading}' section")
    if reason == "duplicate" and not (issue["duplicateOf"] and issue["duplicateOf"]["number"] == args.of):
        problems.append(f"it is not marked a duplicate of #{args.of}")
    if problems:
        print(f"read back #{args.issue}: " + "; ".join(problems), file=sys.stderr)
        return EXIT_FINDINGS
    print(f"#{args.issue} closed as {reason}.")
    return 0


def refuse_open_pieces(issue):
    found = open_pieces(issue)
    if found:
        print(RULE, file=sys.stderr)
        for _, message in found:
            print(f"  - {message}", file=sys.stderr)
    return bool(found)


def completed(args):
    issue = read_issue(args.repo, args.issue)
    proof = [" ".join(p.split()) for p in args.proof if p.strip()]
    if not proof:
        print("completed needs proof a person can check: a commit, a test run, a walk through the product",
              file=sys.stderr)
        return EXIT_FINDINGS
    found = ready_findings(issue)
    if found:
        print(RULE, file=sys.stderr)
        for _, message in found:
            print(f"  - {message}", file=sys.stderr)
        return EXIT_FINDINGS
    if issue["state"] == "CLOSED" and issue["stateReason"] != "COMPLETED":
        print(f"#{args.issue} is already closed as {issue['stateReason']}; reopen it first", file=sys.stderr)
        return EXIT_FINDINGS
    write_body(args, issue, "## Proof", "\n".join(f"- {p}" for p in proof))
    if issue["state"] == "OPEN":
        gh("issue", "close", str(args.issue), "--repo", args.repo, "--reason", "completed")
    return read_back(args, "completed", "## Proof")


def duplicate(args):
    issue = read_issue(args.repo, args.issue)
    survivor = read_issue(args.repo, args.of)
    found = uncarried_pieces(issue, survivor)
    if found:
        print(RULE, file=sys.stderr)
        for _, message in found:
            print(f"  - {message}", file=sys.stderr)
        return EXIT_FINDINGS
    if survivor["state"] != "OPEN":
        print(f"#{args.of} is closed; a duplicate points at the open issue that carries the work",
              file=sys.stderr)
        return EXIT_FINDINGS
    if f"(was #{args.issue})" not in (survivor["body"] or ""):
        print(f"#{args.of} does not carry #{args.issue}'s details yet. Copy every detail #{args.of}"
              f" lacks into its body, word for word, under a line ending '(was #{args.issue})',"
              " then run this again.", file=sys.stderr)
        return EXIT_FINDINGS
    gh("issue", "close", str(args.issue), "--repo", args.repo, "--duplicate-of", str(args.of))
    return read_back(args, "duplicate", None)


def out_of_date(args):
    issue = read_issue(args.repo, args.issue)
    evidence = " ".join(args.evidence.split())
    if not evidence:
        print("out of date needs the evidence: the commit, release or code that moved on", file=sys.stderr)
        return EXIT_FINDINGS
    if refuse_open_pieces(issue):
        return EXIT_FINDINGS
    write_body(args, issue, "## Out of date", evidence)
    gh("issue", "close", str(args.issue), "--repo", args.repo, "--reason", "not planned")
    return read_back(args, "out-of-date", "## Out of date")


def not_planned(args):
    issue = read_issue(args.repo, args.issue)
    said = " ".join(args.owner_said.split())
    if not said:
        print("not planned is the owner's decision: quote what they said", file=sys.stderr)
        return EXIT_FINDINGS
    if refuse_open_pieces(issue):
        return EXIT_FINDINGS
    write_body(args, issue, "## Not planned", f"The owner decided: {said}")
    gh("issue", "close", str(args.issue), "--repo", args.repo, "--reason", "not planned")
    return read_back(args, "not-planned", "## Not planned")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    parsers = {name: commands.add_parser(name)
               for name in ("ready", "completed", "duplicate", "out-of-date", "not-planned")}
    for sub in parsers.values():
        sub.add_argument("--repo", required=True)
        sub.add_argument("--issue", type=int, required=True)
    parsers["completed"].add_argument("--proof", action="append", required=True)
    parsers["duplicate"].add_argument("--of", type=int, required=True)
    parsers["out-of-date"].add_argument("--evidence", required=True)
    parsers["not-planned"].add_argument("--owner-said", required=True)
    args = parser.parse_args()
    handlers = {"ready": ready, "completed": completed, "duplicate": duplicate,
                "out-of-date": out_of_date, "not-planned": not_planned}
    try:
        return handlers[args.command](args)
    except RuntimeError as error:
        print(error, file=sys.stderr)
        return EXIT_UNREADABLE


if __name__ == "__main__":
    sys.exit(main())
