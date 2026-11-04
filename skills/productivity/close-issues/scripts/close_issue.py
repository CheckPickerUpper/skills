"""Close a GitHub issue only when nothing open hides under it, and record why.

An issue closes for one of four reasons, each recorded in its body:
completed (the proof a person can check), a duplicate (after the survivor
carries every detail under "(was #N)"), out of date (the evidence that the
code or release it describes moved on), or not planned (the owner's decision,
quoted). Open sub-issues and unticked checklist lines block every close; a
duplicate's unticked lines may close once the survivor carries them. An issue
whose body has a reproduction section closes as completed only after a rerun of
that reproduction is recorded and shows it fixed: passing tests are not a rerun.
A checklist line is done only when a landed commit names it ('Part of #N: <id>')
or another proof in checklist_proof.py holds; a box ticked by hand counts for
nothing, and a line that left the body needs a recorded move or drop.

Run every command inside a checkout of the repository: the landed commits are
read from its origin's landing branch (the repository's default branch, or
--branch).

    close_issue.py ready --repo OWNER/REPO --issue N
        Lists what stops N closing. Exits 1 while anything does.
    close_issue.py sync --repo OWNER/REPO --issue N
        Sets every checklist box of N to what its proof shows.
    close_issue.py pre-push REMOTE URL
        The pre-push hook: refuses a push to the landing branch whose commits
        say 'Closes #N' while N cannot close, because GitHub closes N on push.
    close_issue.py reran --repo OWNER/REPO --issue N --ran TEXT --saw TEXT --result fixed|still-fails
        Writes the rerun of N's reproduction under '## Reproduction rerun'. Refuses
        a rerun that runs none of the reproduction's commands. Exits 1 while the
        reproduction still fails.
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

from checklist_proof import Evidence, checklist, section_lines, closed_issues, line_findings, removed_findings, with_derived_ticks

EXIT_FINDINGS = 1
EXIT_UNREADABLE = 2

RULE = (
    "An issue closes as completed with proof, as a duplicate once the survivor"
    " holds its details, or as not planned on the owner's word. Nothing closes"
    " while it has open sub-issues or unproved checklist lines: finish them, move"
    " them under an open parent, or close each with its own reason first. A line is"
    " proved by a landed commit that names it ('Part of #N: <line id>'), never by a"
    " box ticked by hand, and a line leaves the body only with a recorded move or"
    " drop under '## Checklist changes'. An issue"
    " with a reproduction closes as completed only once a recorded rerun of that"
    " reproduction shows it fixed; tests that pass are not that rerun."
)
HEADING = re.compile(r"^#{1,6} ")
FENCE = re.compile(r"^\s*(```|~~~)\s*(?P<lang>\S*)")
UNTICKED = re.compile(r"^\s*[-*+] \[ \] (?P<text>.+)")
DECISION_LABEL = re.compile(r"decision", re.IGNORECASE)
REPRO_HEADING = re.compile(
    r"^#{1,6}\s+(steps to reproduce|how to reproduce|to reproduce|reproduce|reproduction( steps)?"
    r"|repro( steps)?)\s*:?\s*$", re.IGNORECASE)
RERUN_HEADING = "## Reproduction rerun"
RERUN_FIELD = re.compile(r"^\s*[-*+]?\s*(?P<name>Ran|Saw|Result):\s*(?P<value>.*)$")
INLINE_CODE = re.compile(r"`([^`\n]+)`")
SHELL_LANGS = {"sh", "bash", "zsh", "fish", "shell", "console", "shell-session", "powershell", "ps1",
               "pwsh", "cmd", "bat"}
RESULTS = {"fixed": "fixed", "still-fails": "still fails"}
ISSUE_FIELDS = """
  number title url state stateReason body
  labels(first: 30) { nodes { name } }
  parent { number title url state }
  subIssues(first: 100) { nodes { number title url state } }
  duplicateOf { number url }
  milestone { number title state issues(states: OPEN) { totalCount } }
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


def evidence_for(issue, repo, commits):
    decided = is_decision(issue) and has_section(issue["body"], "## Decision")
    return Evidence(issue["number"], repo, tuple(commits), issue["body"] or "", decided)


def open_pieces(issue, evidence, revisions=(), read_body=None):
    """What open work sits under the issue: (kind, message) pairs."""
    me = f"#{issue['number']}"
    found = []
    for child in issue["subIssues"]["nodes"]:
        if child["state"] == "OPEN":
            found.append(("open-sub-issue", f"{me} has open sub-issue #{child['number']} {child['title']}"))
    found += line_findings(evidence)
    if revisions:
        found += removed_findings(evidence, revisions, read_body)
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


def section(body, matches):
    """The heading and lines of the first section whose heading matches, ignoring
    heading-like lines inside code fences; (None, []) when there is none."""
    heading, lines, fenced = None, [], False
    for line in (body or "").splitlines():
        if FENCE.match(line):
            fenced = not fenced
        elif not fenced and HEADING.match(line):
            if heading:
                break
            if matches(line.strip()):
                heading = line.strip()
                continue
        if heading:
            lines.append(line)
    return heading, lines


def reproduction(body):
    return section(body, lambda line: bool(REPRO_HEADING.match(line)))


def reproduction_commands(lines):
    """What the reproduction runs: its inline code, the lines of its shell blocks,
    and any '$ ' line in its other blocks."""
    found, fence_lang = [], None
    for line in lines:
        fence = FENCE.match(line)
        if fence:
            fence_lang = None if fence_lang is not None else fence["lang"].lower()
            continue
        text = line.strip()
        if fence_lang is None:
            found += [code.strip() for code in INLINE_CODE.findall(line) if code.strip()]
        elif text.startswith("$ "):
            found.append(text[2:].strip())
        elif fence_lang in SHELL_LANGS and text and not text.startswith("#"):
            found.append(text)
    return list(dict.fromkeys(" ".join(c.split()) for c in found if c.strip()))


def runs_reproduction(ran, commands):
    """Whether the rerun names one of the reproduction's commands; a reproduction
    written only in prose has none to name, so any rerun of it counts."""
    ran = " ".join(ran.split())
    return not commands or any(command in ran for command in commands)


def recorded_rerun(body):
    """The Ran, Saw and Result fields under '## Reproduction rerun', or None."""
    heading, lines = section(body, lambda line: line.lower() == RERUN_HEADING.lower())
    if not heading:
        return None
    fields = {}
    for line in lines:
        match = RERUN_FIELD.match(line)
        if match:
            fields[match["name"].lower()] = match["value"].strip()
    return fields


def rerun_findings(issue):
    me = f"#{issue['number']}"
    heading, lines = reproduction(issue["body"])
    if not heading:
        return []
    rerun = recorded_rerun(issue["body"])
    if rerun is None:
        return [("no-rerun", f"{me} has a reproduction under '{heading}' and no recorded rerun of it."
                 " Rerun that reproduction on the fixed code and record it with 'close_issue.py reran';"
                 " tests that pass are not a rerun")]
    commands = reproduction_commands(lines)
    if not runs_reproduction(rerun.get("ran", ""), commands):
        return [("rerun-unrelated", f"{me}'s recorded rerun ran '{rerun.get('ran', '')}', which is none of"
                 f" its reproduction's commands: {', '.join(commands)}")]
    if rerun.get("result", "").lower() != RESULTS["fixed"]:
        return [("repro-still-fails", f"{me}'s reproduction still fails on its last rerun"
                 f" ({rerun.get('saw', '')}); the bug is not fixed, whatever the tests say")]
    return []


def ready_findings(issue, evidence, revisions=(), read_body=None):
    found = open_pieces(issue, evidence, revisions, read_body)
    if is_decision(issue) and not has_section(issue["body"], "## Decision"):
        found.append(("no-decision", f"#{issue['number']} is a decision issue with no '## Decision' section"))
    return found + rerun_findings(issue)


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


def read_revisions(repo, number):
    """Every earlier text of the issue's body, newest first, from GitHub's edit history."""
    owner, name = repo.split("/")
    query = """query($owner: String!, $name: String!, $number: Int!, $after: String) {
      repository(owner: $owner, name: $name) { issue(number: $number) {
        userContentEdits(first: 100, after: $after) { nodes { diff } pageInfo { hasNextPage endCursor } }
      } }
    }"""
    texts, after = [], None
    while True:
        variables = {"owner": owner, "name": name, "number": number}
        if after:
            variables["after"] = after
        edits = graphql(query, **variables)["repository"]["issue"]["userContentEdits"]
        texts += [node["diff"] or "" for node in edits["nodes"]]
        if not edits["pageInfo"]["hasNextPage"]:
            return texts
        after = edits["pageInfo"]["endCursor"]


def git(checkout, *args):
    result = subprocess.run(["git", "-C", checkout, *args], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"git -C {checkout} {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout


REMOTE_SLUG = re.compile(r"github\.com[:/](?P<slug>[^/]+/[^/]+?)(?:\.git)?/?$")


def remote_slug(url):
    match = REMOTE_SLUG.search(url.strip())
    return match["slug"] if match else None


def landing_branch(args):
    return args.branch or gh("api", f"repos/{args.repo}", "--jq", ".default_branch").strip()


def commits_of(checkout, *revs):
    """(sha, message) pairs of the commits revs select."""
    out = git(checkout, "log", "--format=%H%x1f%B%x1e", *revs)
    pairs = [entry.strip("\n").split("\x1f", 1) for entry in out.split("\x1e") if entry.strip()]
    return [(sha, message) for sha, message in pairs]


def landed_commits(args, number):
    """The commits on origin's landing branch that mention #number."""
    url = git(args.checkout, "remote", "get-url", "origin").strip()
    if (remote_slug(url) or "").lower() != args.repo.lower():
        raise RuntimeError(f"{args.checkout} is a checkout of {url}, not {args.repo}; run inside a checkout"
                           f" of {args.repo} or pass --checkout")
    branch = landing_branch(args)
    git(args.checkout, "fetch", "--quiet", "origin", branch)
    return commits_of(args.checkout, f"origin/{branch}", "--fixed-strings", f"--grep=#{number}")


def assess(args, issue, pushed=()):
    """The issue's evidence and every finding that stops it closing."""
    revisions = read_revisions(args.repo, issue["number"])
    needs_commits = bool(checklist(issue["body"])) or any(checklist(text) for text in revisions)
    commits = [*landed_commits(args, issue["number"]), *pushed] if needs_commits else []
    evidence = evidence_for(issue, args.repo, commits)
    read_body = lambda number: read_issue(args.repo, number)["body"]
    return evidence, ready_findings(issue, evidence, revisions, read_body)


def print_findings(found):
    for kind, message in found:
        print(f"  - {message}")


def ready(args):
    issue = read_issue(args.repo, args.issue)
    _, found = assess(args, issue)
    print(RULE)
    if not found:
        print(f"\n#{args.issue} has nothing open under it and can close.")
        return 0
    print(f"\n#{args.issue} cannot close yet:")
    print_findings(found)
    return EXIT_FINDINGS


def write_body(args, issue, heading, content, base=None):
    updated = with_section(issue["body"] if base is None else base, heading, content)
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
    close_finished_milestone(args, issue)
    return 0


def finished_milestone(issue):
    """The number of the issue's milestone when it is still open with no open issue left."""
    milestone = issue.get("milestone")
    if milestone and milestone["state"] == "OPEN" and milestone["issues"]["totalCount"] == 0:
        return milestone["number"]
    return None


def close_finished_milestone(args, issue):
    """GitHub never closes a milestone itself, so the close that finishes one closes it."""
    number = finished_milestone(issue)
    if number is not None:
        gh("api", "-X", "PATCH", f"repos/{args.repo}/milestones/{number}", "-f", "state=closed")
        print(f"Milestone '{issue['milestone']['title']}' has no open issue left; closed it.")


def refuse_open_pieces(args, issue):
    evidence, _ = assess(args, issue)
    found = open_pieces(issue, evidence)
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
    evidence, found = assess(args, issue)
    if found:
        print(RULE, file=sys.stderr)
        for _, message in found:
            print(f"  - {message}", file=sys.stderr)
        return EXIT_FINDINGS
    if issue["state"] == "CLOSED" and issue["stateReason"] != "COMPLETED":
        print(f"#{args.issue} is already closed as {issue['stateReason']}; reopen it first", file=sys.stderr)
        return EXIT_FINDINGS
    # A reopened issue closes again on top of its earlier proof, never in place of it.
    earlier = [line for line in section_lines(issue["body"], "## Proof") if line.strip()]
    added = [line for line in dict.fromkeys(f"- {p}" for p in proof) if line not in earlier]
    write_body(args, issue, "## Proof", "\n".join([*earlier, *added]), base=with_derived_ticks(evidence))
    if issue["state"] == "OPEN":
        gh("issue", "close", str(args.issue), "--repo", args.repo, "--reason", "completed")
    return read_back(args, "completed", "## Proof")


def reran(args):
    issue = read_issue(args.repo, args.issue)
    ran, saw = " ".join(args.ran.split()), " ".join(args.saw.split())
    heading, lines = reproduction(issue["body"])
    if not heading:
        print(f"#{args.issue} has no reproduction section; record its proof with 'completed --proof'",
              file=sys.stderr)
        return EXIT_FINDINGS
    if not ran or not saw:
        print("a rerun records what you ran and what you saw it do", file=sys.stderr)
        return EXIT_FINDINGS
    commands = reproduction_commands(lines)
    if not runs_reproduction(ran, commands):
        print(f"'{ran}' is not #{args.issue}'s reproduction. Rerun what '{heading}' runs, one of:"
              f" {', '.join(commands)}. A test that passes elsewhere does not show this bug is gone.",
              file=sys.stderr)
        return EXIT_FINDINGS
    write_body(args, issue, RERUN_HEADING,
               f"- Ran: {ran}\n- Saw: {saw}\n- Result: {RESULTS[args.result]}")
    if recorded_rerun(read_issue(args.repo, args.issue)["body"]) is None:
        print(f"read back #{args.issue}: its body has no '{RERUN_HEADING}' section", file=sys.stderr)
        return EXIT_FINDINGS
    if args.result != "fixed":
        print(f"Recorded on #{args.issue}: its reproduction still fails. It stays open until a rerun shows it"
              " fixed, even with every test passing.")
        return EXIT_FINDINGS
    print(f"Recorded on #{args.issue}: its reproduction no longer fails.")
    return 0


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
    if refuse_open_pieces(args, issue):
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
    if refuse_open_pieces(args, issue):
        return EXIT_FINDINGS
    write_body(args, issue, "## Not planned", f"The owner decided: {said}")
    gh("issue", "close", str(args.issue), "--repo", args.repo, "--reason", "not planned")
    return read_back(args, "not-planned", "## Not planned")


def sync(args):
    issue = read_issue(args.repo, args.issue)
    evidence, found = assess(args, issue)
    updated = with_derived_ticks(evidence)
    if updated != (issue["body"] or ""):
        gh("issue", "edit", str(args.issue), "--repo", args.repo, "--body-file", "-", stdin=updated)
    proved = sum(1 for line in checklist(updated) if line.ticked)
    print(f"#{args.issue}: {proved} of {len(checklist(updated))} lines proved; boxes set to match.")
    print_findings(found)
    return EXIT_FINDINGS if found else 0


ZERO = "0" * 40


def pre_push(args):
    """Refuse a push to the landing branch that would close an issue GitHub-side
    while the issue cannot close."""
    args.repo = remote_slug(args.url)
    if args.repo is None:
        return 0
    branch = landing_branch(args)
    refused = False
    for update in sys.stdin.read().splitlines():
        local_ref, local_sha, remote_ref, remote_sha = (update.split() + ["", "", "", ""])[:4]
        if local_sha == ZERO or remote_ref != f"refs/heads/{branch}":
            continue
        span = [local_sha, "--not", f"--remotes={args.remote}"] if remote_sha == ZERO else [f"{remote_sha}..{local_sha}"]
        pushed = commits_of(args.checkout, *span)
        for number in sorted({n for _, message in pushed for n in closed_issues(message, args.repo)}):
            issue = read_issue(args.repo, number)
            _, found = assess(args, issue, pushed)
            if found:
                refused = True
                print(f"This push says 'Closes #{number}', and GitHub would close it now, but it cannot close:",
                      file=sys.stderr)
                for _, message in found:
                    print(f"  - {message}", file=sys.stderr)
    if refused:
        print(RULE, file=sys.stderr)
        print("Say 'Part of #N: <line id>' instead, or finish what is listed, then push again.", file=sys.stderr)
    return EXIT_FINDINGS if refused else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    parsers = {name: commands.add_parser(name)
               for name in ("ready", "sync", "reran", "completed", "duplicate", "out-of-date", "not-planned")}
    for sub in parsers.values():
        sub.add_argument("--repo", required=True)
        sub.add_argument("--issue", type=int, required=True)
    parsers["pre-push"] = commands.add_parser("pre-push")
    parsers["pre-push"].add_argument("remote")
    parsers["pre-push"].add_argument("url")
    for sub in parsers.values():
        sub.add_argument("--checkout", default=".")
        sub.add_argument("--branch")
    parsers["reran"].add_argument("--ran", required=True)
    parsers["reran"].add_argument("--saw", required=True)
    parsers["reran"].add_argument("--result", choices=sorted(RESULTS), required=True)
    parsers["completed"].add_argument("--proof", action="append", required=True)
    parsers["duplicate"].add_argument("--of", type=int, required=True)
    parsers["out-of-date"].add_argument("--evidence", required=True)
    parsers["not-planned"].add_argument("--owner-said", required=True)
    args = parser.parse_args(argv)
    handlers = {"ready": ready, "sync": sync, "pre-push": pre_push, "reran": reran, "completed": completed, "duplicate": duplicate,
                "out-of-date": out_of_date, "not-planned": not_planned}
    try:
        return handlers[args.command](args)
    except RuntimeError as error:
        print(error, file=sys.stderr)
        return EXIT_UNREADABLE


if __name__ == "__main__":
    sys.exit(main())
