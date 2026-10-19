# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright==1.58.0"]
# ///
"""Render a diagram in light and dark themes and refuse what a reader would trip on.

Usage: uv run check_diagram.py <diagram.html | diagram.svg>
           [--out DIR] [--words FILE] [--accepted FILE]

Opens the file in a headless browser, writes one PNG per diagram per theme
(<stem>.light.png and <stem>.dark.png, next to the file or in --out), and
measures every <svg> that uses the drawing vocabulary in diagram_geometry.js.
Prints each finding under the rule it breaks and exits 1 while any remain,
0 when none do, and 2 when the file cannot be opened or no browser starts.

The words file (default <stem>.words.txt beside the diagram) is required: it
records the cold read of every word on the drawing and the owner's wording
corrections, one per line:
    import feed facts => copy official stats
    Project Falcon =>
A phrase on the left may not appear in the diagram as whole words (any case;
"round" does not catch "background"); an empty right side means
the name is dropped. Lines starting with # are ignored.

Most rules are hard: a finding is fixed in the drawing. Four are judgment
calls with legitimate exceptions (a row over 32 characters, a row joining two
things with "and", two arrows that cross, a non-loop arrow that points up or
back). One of those can stand when
the drawing is clearer that way and the accepted file (default
<stem>.accepted.txt) holds the finding as printed and the reason:
    arrow "A" → "B" crosses the arrow "C" → "D" | the two lanes must both reach "B"
An accepted line that matches no current judgment finding is itself a finding,
so the file stays true as the drawing changes.
"""

import argparse
from pathlib import Path
import re
import sys

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

EXIT_FINDINGS = 1
EXIT_UNUSABLE = 2
VIEWPORT = {"width": 1280, "height": 900}
GEOMETRY = (Path(__file__).resolve().parent / "diagram_geometry.js").read_text()

RULES = {
    "size": "Text is 15px or larger where it is drawn.",
    "overlap": "Every label has its own space: no text overlaps another text,"
    " sits on an arrow, or spills out of its shape or the drawing.",
    "box": "A box holds a short title plus at most two short lines, or a titled checklist:"
    " subheadings ending in ':' and one '• ' bullet per concrete thing. Show more mechanism"
    " as more nodes.",
    "rowlength": "Judgment: a row in a box stays short (32 characters or fewer).",
    "list": "A box row holds one item. Two or more items are bullet rows, never a comma list.",
    "vague": "Judgment: a row names one concrete thing. Two things joined by 'and' with no"
    " specifics ('jerseys and the court') are bullets that each say exactly what: 'each"
    " team's jersey colour', 'which gym'.",
    "twice": "A step is drawn once. Where lanes reach a step both take, they merge into one"
    " shared flow; a step that differs by lane is a decision in it.",
    "end": "An end box says what happens after it: whether and when it can be retried"
    " or left, or what it hands on. A title alone leaves a gap.",
    "example": "Every check shows a real case of what fails it, as a row starting 'e.g.' in the"
    " diamond or in the box its no branch reaches: 'Each time after the one before?' with"
    " 'e.g. Q2 starts before Q1 ends'.",
    "float": "Nothing floats: every node connects to the flow, every arrow"
    " starts and ends on a shape, and every loose text labels an arrow.",
    "decision": "A decision is a diamond with a labelled yes branch and a"
    " labelled no branch, and yes and no colours appear only on those branches.",
    "direction": "Judgment: arrows read left to right and top to bottom; a loop goes back."
    " Arrows back to an earlier level or state mean a rulebook: put it in a table.",
    "crossing": "Judgment: arrows do not cross each other.",
    "through": "An arrow never runs through a box it does not connect.",
    "colour": "Arrow colour means one thing: yes green, no red, data blue, loop amber"
    " dashed, next step grey; one colour per kind; a legend lists exactly the kinds used.",
    "caption": "No caption or note under the diagram. If it needs one, change the diagram.",
    "contrast": "Text reads in both themes: contrast of at least 4.5:1 against what is"
    " behind it, and dark text on light fills.",
    "words": "Every word reads cold to a stranger, and the owner's corrections hold:"
    " a replaced or dropped phrase stays out.",
    "accepted": "Each accepted judgment call names a current judgment finding and gives a reason.",
    "found": "The file holds a diagram drawn in the vocabulary: g.node and g.decision"
    " shapes joined by .arrow elements.",
}


JUDGMENT_RULES = {"rowlength", "vague", "crossing", "direction"}
ACCEPTED_SEPARATOR = " | "


def read_accepted(path):
    """Accepted judgment calls as {finding: reason}; a line with no reason is kept empty."""
    accepted = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        finding, _, reason = line.partition(ACCEPTED_SEPARATOR.strip())
        accepted[finding.strip()] = reason.strip()
    return accepted


def apply_accepted(findings, accepted, accepted_path):
    remaining, standing = [], []
    for finding in findings:
        reason = accepted.get(finding["message"])
        if finding["rule"] in JUDGMENT_RULES and reason:
            standing.append((finding["message"], reason))
        else:
            remaining.append(finding)
    judged = {f["message"] for f in findings if f["rule"] in JUDGMENT_RULES}
    for finding, reason in accepted.items():
        if finding not in judged:
            remaining.append({"rule": "accepted", "message": (
                f'{accepted_path.name} accepts "{finding}", which is not a current judgment finding')})
        elif not reason:
            remaining.append({"rule": "accepted", "message": (
                f'{accepted_path.name} accepts "{finding}" without a reason')})
    return remaining, standing


def read_words(path):
    corrections = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=>" not in line:
            continue
        phrase, replacement = (part.strip() for part in line.split("=>", 1))
        if phrase:
            corrections.append((phrase, replacement))
    return corrections


def word_findings(texts, corrections):
    findings = []
    for phrase, replacement in corrections:
        # Whole words only: a ban on "round" must not catch "background".
        pattern = re.compile(rf"(?<!\w){re.escape(phrase)}(?!\w)", re.IGNORECASE)
        for text in sorted({t for t in texts if pattern.search(t)}):
            fix = f'write "{replacement}"' if replacement else "drop it"
            findings.append({
                "rule": "words",
                "message": f'"{text}" uses "{phrase}"; {fix}',
            })
    return findings


def launch(playwright):
    failures = []
    for options in ({"channel": "chrome"}, {}):
        try:
            return playwright.chromium.launch(**options)
        except PlaywrightError as error:
            failures.append(str(error).splitlines()[0])
    raise RuntimeError(
        "no browser started; install Google Chrome or run"
        " `uv run --with playwright==1.58.0 playwright install chromium`:\n  "
        + "\n  ".join(failures))


def measure(browser, url, scheme, out_dir, stem):
    page = browser.new_page(viewport=VIEWPORT, color_scheme=scheme)
    try:
        page.goto(url)
        page.wait_for_load_state("networkidle")
        result = page.evaluate(GEOMETRY)
        svgs = [
            handle for handle in page.query_selector_all("svg")
            if handle.evaluate("s => !!s.querySelector('.node, .decision')")
        ]
        images = []
        for index, handle in enumerate(svgs):
            suffix = f".{index + 1}" if len(svgs) > 1 else ""
            image = out_dir / f"{stem}{suffix}.{scheme}.png"
            handle.screenshot(path=str(image))
            images.append(image)
        return result, images
    finally:
        page.close()


def report(path, findings, images, standing, accepted_path):
    for image in images:
        print(f"rendered {image}")
    for finding, reason in standing:
        print(f"accepted judgment call: {finding} | {reason}")
    if not findings:
        print(f"{path}: no findings. Now open every rendered image and look at it.")
        return
    print(f"{path}: {len(findings)} finding(s)")
    for rule, statement in RULES.items():
        messages = [f["message"] for f in findings if f["rule"] == rule]
        if messages:
            print(f"\n{statement}")
            for message in messages:
                print(f"  - {message}")
    if any(f["rule"] in JUDGMENT_RULES for f in findings):
        print(f"\nFix each judgment finding, or, when the drawing is clearer as it is, add a line"
              f" to {accepted_path} reading: <finding as printed>{ACCEPTED_SEPARATOR}<why>")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("diagram", type=Path)
    parser.add_argument("--out", type=Path, help="directory for the rendered PNGs")
    parser.add_argument("--words", type=Path, help="wording corrections file")
    parser.add_argument("--accepted", type=Path, help="accepted judgment calls file")
    args = parser.parse_args()

    path = args.diagram.resolve()
    if not path.is_file():
        print(f"{path}: not a file", file=sys.stderr)
        return EXIT_UNUSABLE
    out_dir = (args.out or path.parent).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    words = args.words or path.with_suffix(".words.txt")
    accepted_path = args.accepted or path.with_suffix(".accepted.txt")
    for named, given in ((words, args.words), (accepted_path, args.accepted)):
        if given and not named.is_file():
            print(f"{named}: not a file", file=sys.stderr)
            return EXIT_UNUSABLE

    findings = []
    images = []
    try:
        with sync_playwright() as playwright:
            browser = launch(playwright)
            try:
                seen = set()
                for scheme in ("light", "dark"):
                    result, shots = measure(browser, path.as_uri(), scheme, out_dir, path.stem)
                    images.extend(shots)
                    if not result["diagrams"]:
                        findings.append({"rule": "found", "message": "no diagram found"})
                        break
                    for finding in result["findings"]:
                        key = (finding["rule"], finding["message"])
                        if key in seen:
                            continue
                        seen.add(key)
                        if scheme == "dark":
                            finding = {**finding, "message": "dark theme: " + finding["message"]}
                        findings.append(finding)
                    if scheme == "light" and words.is_file():
                        findings.extend(word_findings(result["texts"], read_words(words)))
                    elif scheme == "light":
                        findings.append({"rule": "words", "message": (
                            f"{words.name} does not exist. Read every word on the drawing as"
                            " someone outside the business who is not technical; replace each"
                            " one they could not read, write each replacement there as"
                            " `old => plain`, and create the file even when nothing changed")})
            finally:
                browser.close()
    except RuntimeError as error:
        print(error, file=sys.stderr)
        return EXIT_UNUSABLE

    accepted = read_accepted(accepted_path) if accepted_path.is_file() else {}
    findings, standing = apply_accepted(findings, accepted, accepted_path)
    report(path, findings, images, standing, accepted_path)
    return EXIT_FINDINGS if findings else 0


if __name__ == "__main__":
    sys.exit(main())
