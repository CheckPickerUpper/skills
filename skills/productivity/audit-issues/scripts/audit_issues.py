"""Audit a GitHub tracker: find hidden open work, suggest causes, and apply an approved plan.

    audit_issues.py scan --repo OWNER/REPO [--milestone TITLE]
        Lists open work hidden under closed issues (exits 1 while any remains),
        milestones with more than 10 top-level issues, groups of issues that look
        like one cause (error text, one bug in several languages, or two shared
        file paths or code names), weaker one-signal leads, and issues whose
        asked-for fix reads like a workaround.
    audit_issues.py index --repo OWNER/REPO [--milestone TITLE] --out FILE
        Writes one line per open issue: the index every batch reads in full.
    audit_issues.py draft --repo OWNER/REPO --title TITLE --body-file FILE [--milestone TITLE] [--parent N]
        Checks one issue before it is filed: refuses while an open issue looks like the
        same cause, the draft asks for a workaround, or it takes its milestone over 10
        causes, until the draft or the milestone records why that does not apply.
    audit_issues.py plan --repo OWNER/REPO --plan PLAN.json [--verdicts FILE ...] --page PAGE.md
        Checks that every open issue in scope has a complete verdict, writes the
        short page the owner approves, and prints the plan's approval code.
        Exits 1 while the plan has findings.
    audit_issues.py apply --repo OWNER/REPO --plan PLAN.json [--verdicts FILE ...] --approved CODE
        Applies the approved plan one verified step at a time. Refuses a plan
        whose files changed since the owner saw its page. Every close runs
        through close-issues' close_issue.py. Safe to rerun after a failure.

Every command reads issues through a local copy kept in
$XDG_CACHE_HOME/checkpickerupper/audit-issues/ (default ~/.cache), refreshed with only the
issues updated since the last run; a changed issue count or an unreadable copy downloads
every issue again and says why on stderr.

The plan format is in references/plan-format.md beside this skill.
"""

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

EXIT_FINDINGS = 1
EXIT_UNREADABLE = 2
MAX_CAUSES = 10
MAX_SHARED = 8
MAX_LEAD = 4
STRONG = {"error": 2, "languages": 2}
DIFFERENT_CAUSE = "Different cause from #{number}:"
NOT_A_WORKAROUND = "Not a workaround:"
OVER_LIMIT_REASON = "More than 10 causes because"

RULE = (
    "Open work stays visible: an issue closes as completed only when nothing under it"
    " is open, a duplicate names its original, a decision closes with its answer in the"
    " body, and an open issue sits under an open parent."
)
FENCE = re.compile(r"^\s*(```|~~~)")
UNTICKED = re.compile(r"^\s*[-*+] \[ \] (?P<text>.+)")
CHECKLIST = re.compile(r"^\s*[-*+] \[[ xX]\] (.+)", re.MULTILINE)
HEADING = re.compile(r"^#{1,6} ")
DECISION_LABEL = re.compile(r"decision", re.IGNORECASE)
ISSUE_FIELDS = """
  id number title url state stateReason body updatedAt
  labels(first: 30) { nodes { name } }
  milestone { title }
  parent { number title url state }
  subIssues(first: 100) { nodes { number title url state } }
  duplicateOf { number url }
"""
FIXES = {
    "closed-parent": "Move each under an open parent, or reopen the parent if its work is not done.",
    "hidden": "Reopen each: it closed with work still open under it.",
    "no-original": "Reopen each and close it again through close-issues' duplicate command.",
    "no-decision": "Write each decision under '## Decision' in the body, or reopen it.",
}
WAITING = "Waiting on the owner (report these; an audit never answers them):"

PATH = re.compile(r"(?<![\w/.-])(?:[\w.-]+/)+[\w.-]+\.[A-Za-z]{1,6}\b")
NAME = re.compile(r"`([A-Za-z_][\w.:-]{3,60})`")
ERROR_LINE = re.compile(r"^.*\b(?:error|exception|panic|traceback)\b\s*:.*$", re.IGNORECASE | re.MULTILINE)
LANGUAGES = {
    "python", "rust", "typescript", "javascript", "ts", "js", "go", "golang", "java", "kotlin",
    "swift", "ruby", "php", "c#", "csharp", "c++", "cpp", "lua", "luau", "dart", "elixir",
    "english", "spanish", "french", "german", "portuguese", "japanese", "chinese", "korean",
}
CONNECTORS = {"in", "for", "on", "with", "the", "a", "an", "under", "via"}
WORKAROUND = re.compile(
    r"\b(time-?outs?|retry|retries|retrying|backoff|sleep|allow-?list|deny-?list|skip-?list"
    r"|exceptions? list|ignore-?list|one at a time|serially|sequentially|per[- ]language"
    r"|for each language|raise the limit|increase the limit)\b", re.IGNORECASE)

VERDICT_FIELDS = {
    "done": ("proof",),
    "duplicate": ("of",),
    "slice": ("cause", "as"),
    "cause": ("reason",),
    "wrong-premise": ("title", "fix", "under"),
    "out-of-date": ("evidence",),
    "still-real": ("evidence",),
    "unsure": ("check", "impossible_because"),
}
CLOSING = {"done", "duplicate", "out-of-date"}
MOVING = {"slice", "wrong-premise"}
STAYING_TOP = {"cause", "still-real", "unsure"}
SLICE_FORMS = ("checkbox", "sub-issue")


# Reading issue bodies.

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


def with_lines_in_section(body, heading, new_lines):
    """The body with new_lines added at the end of the section under heading, which is
    created at the end of the body when missing."""
    lines = (body or "").rstrip("\n").splitlines()
    for start, line in enumerate(lines):
        if line.strip().lower() == heading.lower():
            end = start + 1
            while end < len(lines) and not HEADING.match(lines[end]):
                end += 1
            while end > start + 1 and not lines[end - 1].strip():
                end -= 1
            lines = lines[:end] + ([""] if end == start + 1 else []) + new_lines + (
                ["", *lines[end:]] if end < len(lines) else [])
            return "\n".join(lines).rstrip("\n") + "\n"
    return "\n".join([*lines, "", heading, "", *new_lines]).lstrip("\n") + "\n"


def is_decision(issue):
    return any(DECISION_LABEL.search(label["name"]) for label in issue["labels"]["nodes"])


def milestone_of(issue):
    return issue["milestone"]["title"] if issue.get("milestone") else "(no milestone)"


def open_parent(issue):
    parent = issue["parent"]
    return parent["number"] if parent and parent["state"] == "OPEN" else None


# Structural findings.

def findings(issue):
    """(kind, message) pairs for one issue: structural findings and decisions waiting on the owner."""
    me = f"#{issue['number']} {issue['title']}"
    found = []
    if issue["state"] == "OPEN":
        parent = issue["parent"]
        if parent and parent["state"] != "OPEN":
            found.append(("closed-parent", f"{me} is open under closed parent #{parent['number']}"))
        if is_decision(issue) and not has_section(issue["body"], "## Decision"):
            found.append(("waiting", f"{me} waits on the owner's decision"))
        return found
    if issue["stateReason"] == "COMPLETED":
        for child in issue["subIssues"]["nodes"]:
            if child["state"] == "OPEN":
                found.append(("hidden", f"closed {me} has open sub-issue #{child['number']} {child['title']}"))
        for text in unticked_lines(issue["body"]):
            found.append(("hidden", f"closed {me} has an unticked line: {text}"))
        if is_decision(issue) and not has_section(issue["body"], "## Decision"):
            found.append(("no-decision", f"{me} closed as decided with no '## Decision' section"))
    if issue["stateReason"] == "DUPLICATE" and not issue["duplicateOf"]:
        found.append(("no-original", f"{me} closed as a duplicate of nothing"))
    return found


# Suggestions: likely slices of one cause, oversized milestones, workaround premises.

def signals(issue):
    """What an issue shares with others of the same cause: file paths, rule names,
    error text, and its title with any language named in it taken out."""
    text = f"{issue['title']}\n{issue['body'] or ''}"
    found = {("file", path) for path in PATH.findall(text)}
    found |= {("name", name) for name in NAME.findall(text)
              if not PATH.fullmatch(name) and re.search(r"[_.:-]|.[A-Z]", name)}
    for line in ERROR_LINE.findall(text):
        found.add(("error", re.sub(r"\s+", " ", re.sub(r"\d+", "#", line.strip().lower()))[:100]))
    words = re.findall(r"[\w#+]+", issue["title"].lower())
    if any(word in LANGUAGES for word in words):
        rest = [w for w in words if w not in LANGUAGES and w not in CONNECTORS]
        found.add(("languages", " ".join(rest)))
    return found


def carriers_of(issues):
    """Each signal with the issues that carry it, kept only when 2 to MAX_SHARED do:
    a signal most issues carry says nothing about a cause."""
    by_signal = defaultdict(set)
    for issue in issues:
        for signal in signals(issue):
            by_signal[signal].add(issue["number"])
    return {s: members for s, members in by_signal.items() if 2 <= len(members) <= MAX_SHARED}


def pair_weights(joining):
    """How strongly each pair of issues looks like one cause: error text or one bug in
    several languages counts 2, a shared file path or code name counts 1."""
    weight = Counter()
    for (kind, _), members in joining.items():
        ordered = sorted(members)
        for i, first in enumerate(ordered):
            for second in ordered[i + 1:]:
                weight[first, second] += STRONG.get(kind, 1)
    return weight


def clusters(issues):
    """Groups of open issues that look like slices of one cause, as (numbers, signals).
    Two issues join at weight 2: error text, one bug in several languages, or two weaker
    shared signals. One shared file alone is a lead, never a join, so it cannot chain."""
    joining = carriers_of(issues)
    root = {issue["number"]: issue["number"] for issue in issues}

    def find(n):
        while root[n] != n:
            root[n] = root[root[n]]
            n = root[n]
        return n

    for (first, second), total in pair_weights(joining).items():
        if total >= 2:
            root[find(second)] = find(first)
    groups = defaultdict(list)
    for number in root:
        groups[find(number)].append(number)
    result = []
    for members in groups.values():
        if len(members) > 1:
            shared = sorted(f"{kind}: {value}" for (kind, value), carriers in joining.items()
                            if len(carriers & set(members)) > 1)
            result.append((sorted(members), shared))
    return sorted(result)


def leads(issues):
    """Weaker leads: issues sharing one file path or code name that few issues carry,
    listed per signal and never chained, unless a cluster already holds them all."""
    grouped = [set(members) for members, _ in clusters(issues)]
    found = defaultdict(list)
    for (kind, value), members in carriers_of(issues).items():
        if kind in STRONG or len(members) > MAX_LEAD or any(members <= g for g in grouped):
            continue
        found[tuple(sorted(members))].append(f"{kind}: {value}")
    return sorted((list(members), "; ".join(sorted(shared))) for members, shared in found.items())


def milestone_sizes(issues):
    """Top-level open issues per milestone: each one a cause the milestone carries."""
    return dict(Counter(milestone_of(i) for i in issues if i["state"] == "OPEN" and not open_parent(i)))


def workaround_hints(issues):
    hints = []
    for issue in issues:
        asked = [issue["title"], *CHECKLIST.findall(issue["body"] or "")]
        match = WORKAROUND.search("\n".join(asked))
        if match:
            hints.append((issue["number"], match.group(0)))
    return hints


# A plain-language issue carries no file path, code name or error text, so two reports of
# one feature can share nothing the signals above see. Their titles still share its name.
SUBJECT_STOP = set("""
a an the and or of to in on at for with by from as is are be been being it its this that these
those into onto over under via per each every any all no not only own their his her our your my
we you they do does did done can could should would will may might must so than then when while
which who what where why how up down out off again new old make makes made let lets get gets use
uses used show shows keep keeps add adds one two against
""".split())


def subject_terms(title):
    """The title's words and adjacent word pairs, without connecting words."""
    words = [w for w in re.findall(r"[a-z][a-z0-9']+", title.lower()) if w not in SUBJECT_STOP and len(w) > 2]
    return set(words) | {f"{a} {b}" for a, b in zip(words, words[1:])}


def subject_scores(draft, opened):
    """(score, number, shared terms) for each open issue whose title shares a rare term with
    the draft's title. A term counts ln(open issues / titles carrying it), and only when at
    most MAX_SHARED titles carry it, so a common word or phrase counts nothing."""
    titles = {i["number"]: subject_terms(i["title"]) for i in opened}
    carriers = Counter(term for terms in titles.values() for term in terms)
    total = max(len(opened), 2)
    wanted = subject_terms(draft["title"])
    scored = []
    for number, terms in titles.items():
        shared = sorted((t for t in wanted & terms if carriers[t] <= MAX_SHARED), key=lambda t: carriers[t])
        if shared and number != draft.get("parent"):
            scored.append((round(sum(math.log(total / carriers[t]) for t in shared), 1), number, shared))
    return sorted(scored, key=lambda row: (-row[0], row[1]))


def subject_threshold(opened):
    """As much as two title words that no other open title carries."""
    return 2 * math.log(max(len(opened), 2))


def subject_leads(draft, issues, limit=3):
    """The closest titles below the refusal threshold, for the filer to read before filing."""
    opened = [i for i in issues if i["state"] == "OPEN"]
    threshold = subject_threshold(opened)
    return [row for row in subject_scores(draft, opened) if row[0] < threshold][:limit]


def draft_findings(draft, issues, milestone_description):
    """What stops a draft being filed: an open issue other than its declared parent that it
    shares a cause with (file paths, code names, error text) or a subject with (rare title
    words), a workaround premise, or a milestone it takes over MAX_CAUSES. Each
    clears by fixing the draft or by its recorded reason: the DIFFERENT_CAUSE or
    NOT_A_WORKAROUND line in the body, or the OVER_LIMIT_REASON line in the milestone
    description."""
    body = draft["body"] or ""
    opened = [i for i in issues if i["state"] == "OPEN"]
    candidate = {"number": 0, "title": draft["title"], "body": body}
    titles = {i["number"]: i["title"] for i in opened}
    found = []
    for (first, number), total in sorted(pair_weights(carriers_of([candidate, *opened])).items()):
        if (first == 0 and total >= 2 and number != draft.get("parent")
                and DIFFERENT_CAUSE.format(number=number) not in body):
            found.append(("same-cause", (
                f"#{number} {titles[number]} looks like the same cause: add this sighting to its body,"
                f" file this as its sub-issue, or write '{DIFFERENT_CAUSE.format(number=number)} <why>'"
                " in the draft")))
    flagged = {int(re.search(r"#(\d+)", message).group(1)) for _, message in found}
    threshold = subject_threshold(opened)
    for score, number, shared in subject_scores(draft, opened):
        if score >= threshold and number not in flagged and DIFFERENT_CAUSE.format(number=number) not in body:
            found.append(("same-subject", (
                f"#{number} {titles[number]} has the same subject ({', '.join(shared)}): add this to its"
                f" body, file this as its sub-issue, or write '{DIFFERENT_CAUSE.format(number=number)} <why>'"
                " in the draft")))
    hints = workaround_hints([candidate])
    if hints and NOT_A_WORKAROUND not in body:
        found.append(("workaround", (
            f"the draft asks for {hints[0][1]!r}, which reads like a workaround: ask for the proper fix,"
            f" or write '{NOT_A_WORKAROUND} <why>' in the draft")))
    milestone = draft.get("milestone")
    if milestone and not draft.get("parent"):
        count = milestone_sizes([i for i in opened if milestone_of(i) == milestone]).get(milestone, 0) + 1
        if count > MAX_CAUSES and OVER_LIMIT_REASON not in (milestone_description or ""):
            found.append(("milestone", (
                f"{milestone} would carry {count} causes, over {MAX_CAUSES}: file this under a cause"
                f" it already has, or add '{OVER_LIMIT_REASON}: <why>' to the milestone description")))
    return found


# The plan.

def in_scope(plan, issues):
    scope = plan.get("milestone")
    return [i for i in issues if i["state"] == "OPEN" and (not scope or milestone_of(i) == scope)]


def verdicts_of(plan):
    return {int(n): v for n, v in plan.get("verdicts", {}).items()}


def plan_findings(plan, issues):
    """(kind, message) pairs for everything that stops the plan being applied."""
    by_number = {i["number"]: i for i in issues}
    scope = {i["number"] for i in in_scope(plan, issues)}
    verdicts = verdicts_of(plan)
    new_causes = plan.get("new_causes", {})
    found = []

    def stays_open(ref):
        match ref:
            case str():
                return ref in new_causes
            case int():
                target = by_number.get(ref)
                return bool(target) and target["state"] == "OPEN" and (
                    ref not in verdicts or verdicts[ref].get("verdict") in STAYING_TOP)
        return False

    for number in sorted(scope - verdicts.keys()):
        found.append(("missing", f"#{number} {by_number[number]['title']} has no verdict"))
    for number, verdict in sorted(verdicts.items()):
        me = f"#{number}"
        if number not in scope:
            found.append(("unknown", f"{me} has a verdict but is not an open issue in scope"))
            continue
        kind = verdict.get("verdict")
        if kind not in VERDICT_FIELDS:
            found.append(("kind", f"{me} has verdict {kind!r}; use one of {', '.join(VERDICT_FIELDS)}"))
            continue
        needed = list(VERDICT_FIELDS[kind]) + (["line"] if verdict.get("as") == "checkbox" else [])
        empty = [field for field in needed if verdict.get(field) in (None, "", [])]
        if empty:
            found.append(("incomplete", f"{me} ({kind}) needs {', '.join(empty)}"))
            continue
        issue = by_number[number]
        match kind:
            case "slice" | "wrong-premise":
                cause = verdict["cause"] if kind == "slice" else verdict["under"]
                if cause == number or not stays_open(cause):
                    found.append(("cause", f"{me} hangs under {cause!r}, which is not a cause that stays open"))
            case "duplicate":
                if verdict["of"] == number or not stays_open(verdict["of"]):
                    found.append(("duplicate", f"{me} duplicates #{verdict['of']}, which does not stay open"))
        if kind == "slice" and verdict["as"] not in SLICE_FORMS:
            found.append(("kind", f"{me} is a slice as {verdict['as']!r}; use checkbox or sub-issue"))
        open_children = [c["number"] for c in issue["subIssues"]["nodes"] if c["state"] == "OPEN"]
        if kind == "slice" and verdict["as"] == "checkbox" and open_children:
            found.append(("checkbox", f"{me} has open sub-issues, so it stays a sub-issue, not a checkbox"))
        if kind in CLOSING:
            left = [c for c in open_children if verdicts.get(c, {}).get("verdict") not in CLOSING | MOVING]
            if left:
                found.append(("closing-parent", f"{me} closes with open sub-issues that stay under it: "
                              + ", ".join(f"#{c}" for c in left)))
    used = {v.get("cause") for v in verdicts.values()} | {v.get("under") for v in verdicts.values()}
    for key in sorted(set(new_causes) - used):
        found.append(("unused", f"new cause {key!r} has no slices; drop it"))
    reasons = plan.get("milestone_reasons", {})
    for milestone, count in sorted(after_sizes(plan, issues).items()):
        if count > MAX_CAUSES and not reasons.get(milestone):
            found.append(("milestone", (f"{milestone} ends with {count} causes, over {MAX_CAUSES}:"
                          f" merge slices of one cause, or give milestone_reasons[{milestone!r}]")))
    return found


def survivors(plan, issues):
    """Open issues in scope that stay open, as {number: parent after the plan or None}."""
    verdicts = verdicts_of(plan)
    staying = {}
    for issue in in_scope(plan, issues):
        verdict = verdicts.get(issue["number"], {})
        match verdict.get("verdict"):
            case "done" | "duplicate" | "out-of-date":
                continue
            case "slice" if verdict.get("as") == "checkbox":
                continue
            case "slice":
                staying[issue["number"]] = verdict["cause"]
            case "wrong-premise":
                staying[issue["number"]] = verdict["under"]
            case _:
                staying[issue["number"]] = open_parent(issue)
    closing = {n for n, v in verdicts.items() if v.get("verdict") in CLOSING}
    return {n: (None if parent in closing else parent) for n, parent in staying.items()}


def after_sizes(plan, issues):
    by_number = {i["number"]: i for i in issues}
    sizes = Counter(milestone_of(by_number[n]) for n, parent in survivors(plan, issues).items()
                    if parent is None)
    for spec in plan.get("new_causes", {}).values():
        sizes[spec.get("milestone") or "(no milestone)"] += 1
    return dict(sizes)


def plural(count, word, many=None):
    return f"{count} {word if count == 1 else many or word + 's'}"


def page(plan, issues, repo):
    """The short page the owner approves: counts first, then each cause with its slices."""
    by_number = {i["number"]: i for i in issues}
    scope = in_scope(plan, issues)
    verdicts = verdicts_of(plan)
    staying = survivors(plan, issues)
    new_causes = plan.get("new_causes", {})
    before_top, after_top = milestone_sizes(scope), after_sizes(plan, issues)
    open_after = Counter(milestone_of(by_number[n]) for n in staying)
    open_before = Counter(milestone_of(i) for i in scope)
    causes = [n for n, parent in staying.items() if parent is None]
    lines = [
        f"# Issue audit plan: {repo}" + (f", {plan['milestone']}" if plan.get("milestone") else ""),
        "",
        (f"Open issues: {len(scope)} → {len(staying) + len(new_causes)}."
         f" Top-level issues: {sum(before_top.values())} → {sum(after_top.values())}."
         f" Causes: {len(causes) + len(new_causes)}."),
        "",
        "| Milestone | Top-level now | Top-level after | Open now | Open after |",
        "|---|---|---|---|---|",
    ]
    for milestone in sorted(set(before_top) | set(after_top) | set(open_before)):
        new_here = sum(1 for s in new_causes.values() if (s.get("milestone") or "(no milestone)") == milestone)
        lines.append(f"| {milestone} | {before_top.get(milestone, 0)} | {after_top.get(milestone, 0)}"
                     f" | {open_before.get(milestone, 0)} | {open_after.get(milestone, 0) + new_here} |")
    lines += ["", "## Causes", ""]
    refs = [(n, f"#{n} {by_number[n]['title']}") for n in sorted(causes)]
    refs += [(key, f"new: {spec['title']}") for key, spec in sorted(new_causes.items())]
    for ref, name in refs:
        slices = [v for v in verdicts.values() if v.get("verdict") == "slice" and v.get("cause") == ref]
        forms = Counter(v["as"] for v in slices)
        premises = sum(1 for v in verdicts.values() if v.get("verdict") == "wrong-premise" and v.get("under") == ref)
        detail = ", ".join(part for part in (
            plural(forms["checkbox"], "checkbox", "checkboxes") if forms["checkbox"] else "",
            plural(forms["sub-issue"], "sub-issue") if forms["sub-issue"] else "") if part)
        text = plural(len(slices), "slice") + (f" ({detail})" if detail else "")
        if premises:
            text += f", {plural(premises, 'rewritten premise')}"
        lines.append(f"- {name}: {text}")
    kinds = Counter(v.get("verdict") for v in verdicts.values())
    folded = sum(1 for v in verdicts.values() if v.get("verdict") == "slice" and v.get("as") == "checkbox")
    lines += ["", "## Closing", "",
              (f"{plural(kinds['done'], 'issue')} done with proof, {plural(kinds['duplicate'], 'duplicate')},"
               f" {folded} folded into a cause as checkboxes, {kinds['out-of-date']} out of date.")]
    unsure = [(n, v) for n, v in sorted(verdicts.items()) if v.get("verdict") == "unsure"]
    if unsure:
        lines += ["", "## Unsure", ""]
        lines += [f"- #{n} {by_number[n]['title']}: settled by {v['check']}; not run here because"
                  f" {v['impossible_because']}" for n, v in unsure]
    reasons = plan.get("milestone_reasons", {})
    over = [(m, c) for m, c in sorted(after_top.items()) if c > MAX_CAUSES]
    if over:
        lines += ["", f"## Milestones over {MAX_CAUSES} causes", ""]
        lines += [f"- {m}: {c}, because {reasons.get(m, '(no reason given)')}" for m, c in over]
    return "\n".join(lines) + "\n"


def depth(number, by_number):
    issue = by_number.get(number)
    parent = open_parent(issue) if issue else None
    return 0 if parent is None else 1 + depth(parent, by_number)


def operations(plan, issues):
    """The plan's side effects in a safe order: create new causes, move issues under their
    causes, then close, deepest issues first so no close leaves open work under it."""
    by_number = {i["number"]: i for i in issues}
    verdicts = verdicts_of(plan)
    ops = [("create", key, spec) for key, spec in sorted(plan.get("new_causes", {}).items())]
    for number, verdict in sorted(verdicts.items()):
        match verdict["verdict"]:
            case "slice" if verdict["as"] == "sub-issue":
                ops.append(("sub-issue", number, verdict))
            case "wrong-premise":
                ops.append(("premise", number, verdict))
    closes = []
    for number, verdict in verdicts.items():
        match verdict["verdict"]:
            case "slice" if verdict["as"] == "checkbox":
                closes.append(("fold", number, verdict))
            case "duplicate" | "done" | "out-of-date":
                closes.append((verdict["verdict"], number, verdict))
    closes.sort(key=lambda op: (-depth(op[1], by_number), op[1]))
    return ops + closes


def approval_code(contents):
    digest = hashlib.sha256()
    for content in contents:
        digest.update(content + b"\0")
    return digest.hexdigest()[:12]


# GitHub.

def gh(*args, stdin=None):
    result = subprocess.run(["gh", *args], input=stdin, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args[:3])}: {result.stderr.strip()}")
    return result.stdout


def graphql(query, **variables):
    args = ["api", "graphql", "-f", f"query={query}"]
    for name, value in variables.items():
        args += ["-F" if isinstance(value, int) else "-f", f"{name}={value}"]
    return json.loads(gh(*args))["data"]


# Each repository's issues are kept on disk and refreshed with only the issues updated since
# the last sync, so a run costs one count query and the changed issues, not the whole tracker.
MIRROR_VERSION = 1
MIRROR_FIELDS = hashlib.sha256(ISSUE_FIELDS.encode()).hexdigest()[:12]


def mirror_path(repo):
    owner, name = repo.split("/")
    cache = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    return Path(cache) / "checkpickerupper" / "audit-issues" / f"{owner}__{name}.json"


def issue_pages(repo, since=None):
    """Every issue, or with since only those updated at or after it (oldest first)."""
    owner, name = repo.split("/")
    filtered = ", filterBy: {since: $since}, orderBy: {field: UPDATED_AT, direction: ASC}" if since else ""
    query = f"""query($owner: String!, $name: String!, $after: String{', $since: DateTime!' if since else ''}) {{
      repository(owner: $owner, name: $name) {{
        issues(first: 50, after: $after{filtered}) {{
          pageInfo {{ hasNextPage endCursor }}
          nodes {{ {ISSUE_FIELDS} }}
        }}
      }}
    }}"""
    issues, after = [], None
    while True:
        variables = {"owner": owner, "name": name, **({"since": since} if since else {})}
        if after:
            variables["after"] = after
        page_ = graphql(query, **variables)["repository"]["issues"]
        issues += page_["nodes"]
        if not page_["pageInfo"]["hasNextPage"]:
            return issues
        after = page_["pageInfo"]["endCursor"]


def issue_count(repo):
    owner, name = repo.split("/")
    query = """query($owner: String!, $name: String!) {
      repository(owner: $owner, name: $name) { issues { totalCount } }
    }"""
    return graphql(query, owner=owner, name=name)["repository"]["issues"]["totalCount"]


def read_mirror(path):
    """The saved mirror, or None with the reason a full download is needed printed on stderr."""
    try:
        loaded = json.loads(path.read_text())
    except FileNotFoundError:
        print(f"no local copy of the issues at {path}; downloading every issue", file=sys.stderr)
        return None
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        print(f"{path} is unreadable ({error}); downloading every issue again", file=sys.stderr)
        return None
    match loaded:
        case {"version": 1, "fields": str(fields), "synced_at": str() | None,
              "issues": dict()} if fields == MIRROR_FIELDS:
            return loaded
        case {"version": 1, "fields": str(fields)}:
            print(f"{path} was saved with issue fields {fields}, this script reads {MIRROR_FIELDS};"
                  " downloading every issue again", file=sys.stderr)
        case _:
            print(f"{path} is unreadable (not a version {MIRROR_VERSION} issue mirror);"
                  " downloading every issue again", file=sys.stderr)
    return None


def write_mirror(path, by_number, synced_at):
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_suffix(".partial")
    partial.write_text(json.dumps({"version": MIRROR_VERSION, "fields": MIRROR_FIELDS,
                                   "synced_at": synced_at, "issues": by_number}))
    partial.replace(path)


def refresh_links(by_number):
    """A sub-issue or parent changing state updates its own updatedAt, not the issues that list
    it, so each listed same-repository issue takes its state and title from its own record."""
    by_url = {issue["url"]: issue for issue in by_number.values()}
    for issue in by_number.values():
        for link in [issue["parent"], *issue["subIssues"]["nodes"]]:
            if link and link["url"] in by_url:
                link["state"] = by_url[link["url"]]["state"]
                link["title"] = by_url[link["url"]]["title"]


def latest_update(issues, previous):
    return max((i["updatedAt"] for i in issues), default=previous)


def synced_issues(repo):
    """Every issue in repo, open and closed, read through the local mirror."""
    path = mirror_path(repo)
    mirror = read_mirror(path)
    by_number, synced_at = None, None
    if mirror is not None and mirror["synced_at"] is not None:
        by_number = mirror["issues"]
        changed = issue_pages(repo, since=mirror["synced_at"])
        by_number.update({str(i["number"]): i for i in changed})
        synced_at = latest_update(changed, mirror["synced_at"])
        total = issue_count(repo)
        if total != len(by_number):
            print(f"{repo} has {total} issues but the local copy at {path} has {len(by_number)}"
                  " (issues were deleted or transferred); downloading every issue again",
                  file=sys.stderr)
            by_number = None
    if by_number is None:
        issues = issue_pages(repo)
        by_number = {str(i["number"]): i for i in issues}
        synced_at = latest_update(issues, None)
    refresh_links(by_number)
    write_mirror(path, by_number, synced_at)
    return [by_number[key] for key in sorted(by_number, key=int)]


def read_issue(repo, number):
    owner, name = repo.split("/")
    query = f"""query($owner: String!, $name: String!, $number: Int!) {{
      repository(owner: $owner, name: $name) {{ issue(number: $number) {{ {ISSUE_FIELDS} }} }}
    }}"""
    issue = graphql(query, owner=owner, name=name, number=number)["repository"]["issue"]
    if issue is None:
        raise RuntimeError(f"{repo}#{number} is not an issue")
    return issue


def close_issue_script():
    script = Path(__file__).resolve().parents[2] / "close-issues" / "scripts" / "close_issue.py"
    if not script.is_file():
        raise RuntimeError(f"apply closes through the close-issues skill, expected at {script}")
    return script


def run_close(repo, command, number, *options):
    result = subprocess.run(
        [sys.executable, str(close_issue_script()), command, "--repo", repo, "--issue", str(number), *options],
        capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"close_issue.py {command} #{number}: {(result.stderr or result.stdout).strip()}")


def edit_body(repo, issue, body):
    if body != (issue["body"] or ""):
        gh("issue", "edit", str(issue["number"]), "--repo", repo, "--body-file", "-", stdin=body)


def carry_into(repo, number, target, checkbox=None):
    """Copy an issue's details into the target's body under '(was #N)' lines."""
    survivor = read_issue(repo, target)
    marker = f"(was #{number})"
    if marker in (survivor["body"] or ""):
        return
    issue = read_issue(repo, number)
    body = survivor["body"] or ""
    if checkbox:
        body = with_lines_in_section(body, "## Done when", [f"- [ ] {checkbox} {marker}"])
    body = with_lines_in_section(body, "## Folded in", [
        f"### {issue['title']} {marker}", "", (issue["body"] or "").strip() or "(no details)"])
    edit_body(repo, survivor, body)


def hang_under(repo, number, parent):
    issue = read_issue(repo, number)
    if issue["parent"] and issue["parent"]["number"] == parent:
        return
    graphql("""mutation($parent: ID!, $child: ID!) {
      addSubIssue(input: {issueId: $parent, subIssueId: $child, replaceParent: true}) { issue { number } }
    }""", parent=read_issue(repo, parent)["id"], child=issue["id"])
    moved = read_issue(repo, number)["parent"]
    if not moved or moved["number"] != parent:
        raise RuntimeError(f"read back #{number}: it is not under #{parent}")


def apply_operation(repo, op, created):
    kind, ref, data = op

    def cause(key):
        return created[key] if isinstance(key, str) else key

    match kind:
        case "create":
            if ref in created:
                return
            args = ["issue", "create", "--repo", repo, "--title", data["title"], "--body-file", "-"]
            if data.get("milestone"):
                args += ["--milestone", data["milestone"]]
            created[ref] = int(gh(*args, stdin=data.get("body", "")).strip().rsplit("/", 1)[-1])
        case "sub-issue":
            hang_under(repo, ref, cause(data["cause"]))
        case "premise":
            issue = read_issue(repo, ref)
            if issue["title"] != data["title"]:
                gh("issue", "edit", str(ref), "--repo", repo, "--title", data["title"])
            edit_body(repo, issue, with_lines_in_section(
                issue["body"], "## Proper fix", [] if data["fix"] in (issue["body"] or "") else [data["fix"]]))
            hang_under(repo, ref, cause(data["under"]))
        case "fold" | "duplicate":
            target = cause(data["cause"] if kind == "fold" else data["of"])
            carry_into(repo, ref, target, checkbox=data.get("line") if kind == "fold" else None)
            if read_issue(repo, ref)["stateReason"] != "DUPLICATE":
                run_close(repo, "duplicate", ref, "--of", str(target))
        case "done":
            run_close(repo, "completed", ref, *[arg for p in data["proof"] for arg in ("--proof", p)])
        case "out-of-date":
            if read_issue(repo, ref)["state"] == "OPEN":
                run_close(repo, "out-of-date", ref, "--evidence", data["evidence"])


# Commands.

def load_plan(plan_path, verdict_paths):
    contents = [plan_path.read_bytes(), *(p.read_bytes() for p in verdict_paths)]
    plan = json.loads(contents[0])
    verdicts = dict(plan.get("verdicts", {}))
    for path, content in zip(verdict_paths, contents[1:], strict=True):
        for number, verdict in json.loads(content).items():
            if number in verdicts:
                raise RuntimeError(f"#{number} has a verdict in two files; {path} repeats it")
            verdicts[number] = verdict
    return {**plan, "verdicts": verdicts}, approval_code(contents)


def scan(args):
    issues = synced_issues(args.repo)
    found = [f for issue in issues for f in findings(issue)]
    print(RULE)
    for kind, fix in FIXES.items():
        messages = [m for k, m in found if k == kind]
        if messages:
            print(f"\n{fix}")
            for message in messages:
                print(f"  - {message}")
    waiting = [m for k, m in found if k == "waiting"]
    if waiting:
        print(f"\n{WAITING}")
        for message in waiting:
            print(f"  - {message}")
    scope = in_scope({"milestone": args.milestone}, issues)
    titles = {i["number"]: i["title"] for i in issues}
    over = {m: c for m, c in milestone_sizes(scope).items() if c > MAX_CAUSES}
    if over:
        print(f"\nMilestones over {MAX_CAUSES} top-level issues; merge slices of one cause"
              " (a plan over the limit needs a reason):")
        for milestone, count in sorted(over.items()):
            print(f"  - {milestone}: {count}")
    grouped = clusters(scope)
    if grouped:
        print("\nLikely slices of one cause (judge each; a shared signal is a lead, not a verdict):")
        for members, shared in grouped:
            print(f"  - {', '.join(f'#{n} {titles[n]}' for n in members)}")
            print(f"      sharing {'; '.join(shared)}")
    weak = leads(scope)
    if weak:
        print("\nWeaker leads, one shared file or name each (read both before calling them one cause):")
        for members, signal in weak:
            print(f"  - {', '.join(f'#{n} {titles[n]}' for n in members)}: {signal}")
    hints = workaround_hints(scope)
    if hints:
        print("\nCheck the premise: each asks for what reads like a workaround (is there a proper fix?):")
        for number, word in hints:
            print(f"  - #{number} {titles[number]} ({word})")
    if any(k != "waiting" for k, _ in found):
        return EXIT_FINDINGS
    print(f"\n{args.repo}: {len(issues)} issues read; no open work hides under a closed issue.")
    return 0


def index(args):
    scope = in_scope({"milestone": args.milestone}, synced_issues(args.repo))
    rows = [f"#{i['number']}\t{milestone_of(i)}\t"
            f"{'under #' + str(open_parent(i)) if open_parent(i) else 'top'}\t"
            f"{','.join(label['name'] for label in i['labels']['nodes'])}\t{i['title']}"
            for i in sorted(scope, key=lambda i: i["number"])]
    args.out.write_text("number\tmilestone\tparent\tlabels\ttitle\n" + "\n".join(rows) + "\n")
    print(f"wrote {len(rows)} open issues to {args.out}")
    return 0


def draft(args):
    milestone_description = ""
    if args.milestone:
        found = json.loads(gh("api", f"repos/{args.repo}/milestones?state=all&per_page=100"))
        matching = [m for m in found if m["title"] == args.milestone]
        if not matching:
            raise RuntimeError(f"{args.repo} has no milestone titled {args.milestone!r}")
        milestone_description = matching[0]["description"] or ""
    candidate = {"title": args.title, "body": args.body_file.read_text(),
                 "milestone": args.milestone, "parent": args.parent}
    issues = synced_issues(args.repo)
    found = draft_findings(candidate, issues, milestone_description)
    leads_ = subject_leads(candidate, issues)
    titles = {i["number"]: i["title"] for i in issues}
    if found:
        print(f"{args.title!r} is not ready to file:")
        for _, message in found:
            print(f"  - {message}")
    else:
        print(f"{args.title!r} passed the checks: no open issue shares its file paths, code names,"
              " error text or rare title words, its premise is not a workaround, and its milestone"
              " stays within its causes.")
    if leads_:
        print("Closest titles by subject; read each before filing:")
        for score, number, shared in leads_:
            print(f"  - #{number} {titles[number]} ({', '.join(shared)})")
    return EXIT_FINDINGS if found else 0


def plan_command(args):
    plan, code = load_plan(args.plan, args.verdicts)
    issues = synced_issues(args.repo)
    found = plan_findings(plan, issues)
    if found:
        print(f"{args.plan}: {len(found)} finding(s); fix the plan and run this again:")
        for _, message in found:
            print(f"  - {message}")
        return EXIT_FINDINGS
    args.page.write_text(page(plan, issues, args.repo))
    print(f"wrote {args.page}. Show the owner that page; nothing has changed yet.")
    print(f"After they approve it, run: apply --approved {code}")
    return 0


def apply(args):
    plan, code = load_plan(args.plan, args.verdicts)
    if args.approved != code:
        print(f"the plan changed since its page was approved (code {code}, approved {args.approved});"
              " run plan again and show the owner the new page", file=sys.stderr)
        return EXIT_FINDINGS
    # A rerun resumes: the first run checked the plan against the tracker it then changed.
    state_path = args.plan.with_suffix(".applied.json")
    resuming = state_path.is_file()
    created = json.loads(state_path.read_text())["created"] if resuming else {}
    issues = synced_issues(args.repo)
    found = [] if resuming else plan_findings(plan, issues)
    if found:
        print("the tracker no longer matches the plan; run plan again:", file=sys.stderr)
        for _, message in found:
            print(f"  - {message}", file=sys.stderr)
        return EXIT_FINDINGS
    steps = operations(plan, issues)
    for kind, ref, data in steps:
        try:
            apply_operation(args.repo, (kind, ref, data), created)
        finally:
            state_path.write_text(json.dumps({"created": created}, indent=2) + "\n")
        print(f"{kind} {ref if isinstance(ref, str) else f'#{ref}'}: done")
    print(f"applied {len(steps)} steps. Run scan to read the tracker back, then report to whoever asked.")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    parsers = {name: commands.add_parser(name) for name in ("scan", "index", "draft", "plan", "apply")}
    for sub in parsers.values():
        sub.add_argument("--repo", required=True)
    for name in ("scan", "index", "draft"):
        parsers[name].add_argument("--milestone")
    parsers["draft"].add_argument("--title", required=True)
    parsers["draft"].add_argument("--body-file", type=Path, required=True)
    parsers["draft"].add_argument("--parent", type=int, help="the issue this is filed under")
    parsers["index"].add_argument("--out", type=Path, required=True)
    for name in ("plan", "apply"):
        parsers[name].add_argument("--plan", type=Path, required=True)
        parsers[name].add_argument("--verdicts", type=Path, action="append", default=[])
    parsers["plan"].add_argument("--page", type=Path, required=True)
    parsers["apply"].add_argument("--approved", required=True)
    args = parser.parse_args()
    handlers = {"scan": scan, "index": index, "draft": draft, "plan": plan_command, "apply": apply}
    try:
        return handlers[args.command](args)
    except (RuntimeError, OSError, json.JSONDecodeError) as error:
        print(error, file=sys.stderr)
        return EXIT_UNREADABLE


if __name__ == "__main__":
    sys.exit(main())
