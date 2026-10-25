"""Write a release's notes: a plain summary first, then the changelog section under Nitty-gritty.

Usage: python3 scripts/release_notes.py VERSION [--changelog CHANGELOG.md] [--readme README.md]

The summary names each new skill with when to use it, taken from its row in the
README catalog, then the retired skills, the improved skills and the repository changes.
The changelog's own section for VERSION follows unchanged.
"""

import argparse
import re
import sys
from pathlib import Path

SKILL = re.compile(r"\*\*`([a-z0-9-]+)`\*\*|^([a-z0-9-]+):")
CATALOG_ROW = re.compile(r"^\| \[([a-z0-9-]+)\]\([^)]*\) \| (.+?) \| .* \|$")
KINDS = {"### Major Changes": "major", "### Minor Changes": "minor", "### Patch Changes": "patch"}


def section(changelog, version):
    """The lines under `## VERSION`, up to the next version heading."""
    lines = changelog.splitlines()
    try:
        start = lines.index(f"## {version}") + 1
    except ValueError:
        raise SystemExit(f"CHANGELOG has no '## {version}' section")
    end = next((i for i in range(start, len(lines)) if lines[i].startswith("## ")), len(lines))
    body = lines[start:end]
    while body and not body[0].strip():
        body = body[1:]
    return body


def entries(lines):
    """(kind, first line of the entry's text) for every changelog entry."""
    kind, found = None, []
    for line in lines:
        if line in KINDS:
            kind = KINDS[line]
        elif line.startswith("- ") and kind:
            text = re.sub(r"^- \[`[0-9a-f]+`\]\([^)]*\) ", "", line)
            found.append((kind, re.sub(r"^Thanks \[@[^\]]+\]\([^)]*\)! - ", "", text)))
    return found


def skill_of(text):
    match = SKILL.search(text)
    return (match.group(1) or match.group(2)) if match else None


def problems(readme):
    """Each catalog skill's 'Use it when' sentence, by name."""
    found = {}
    for line in readme.splitlines():
        match = CATALOG_ROW.match(line)
        if match:
            found[match.group(1)] = match.group(2)
    return found


def notes(version, changelog, readme):
    lines = section(changelog, version)
    known = problems(readme)
    added, removed, improved, repository = [], [], [], 0
    for kind, text in entries(lines):
        name = skill_of(text)
        match (kind, name):
            case ("minor", str()) if text.startswith("Ship "):
                added.append(name)
            case ("major", str()) if text.startswith("Remove "):
                removed.append(name)
            case (_, str()) if name in known:
                improved.append(name)
            case _:
                repository += 1
    out = [f"## What's in v{version}", ""]
    if added:
        out += ["**New skills**", "", "| Skill | Use it when |", "|---|---|"]
        out += [f"| **{n}** | {known.get(n, '')} |" for n in added] + [""]
    if removed:
        out += ["**Retired:** " + ", ".join(removed) + ".", ""]
    if improved:
        out += ["**Improved:** " + ", ".join(dict.fromkeys(n for n in improved if n not in added)) + ".", ""]
    if repository:
        out += [f"**Repository:** {repository} change{'s' if repository != 1 else ''} to installing, linking and the catalog.", ""]
    out += ["## Nitty-gritty", ""] + [l.replace("### ", "#### ", 1) if l.startswith("### ") else l for l in lines]
    return "\n".join(out).rstrip() + "\n"


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("version")
    parser.add_argument("--changelog", type=Path, default=Path("CHANGELOG.md"))
    parser.add_argument("--readme", type=Path, default=Path("README.md"))
    args = parser.parse_args(argv)
    sys.stdout.write(notes(args.version, args.changelog.read_text(), args.readme.read_text()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
