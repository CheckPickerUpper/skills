"""Which checklist lines of an issue are proved, and which left its body without a record.

A checklist line is done only when something checkable proves it, never because
its box was ticked by hand:

- a landed commit names the line: `Part of #N: <line id>` (or `Closes #N: <id>`,
  several ids separated by commas);
- the line ends with a commit hash, `(abc1234)`, of a landed commit that names #N;
- a `## Proof` line `- <line id>: <link>` records a link a person can open;
- on a decision issue, the `## Decision` section answers it.

A line id is the lowercase word before the first colon: `- [ ] cleanse: Cleanse
effects`. Every line that ever appeared in the body, read from its edit history,
must still be there, be proved, or be recorded under `## Checklist changes` as
`- <id or text>: moved to #M` (and found in #M) or `- <id or text>: dropped, <reason>`.
"""

import difflib
import re
from dataclasses import dataclass

FENCE = re.compile(r"^\s*(```|~~~)")
HEADING = re.compile(r"^#{1,6} ")
BOX = re.compile(r"^\s*[-*+] \[(?P<mark>[ xX])\] (?P<text>.+)$")
ID = r"[a-z0-9][a-z0-9-]*"
LINE_ID = re.compile(rf"^(?P<id>{ID}):\s+\S")
ID_PREFIX = re.compile(rf"^{ID}:\s+")
LINE_SHA = re.compile(r"\((?P<sha>[0-9a-f]{7,40})\)\s*$")
CHANGE = re.compile(r"^\s*[-*+] (?P<key>.+?): (?:moved to #(?P<to>\d+)|dropped[,:]?\s*(?P<why>.*))\s*$")
PROOF_LINE = re.compile(rf"^\s*[-*+] (?P<id>{ID}):\s*(?P<evidence>.*https?://\S+.*)$")
CLOSING = re.compile(r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s*:?\s+(?P<ref>(?:[\w.-]+/[\w.-]+)?#\d+)",
                     re.IGNORECASE)
REWORD_SIMILARITY = 0.6


@dataclass(frozen=True)
class Line:
    ticked: bool
    text: str
    line_id: str | None
    sha: str | None

    @property
    def key(self):
        return self.line_id or self.text

    @property
    def wording(self):
        """The text without its line id, so a line that gains an id keeps its wording."""
        return ID_PREFIX.sub("", self.text, count=1) if self.line_id else self.text


def checklist(body):
    """The '- [ ]' and '- [x]' lines outside code fences."""
    found, fenced = [], False
    for raw in (body or "").splitlines():
        if FENCE.match(raw):
            fenced = not fenced
            continue
        match = None if fenced else BOX.match(raw)
        if match:
            text = match["text"].strip()
            line_id, sha = LINE_ID.match(text), LINE_SHA.search(text)
            found.append(Line(match["mark"] != " ", text, line_id and line_id["id"], sha and sha["sha"]))
    return found


def section_lines(body, heading):
    lines, inside = [], False
    for raw in (body or "").splitlines():
        if HEADING.match(raw):
            inside = raw.strip().lower() == heading.lower()
            continue
        if inside:
            lines.append(raw)
    return lines


def issue_ref(number, repo):
    return rf"(?:(?<=\s)|(?<=\()|^)(?:{re.escape(repo)})?#{number}(?!\d)"


def mentions(message, number, repo):
    return re.search(issue_ref(number, repo), message, re.IGNORECASE | re.MULTILINE) is not None


def claimed_ids(message, number, repo):
    """The line ids a commit message names for issue #number."""
    found = set()
    pattern = issue_ref(number, repo) + rf":\s*(?P<ids>{ID}(?:\s*,\s*{ID})*)"
    for match in re.finditer(pattern, message, re.IGNORECASE | re.MULTILINE):
        found.update(part.strip() for part in match["ids"].split(","))
    return found


def closed_issues(message, repo):
    """The issue numbers of this repository that a commit message closes on push."""
    numbers = set()
    for match in CLOSING.finditer(message):
        ref = match["ref"]
        prefix, _, number = ref.partition("#")
        if not prefix or prefix.lower() == repo.lower():
            numbers.add(int(number))
    return numbers


@dataclass(frozen=True)
class Evidence:
    """What can prove the lines of issue #number."""
    number: int
    repo: str
    commits: tuple  # (sha, message) pairs on the landing branch or being pushed
    body: str
    decided: bool

    def proof_of(self, line):
        """How the line is proved, or None."""
        if self.decided:
            return "the ## Decision section"
        for sha, message in self.commits:
            if line.line_id and line.line_id in claimed_ids(message, self.number, self.repo):
                return f"commit {sha[:10]}"
        if line.sha:
            for sha, message in self.commits:
                if sha.startswith(line.sha) and mentions(message, self.number, self.repo):
                    return f"commit {sha[:10]}"
        if line.line_id:
            for raw in section_lines(self.body, "## Proof"):
                match = PROOF_LINE.match(raw)
                if match and match["id"] == line.line_id:
                    return f"the ## Proof link {match['evidence'].strip()}"
        return None


def line_findings(evidence):
    """(kind, message) for every line nothing proves: an unticked line is open work,
    a ticked one was ticked by hand."""
    me, found = f"#{evidence.number}", []
    for line in checklist(evidence.body):
        if evidence.proof_of(line):
            continue
        if not line.ticked:
            found.append(("unticked", f"{me} has an open line: {line.text}"))
        elif line.line_id:
            found.append(("ticked-unproven", f"{me} line '{line.line_id}' is ticked but no landed commit says"
                          f" 'Part of {me}: {line.line_id}' and no ## Proof link names it"))
        else:
            found.append(("ticked-unproven", f"{me} line '{line.text}' is ticked with no line id and no commit"
                          " hash; give it an id and land the commit that names it, or end it with the hash of"
                          " the landed commit that did it"))
    return found


def changes(body):
    """The recorded moves and drops under '## Checklist changes': key -> (moved_to, why)."""
    recorded = {}
    for raw in section_lines(body, "## Checklist changes"):
        match = CHANGE.match(raw)
        if match:
            recorded[match["key"].strip()] = (int(match["to"]) if match["to"] else None, match["why"])
    return recorded


def reworded(line, current):
    """Whether an id-less line that left the body lives on as a current line, reworded or
    given a line id."""
    return any(difflib.SequenceMatcher(None, line.text, other.wording).ratio() >= REWORD_SIMILARITY
               for other in current)


def removed_findings(evidence, revisions, read_body):
    """(kind, message) for every line an earlier revision had that the body lost
    without proof or a record. read_body(number) returns another issue's body."""
    me = f"#{evidence.number}"
    current = checklist(evidence.body)
    keys = {line.key for line in current}
    recorded = changes(evidence.body)
    seen, found = set(), []
    for revision in revisions:
        for line in checklist(revision):
            if line.key in keys or line.key in seen:
                continue
            seen.add(line.key)
            if (line.line_id is None and reworded(line, current)) or evidence.proof_of(line):
                continue
            moved_to, why = recorded.get(line.key, (None, None))
            if moved_to is not None:
                target = checklist(read_body(moved_to))
                if not any(other.key == line.key for other in target):
                    found.append(("moved-missing", f"{me} records '{line.key}' as moved to #{moved_to},"
                                  f" but #{moved_to} has no line '{line.key}'"))
            elif not why:
                found.append(("removed-unrecorded", f"{me} lost the line '{line.text}' with no proof and no"
                              f" record; restore it, or add '- {line.key}: moved to #M' or"
                              f" '- {line.key}: dropped, <reason>' under '## Checklist changes'"))
    return found


def with_derived_ticks(evidence):
    """The body with every box set to what the evidence proves."""
    out, fenced = [], False
    for raw in (evidence.body or "").splitlines():
        if FENCE.match(raw):
            fenced = not fenced
        match = None if fenced else BOX.match(raw)
        if match:
            line = checklist(raw)[0]
            mark = "x" if evidence.proof_of(line) else " "
            raw = raw[:match.start("mark")] + mark + raw[match.end("mark"):]
        out.append(raw)
    return "\n".join(out) + ("\n" if (evidence.body or "").endswith("\n") else "")
