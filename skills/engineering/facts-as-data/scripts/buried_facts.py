#!/usr/bin/env python3
"""Find facts buried in logic, and check that a census records a decision for each.

    buried_facts.py [--record CENSUS.tsv] [--since REV] [--include-tests] PATH...
        Lists every lead in the source files under PATH: names joined in a string
        alternation (a regex of callees, match arms joined on literals, name checks
        chained with || or `or`), a literal list of names, and a run of nearby
        branches keyed by a literal; the thresholds follow this text. With --record, a
        lead is settled by a census row naming its file or its file:line. With --since,
        only lines added since REV are read, which is the review of one diff. Exits 1
        while a lead is unsettled or a row is incomplete.

The census format is in references/census-format.md beside this skill.
"""

import argparse
import csv
import re
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum, StrEnum
from pathlib import Path

EXIT_FINDINGS = 1
EXIT_UNREADABLE = 2
MIN_ALTERNATIVES = 3
MIN_LIST = 4
MIN_BRANCHES = 4
BRANCH_GAP = 12
NONE = "-"
HEADER = ("site", "group", "meaning", "decision", "table", "readers", "check", "reason")

RULE = (
    "A fact several readers need lives in one table they all read, not inside one"
    " branch of logic. Record each lead in the census: table (it moves into a table),"
    " is-table (it already is the shared table), or not-data with the reason its"
    " variation has no real form."
)

SOURCE_SUFFIXES = {
    ".c", ".cc", ".cjs", ".cpp", ".cs", ".dart", ".ex", ".exs", ".go", ".h", ".hpp", ".hs",
    ".java", ".js", ".jsx", ".kt", ".lua", ".luau", ".mjs", ".php", ".py", ".rb", ".rs",
    ".scala", ".sh", ".swift", ".ts", ".tsx",
}
TEST_PATH = re.compile(
    r"(^|/)(tests?|spec|fixtures?|__tests__)/|(^|/)test_[^/]*$|_test\.[^/]*$|\.(test|spec)\.[^/]*$")
STRING = r'"(?:[^"\\\n]|\\.)*"|\'(?:[^\'\\\n]|\\.)*\''
NAME = r"[A-Za-z_](?:[\w:]|\\?\.)*"
STRINGS = re.compile(STRING)
ALTERNATION = re.compile(
    rf"(?<![\w|]){NAME}(?:\|{NAME}){{{MIN_ALTERNATIVES - 1},}}(?![\w|])")
JOINED_LITERALS = re.compile(rf"(?:{STRING})(?:\s*\|\s*(?:{STRING})){{{MIN_ALTERNATIVES - 1},}}")
LITERAL_LIST = re.compile(
    rf"[\[({{]\s*(?:(?:{STRING})\s*,\s*(?:(?:#|//)[^\n]*\n\s*)?){{{MIN_LIST - 1},}}"
    rf"(?:{STRING})\s*,?\s*[\])}}]")
NAME_LIKE = re.compile(r"[\w.:/@-]+")
OR = re.compile(r"\|\||\bor\b")
BRANCH = re.compile(
    rf"^\s*(?:(?:case|when)\s+(?:{STRING})"
    rf"|(?:\}}\s*)?(?:else\s+if|elif|if)\s*\(?\s*[\w.]+\s*===?\s*(?:{STRING})"
    rf"|(?:{STRING})(?:\s*\|\s*(?:{STRING}))*\s*(?:=>|->))")


class Kind(StrEnum):
    ALTERNATION = "alternation"
    LIST = "list"
    BRANCHES = "branches"


class Decision(Enum):
    TABLE = "table"
    IS_TABLE = "is-table"
    NOT_DATA = "not-data"


@dataclass(frozen=True)
class Lead:
    path: str
    line: int
    kind: Kind
    text: str

    def __str__(self):
        return f"{self.path}:{self.line} {self.kind}  {self.text}"


def line_of(text, offset):
    return text.count("\n", 0, offset) + 1


def leads(path, text):
    """Every place in one file where a fact looks written into logic: leads, not findings."""
    lines = text.splitlines()
    found = []
    for number, line in enumerate(lines, 1):
        literals = STRINGS.findall(line)
        chained = (len(OR.findall(line)) >= MIN_ALTERNATIVES - 1
                   and sum(bool(NAME_LIKE.fullmatch(lit[1:-1])) for lit in literals) >= MIN_ALTERNATIVES)
        if chained or JOINED_LITERALS.search(line) or any(
                ALTERNATION.search(literal[1:-1]) for literal in literals):
            found.append(Lead(path, number, Kind.ALTERNATION, line.strip()))
    for match in LITERAL_LIST.finditer(text):
        literals = [literal[1:-1] for literal in STRINGS.findall(match.group(0))]
        if all(NAME_LIKE.fullmatch(literal) for literal in literals):
            number = line_of(text, match.start())
            found.append(Lead(path, number, Kind.LIST, lines[number - 1].strip()))
    run = []
    for number in [n for n, line in enumerate(lines, 1) if BRANCH.match(line)] + [None]:
        if run and (number is None or number - run[-1] > BRANCH_GAP):
            if len(run) >= MIN_BRANCHES:
                found.append(Lead(path, run[0], Kind.BRANCHES, f"{len(run)} branches keyed by literals"))
            run = []
        if number is not None:
            run.append(number)
    return sorted(found, key=lambda lead: (lead.line, lead.kind))


def source_files(paths, include_tests):
    listed = subprocess.run(["git", "ls-files", "-co", "--exclude-standard", "--", *paths],
                            capture_output=True, text=True)
    if listed.returncode == 0:
        files = listed.stdout.splitlines()
    else:
        files = [str(p) for root in paths for p in
                 ([Path(root)] if Path(root).is_file() else Path(root).rglob("*"))]
    return sorted(f for f in files if Path(f).suffix in SOURCE_SUFFIXES and Path(f).is_file()
                  and (include_tests or not TEST_PATH.search(f)))


def added_lines(rev, path):
    """Line numbers in the working copy of path that the diff from rev adds."""
    diff = subprocess.run(["git", "diff", "-U0", rev, "--", path],
                          capture_output=True, text=True, check=True).stdout
    added = set()
    for start, count in re.findall(r"^@@ -\S+ \+(\d+)(?:,(\d+))? @@", diff, re.MULTILINE):
        added.update(range(int(start), int(start) + int(count or 1)))
    return added


def read_record(path):
    with open(path, encoding="utf-8", newline="") as stream:
        rows = csv.reader(stream, delimiter="\t")
        header = tuple(next(rows, ()))
        if header != HEADER:
            raise ValueError(f"{path}: header {header!r} must be {HEADER!r}")
        return [dict(zip(HEADER, (field.strip() for field in row))) for row in rows if row]


def row_findings(row):
    site = row.get("site") or "?"
    missing = [field for field in HEADER if not row.get(field)]
    if missing:
        return [f"{site}: empty {', '.join(missing)} (write {NONE} for none)"]
    found = [f"{site}: {field} must say what the fact is" for field in ("group", "meaning")
             if row[field] == NONE]
    try:
        decision = Decision(row["decision"])
    except ValueError:
        return [*found, f"{site}: decision {row['decision']!r} must be table, is-table or not-data"]
    match decision:
        case Decision.TABLE | Decision.IS_TABLE:
            found += [f"{site}: a {decision.value} row names its {field}"
                      for field in ("table", "readers", "check") if row[field] == NONE]
        case Decision.NOT_DATA:
            if row["reason"] == NONE:
                found.append(f"{site}: a not-data row gives the reason its variation has no real form")
            if any(row[field] != NONE for field in ("table", "readers", "check")):
                found.append(f"{site}: a not-data row names no table, readers or check")
    return found


def record_findings(rows, found_leads):
    """What keeps the census open: a lead no row settles, and every incomplete row."""
    sites = {row.get("site") for row in rows}
    unsettled = [f"unsettled lead {lead}" for lead in found_leads
                 if lead.path not in sites and f"{lead.path}:{lead.line}" not in sites]
    return unsettled + [finding for row in rows for finding in row_findings(row)]


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(f"Thresholds: {MIN_ALTERNATIVES} or more names in an alternation or chain,"
                f" {MIN_LIST} or more in a list, {MIN_BRANCHES} or more branches no more than"
                f" {BRANCH_GAP} lines apart."))
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--record", help="census TSV that settles each lead")
    parser.add_argument("--since", help="read only lines added since this revision")
    parser.add_argument("--include-tests", action="store_true")
    args = parser.parse_args(argv)
    try:
        rows = read_record(args.record) if args.record else []
        found = []
        for path in source_files(args.paths, args.include_tests):
            file_leads = leads(path, Path(path).read_text(encoding="utf-8", errors="replace"))
            if args.since:
                added = added_lines(args.since, path)
                file_leads = [lead for lead in file_leads if lead.line in added]
            found += file_leads
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"unreadable: {error}", file=sys.stderr)
        return EXIT_UNREADABLE
    findings = record_findings(rows, found)
    for finding in findings:
        print(finding)
    if findings:
        print(f"\n{len(findings)} open. {RULE}")
        return EXIT_FINDINGS
    print(f"No unsettled leads. {RULE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
