"""Keep every GitHub blocked-by link paired with the reason it is real.

An issue is blocked only when it cannot be done now, or doing it now means
redoing part of it once the blocker lands. Each real blocker is two things
kept in step: a GitHub "blocked by" link, and a line under `## Blocked by` in
the blocked issue's body giving that reason.

    blockers.py check --repo OWNER/REPO [--issue N ...]
        Lists links with no reason line, lines with no link, lines with no
        reason, and blockers that have already closed. Exits 1 while any
        remain, 0 when none do, 2 when GitHub cannot be read.
    blockers.py keep --repo OWNER/REPO --issue N --blocker REF --reason TEXT
        Records a real blocker: adds the link if missing and writes its line.
    blockers.py drop --repo OWNER/REPO --issue N --blocker REF
        Removes a blocker that is not real or has landed: the link and its line.

REF is 123, #123, OWNER/REPO#123 or an issue URL. keep and drop read the issue back
and exit 1 unless the link and the line agree.
"""

import argparse
from dataclasses import dataclass
import json
import re
import subprocess
import sys

EXIT_FINDINGS = 1
EXIT_UNREADABLE = 2

RULE = (
    "An issue is blocked only when it cannot be done now, or doing it now means"
    " redoing part of it once the blocker lands. Each real blocker is a GitHub"
    " blocked-by link plus a line under '## Blocked by' giving that reason;"
    " anything else is not a blocker."
)
SECTION_HEADING = "## Blocked by"
HEADING = re.compile(r"^#{1,6} ")
REFERENCE = re.compile(
    r"https://github\.com/(?P<url_repo>[\w.-]+/[\w.-]+)/issues/(?P<url_number>\d+)"
    r"|(?P<repo>[\w.-]+/[\w.-]+)?#(?P<number>\d+)"
)
ISSUE_FIELDS = """
  number title url state body
  repository { nameWithOwner }
  blockedBy(first: 50) {
    nodes { number title url state repository { nameWithOwner } }
  }
"""


@dataclass(frozen=True)
class Ref:
    repo: str
    number: int

    def short(self, home):
        return f"#{self.number}" if self.repo == home else f"{self.repo}#{self.number}"

    def url(self):
        return f"https://github.com/{self.repo}/issues/{self.number}"


def parse_ref(text, home):
    if text.strip().isdigit():
        return Ref(home, int(text))
    match = REFERENCE.search(text)
    if not match:
        return None
    if match["url_number"]:
        return Ref(match["url_repo"], int(match["url_number"]))
    return Ref(match["repo"] or home, int(match["number"]))


def section_bounds(lines):
    """(start, end) line indexes of the Blocked by section, end exclusive."""
    for start, line in enumerate(lines):
        if line.strip().lower() == SECTION_HEADING.lower():
            end = start + 1
            while end < len(lines) and not HEADING.match(lines[end]):
                end += 1
            return start, end
    return None


def reason_of(line):
    """Text after the reference and its title: after '): ' when the title is a
    link, else after the first ': '."""
    linked = line.find("): ")
    if linked != -1:
        return line[linked + 3:].strip()
    plain = line.find(": ")
    return line[plain + 2:].strip() if plain != -1 else ""


def blocked_by_lines(body, home):
    """{Ref: reason} for each bullet under the Blocked by section."""
    lines = body.splitlines()
    bounds = section_bounds(lines)
    entries = {}
    if not bounds:
        return entries
    for line in lines[bounds[0] + 1:bounds[1]]:
        if not line.lstrip().startswith(("- ", "* ")):
            continue
        ref = parse_ref(line, home)
        if ref:
            entries[ref] = reason_of(line)
    return entries


def format_line(ref, title, reason, home):
    return f"- {ref.short(home)} [{title}]({ref.url()}): {reason}"


def with_line(body, ref, line, home):
    """The body with ref's line replaced, or added to the section, or a new
    section appended at the end."""
    lines = body.splitlines()
    bounds = section_bounds(lines)
    if not bounds:
        trimmed = body.rstrip("\n")
        return f"{trimmed}\n\n{SECTION_HEADING}\n\n{line}\n"
    start, end = bounds
    for index in range(start + 1, end):
        if parse_ref(lines[index], home) == ref and lines[index].lstrip().startswith(("- ", "* ")):
            lines[index] = line
            return "\n".join(lines) + "\n"
    last = end
    while last > start + 1 and not lines[last - 1].strip():
        last -= 1
    lines.insert(last, line)
    return "\n".join(lines) + "\n"


def without_line(body, ref, home):
    """The body with ref's line removed, and the section removed once empty."""
    lines = body.splitlines()
    bounds = section_bounds(lines)
    if not bounds:
        return body
    start, end = bounds
    kept = [
        line for line in lines[start + 1:end]
        if not (line.lstrip().startswith(("- ", "* ")) and parse_ref(line, home) == ref)
    ]
    if any(line.strip() for line in kept):
        lines[start + 1:end] = kept
    else:
        before = lines[:start]
        while before and not before[-1].strip():
            before.pop()
        after = lines[end:]
        lines = before + ([""] if before and after else []) + after
    return "\n".join(lines).rstrip("\n") + "\n"


def findings_for(issue):
    """Findings for one issue as returned by the GraphQL query."""
    home = issue["repository"]["nameWithOwner"]
    me = f"#{issue['number']}"
    links = {
        Ref(node["repository"]["nameWithOwner"], node["number"]): node
        for node in issue["blockedBy"]["nodes"]
    }
    lines = blocked_by_lines(issue["body"] or "", home)
    found = []
    for ref, node in links.items():
        if node["state"] != "OPEN":
            found.append(("landed", f"{me} is still linked as blocked by {ref.short(home)}, which is closed"))
        elif ref not in lines:
            found.append(("unsettled", f"{me} is linked as blocked by {ref.short(home)} with no reason line"))
    for ref, reason in lines.items():
        if ref not in links:
            found.append(("unlinked", f"{me} lists {ref.short(home)} under Blocked by with no blocked-by link"))
        elif not reason:
            found.append(("no-reason", f"{me} lists {ref.short(home)} under Blocked by with no reason"))
    return found


FIX = {
    "unsettled": "Judge each: keep it with the reason it is real, or drop it.",
    "unlinked": "Judge each: keep it (adds the link) or drop it (removes the line).",
    "no-reason": "Judge each: keep it with the reason it is real, or drop it.",
    "landed": "The blocker closed, so it no longer blocks: drop it.",
}


def gh(*args, stdin=None):
    result = subprocess.run(["gh", *args], input=stdin, capture_output=True, text=True)
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


def open_issues(repo):
    owner, name = repo.split("/")
    query = f"""query($owner: String!, $name: String!, $after: String) {{
      repository(owner: $owner, name: $name) {{
        issues(states: OPEN, first: 50, after: $after) {{
          pageInfo {{ hasNextPage endCursor }}
          nodes {{ {ISSUE_FIELDS} }}
        }}
      }}
    }}"""
    issues, after = [], None
    while True:
        variables = {"owner": owner, "name": name}
        if after:
            variables["after"] = after
        page = graphql(query, **variables)["repository"]["issues"]
        issues += page["nodes"]
        if not page["pageInfo"]["hasNextPage"]:
            return issues
        after = page["pageInfo"]["endCursor"]


def check(args):
    issues = ([read_issue(args.repo, n) for n in args.issue] if args.issue else open_issues(args.repo))
    found = [f for issue in issues for f in findings_for(issue)]
    print(RULE)
    if not found:
        print(f"\n{args.repo}: every blocked-by link has its reason, and every reason its link.")
        return 0
    for kind, fix in FIX.items():
        messages = [message for k, message in found if k == kind]
        if messages:
            print(f"\n{fix}")
            for message in messages:
                print(f"  - {message}")
    script = sys.argv[0]
    print(f"\nkeep: {script} keep --repo {args.repo} --issue N --blocker REF --reason TEXT"
          f"\ndrop: {script} drop --repo {args.repo} --issue N --blocker REF")
    return EXIT_FINDINGS


def state_of(issue, ref):
    home = issue["repository"]["nameWithOwner"]
    linked = any(
        Ref(n["repository"]["nameWithOwner"], n["number"]) == ref for n in issue["blockedBy"]["nodes"])
    return linked, blocked_by_lines(issue["body"] or "", home).get(ref)


def keep(args):
    issue = read_issue(args.repo, args.issue)
    home = issue["repository"]["nameWithOwner"]
    ref = parse_ref(args.blocker, home)
    reason = " ".join(args.reason.split())
    if not reason:
        print("a kept blocker needs its reason", file=sys.stderr)
        return EXIT_FINDINGS
    blocker = read_issue(ref.repo, ref.number)
    if blocker["state"] != "OPEN":
        print(f"{ref.short(home)} is closed and blocks nothing; drop it instead", file=sys.stderr)
        return EXIT_FINDINGS
    linked, _ = state_of(issue, ref)
    if not linked:
        gh("issue", "edit", str(args.issue), "--repo", args.repo, "--add-blocked-by", ref.url())
    body = issue["body"] or ""
    updated = with_line(body, ref, format_line(ref, blocker["title"], reason, home), home)
    if updated != body:
        gh("issue", "edit", str(args.issue), "--repo", args.repo, "--body-file", "-", stdin=updated)
    linked, line = state_of(read_issue(args.repo, args.issue), ref)
    if not (linked and line == reason):
        print(f"read back #{args.issue}: link {'present' if linked else 'missing'},"
              f" line {'matches' if line == reason else 'does not match'}", file=sys.stderr)
        return EXIT_FINDINGS
    print(f"#{args.issue} blocked by {ref.short(home)}: {reason}")
    return 0


def drop(args):
    issue = read_issue(args.repo, args.issue)
    home = issue["repository"]["nameWithOwner"]
    ref = parse_ref(args.blocker, home)
    linked, _ = state_of(issue, ref)
    if linked:
        gh("issue", "edit", str(args.issue), "--repo", args.repo, "--remove-blocked-by", ref.url())
    body = issue["body"] or ""
    updated = without_line(body, ref, home)
    if updated != body:
        gh("issue", "edit", str(args.issue), "--repo", args.repo, "--body-file", "-", stdin=updated)
    linked, line = state_of(read_issue(args.repo, args.issue), ref)
    if linked or line is not None:
        print(f"read back #{args.issue}: {ref.short(home)} is still"
              f" {'linked' if linked else 'listed'}", file=sys.stderr)
        return EXIT_FINDINGS
    print(f"#{args.issue} is not blocked by {ref.short(home)}")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    check_parser = commands.add_parser("check")
    check_parser.add_argument("--repo", required=True)
    check_parser.add_argument("--issue", type=int, action="append")
    keep_parser = commands.add_parser("keep")
    drop_parser = commands.add_parser("drop")
    for sub in (keep_parser, drop_parser):
        sub.add_argument("--repo", required=True)
        sub.add_argument("--issue", type=int, required=True)
        sub.add_argument("--blocker", required=True)
    keep_parser.add_argument("--reason", required=True)
    args = parser.parse_args()
    try:
        return {"check": check, "keep": keep, "drop": drop}[args.command](args)
    except RuntimeError as error:
        print(error, file=sys.stderr)
        return EXIT_UNREADABLE


if __name__ == "__main__":
    sys.exit(main())
