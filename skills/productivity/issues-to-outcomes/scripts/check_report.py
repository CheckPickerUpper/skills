"""Refuse a work report whose lines open with a tracker reference.

Reads the report from the file named on the command line, or from standard
input. Prints every line that opens with an issue or pull-request reference
and exits 1 while any remain; exits 0 when none do and 2 for an empty report.
Lines inside a fenced code block are quoted material and are not judged.
"""

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import sys

EXIT_FINDINGS = 1
EXIT_EMPTY = 2

FENCE = re.compile(r"\s*(```|~~~)")
# List bullets, numbering, task boxes, quote marks, table bars, headings and
# emphasis: everything a line may carry before its first word.
LINE_PREFIX = re.compile(r"^(?:\s|[-*+>|]\s|#+\s|\d+[.)]\s|\[[ xX]\]\s|[*_`])*")
LEADING_REFERENCE = re.compile(
    r"""\[?(?:
        (?:(?i:PR|MR|issue|pull\ request)\s+)?(?:[\w.-]+/[\w.-]+)?\#\d+
        | https?://\S+/(?:issues|pull|pulls|merge_requests)/\d+
        | [A-Z][A-Z0-9]+-\d+\b
    )""",
    re.VERBOSE,
)

RULE = (
    "A reader cannot tell what changed for them from a number and a title.\n"
    "Rewrite each line as what the reader notices: their situation, what happened\n"
    "before, and what happens now. Move the reference to the end of the sentence."
)


@dataclass(frozen=True)
class ReferenceLedLine:
    number: int
    text: str


def opens_with_reference(line: str) -> bool:
    body = line[LINE_PREFIX.match(line).end():]
    return LEADING_REFERENCE.match(body) is not None


def reference_led_lines(report: str) -> list[ReferenceLedLine]:
    found: list[ReferenceLedLine] = []
    in_fence = False
    for number, line in enumerate(report.splitlines(), start=1):
        if FENCE.match(line):
            in_fence = not in_fence
        elif not in_fence and opens_with_reference(line):
            found.append(ReferenceLedLine(number, line.strip()))
    return found


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("report", nargs="?", type=Path, help="report file; standard input when omitted")
    arguments = parser.parse_args()
    report = sys.stdin.read() if arguments.report is None else arguments.report.read_text(encoding="utf-8")
    if not report.strip():
        print("The report is empty; pass the draft as a file or on standard input.", file=sys.stderr)
        sys.exit(EXIT_EMPTY)
    found = reference_led_lines(report)
    if not found:
        print("No line opens with a tracker reference.")
        return
    count = "1 line opens" if len(found) == 1 else f"{len(found)} lines open"
    print(f"{count} with a tracker reference.\n{RULE}\n")
    for finding in found:
        print(f"  line {finding.number}: {finding.text}")
    sys.exit(EXIT_FINDINGS)


if __name__ == "__main__":
    main()
