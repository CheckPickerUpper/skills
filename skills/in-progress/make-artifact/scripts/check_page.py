"""Refuse an Artifact page that shows uncoloured code or silently drops content.

Reads the HTML page named on the command line. Prints each finding and exits 1
while any remain; exits 0 when none do and 2 when the page cannot be read.

Every run: a code block (`<pre>`) must be syntax-coloured. It counts as
coloured when it holds styled child elements, or when it or its `<code>`
carries a class naming a language or highlighter that a script on the page
colours at load.

With `--previous OLD`: a revision must not lose what the last version showed.
Reported as dropped are link targets, issue references, inline code names, table
column headings, and repeated labels (a short text that appeared three or more
times, such as a status chip). Each dropped entry needs a line in the file
given by `--dropped` (default: `<page>.dropped.txt`), written as
`<entry>: <where it moved, or the reader's words asking for it gone>`.
"""

import argparse
from collections import Counter
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
import re
import sys

EXIT_FINDINGS = 1
EXIT_UNREADABLE = 2

VOID_TAGS = {"br", "hr", "img", "input", "meta", "link", "wbr", "source", "col"}
UNSEEN_TAGS = {"script", "style", "template", "title"}
COLOURED_BY_SCRIPT = re.compile(r"lang|highlight|hljs|prism|shiki", re.IGNORECASE)
ISSUE_REFERENCE = re.compile(r"(?<![\w&])#\d+\b")
REPEATED_LABEL_MAX_WORDS = 3
REPEATED_LABEL_MIN_COUNT = 3


@dataclass
class OpenElement:
    tag: str
    has_child_element: bool = False
    text: list[str] = field(default_factory=list)


@dataclass
class OpenCodeBlock:
    line: int
    coloured: bool
    text: list[str] = field(default_factory=list)


@dataclass
class Page:
    links: set[str] = field(default_factory=set)
    issue_references: set[str] = field(default_factory=set)
    code_names: set[str] = field(default_factory=set)
    column_headings: set[str] = field(default_factory=set)
    leaf_texts: Counter = field(default_factory=Counter)
    uncoloured_code_blocks: list[tuple[int, str]] = field(default_factory=list)

    def repeated_labels(self):
        return {
            text for text, count in self.leaf_texts.items()
            if count >= REPEATED_LABEL_MIN_COUNT
            and len(text.split()) <= REPEATED_LABEL_MAX_WORDS
        }

    def shown(self):
        """Everything a later version is held to, keyed by how it is named."""
        entries = {}
        for kind, values in (
            ("link", self.links),
            ("issue", self.issue_references),
            ("code name", self.code_names),
            ("column", self.column_headings),
            ("repeated label", self.repeated_labels()),
        ):
            for value in values:
                entries.setdefault(value.casefold(), (kind, value))
        return entries

    def all_text(self):
        return " ".join(self.leaf_texts).casefold()


def squeeze(text):
    return " ".join(text.split())


class PageReader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.page = Page()
        self.open_elements: list[OpenElement] = []
        self.code_block: OpenCodeBlock | None = None
        self.unseen_depth = 0

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag in UNSEEN_TAGS:
            self.unseen_depth += 1
            return
        if tag == "a" and attributes.get("href", "").startswith("http"):
            self.page.links.add(attributes["href"])
        classes = attributes.get("class") or ""
        if tag == "pre":
            self.code_block = OpenCodeBlock(
                self.getpos()[0], bool(COLOURED_BY_SCRIPT.search(classes))
            )
        elif self.code_block is not None:
            if tag == "code":
                self.code_block.coloured |= bool(COLOURED_BY_SCRIPT.search(classes))
            elif classes or attributes.get("style"):
                self.code_block.coloured = True
        if tag in VOID_TAGS:
            return
        if self.open_elements:
            self.open_elements[-1].has_child_element = True
        self.open_elements.append(OpenElement(tag))

    def handle_endtag(self, tag):
        if tag in UNSEEN_TAGS:
            self.unseen_depth = max(0, self.unseen_depth - 1)
            return
        if tag == "pre" and self.code_block is not None:
            block, self.code_block = self.code_block, None
            excerpt = squeeze("".join(block.text))
            if excerpt and not block.coloured:
                self.page.uncoloured_code_blocks.append((block.line, excerpt[:60]))
        while self.open_elements:
            element = self.open_elements.pop()
            self.record(element)
            if element.tag == tag:
                break

    def handle_data(self, data):
        if self.unseen_depth:
            return
        if self.code_block is not None:
            self.code_block.text.append(data)
        for element in self.open_elements:
            element.text.append(data)
        self.page.issue_references.update(ISSUE_REFERENCE.findall(data))

    def record(self, element):
        text = squeeze("".join(element.text))
        if not text:
            return
        if element.tag == "th":
            self.page.column_headings.add(text)
        if element.tag == "code" and self.code_block is None:
            self.page.code_names.add(text)
        if not element.has_child_element:
            self.page.leaf_texts[text] += 1

    def close(self):
        super().close()
        while self.open_elements:
            self.record(self.open_elements.pop())


def read_page(path):
    reader = PageReader()
    reader.feed(path.read_text(encoding="utf-8"))
    reader.close()
    return reader.page


def read_accounted(path):
    if not path.exists():
        return set()
    accounted = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        entry, separator, reason = line.rpartition(": ")
        if separator and reason.strip():
            accounted.add(squeeze(entry).casefold())
    return accounted


def dropped_entries(previous, current, accounted):
    kept = current.shown()
    current_text = current.all_text()
    dropped = []
    for key, (kind, value) in sorted(previous.shown().items()):
        if key in kept or key in accounted:
            continue
        # A link is its target; everything else may survive reworded into
        # running text, so it is dropped only when the words are gone.
        if kind != "link" and key in current_text:
            continue
        dropped.append((kind, value))
    return dropped


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("page", type=Path)
    parser.add_argument("--previous", type=Path, help="the last published version")
    parser.add_argument("--dropped", type=Path, help="file accounting for dropped entries")
    arguments = parser.parse_args()

    try:
        current = read_page(arguments.page)
        previous = read_page(arguments.previous) if arguments.previous else None
    except (OSError, UnicodeDecodeError) as error:
        print(f"cannot read the page: {error}")
        return EXIT_UNREADABLE

    findings = 0
    if current.uncoloured_code_blocks:
        findings += len(current.uncoloured_code_blocks)
        print(
            f"{len(current.uncoloured_code_blocks)} code blocks have no syntax "
            "colouring. Rule: code on a page is coloured like code in an editor."
        )
        for line, excerpt in current.uncoloured_code_blocks:
            print(f"  line {line}: {excerpt}")

    if previous is not None:
        dropped_file = arguments.dropped or arguments.page.with_name(
            arguments.page.name + ".dropped.txt"
        )
        dropped = dropped_entries(previous, current, read_accounted(dropped_file))
        if dropped:
            findings += len(dropped)
            print(
                f"{len(dropped)} things the previous version showed are gone. Rule: "
                "a revision keeps everything the reader did not ask to remove. "
                f"Restore each, or add `<entry>: <reason>` to {dropped_file}."
            )
            for kind, value in dropped:
                print(f"  {kind}: {value}")

    if findings:
        return EXIT_FINDINGS
    print("page check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
