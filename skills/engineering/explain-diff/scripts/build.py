#!/usr/bin/env python3
"""Assemble an explain-diff page from a body file and quiz data.

The model writes the explanation body and the quiz as data; this script owns
answer placement, so the correct option's position is balanced across
questions instead of chosen by the model, and it refuses a quiz whose correct
answers stand out by length.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import random
import re
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "template.html"
OPTIONS_PER_QUESTION = 4
# A correct option this much longer than its longest distractor gives itself away.
GIVEAWAY_RATIO = 1.15

FORBIDDEN_BODY = [
    (re.compile(r"<\s*script", re.I), "<script> (the template owns all JavaScript)"),
    (re.compile(r"<\s*(link|iframe|object|embed)\b", re.I), "an external embed (<link>, <iframe>, <object>, <embed>)"),
    (re.compile(r"\son[a-z]+\s*=", re.I), "an inline event handler (onclick= and similar)"),
    (re.compile(r"\bsrc\s*=\s*[\"']?\s*(https?:)?//", re.I), "a remote src URL (the page must work offline)"),
    (re.compile(r"javascript:", re.I), "a javascript: URL"),
]


class BuildError(Exception):
    pass


def load_quiz(path: Path) -> list[dict]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise BuildError(f"{path}: cannot read quiz JSON: {error}") from error
    if not isinstance(raw, list) or not raw:
        raise BuildError(f"{path}: quiz must be a non-empty JSON array")
    for i, q in enumerate(raw, 1):
        if not isinstance(q, dict):
            raise BuildError(f"question {i}: must be an object")
        for key in ("question", "correct", "explanation"):
            if not isinstance(q.get(key), str) or not q[key].strip():
                raise BuildError(f"question {i}: '{key}' must be a non-empty string")
        distractors = q.get("distractors")
        if (not isinstance(distractors, list) or len(distractors) != OPTIONS_PER_QUESTION - 1
                or not all(isinstance(d, str) and d.strip() for d in distractors)):
            raise BuildError(f"question {i}: 'distractors' must be {OPTIONS_PER_QUESTION - 1} non-empty strings")
        options = [q["correct"], *distractors]
        if len({o.strip().lower() for o in options}) != len(options):
            raise BuildError(f"question {i}: options must all differ")
    return raw


def audit_lengths(quiz: list[dict]) -> None:
    giveaways, longest = [], 0
    for i, q in enumerate(quiz, 1):
        correct = len(q["correct"])
        longest_distractor = max(len(d) for d in q["distractors"])
        if correct > longest_distractor:
            longest += 1
        if correct > GIVEAWAY_RATIO * longest_distractor:
            giveaways.append(i)
    n = len(quiz)
    problems = []
    if len(giveaways) > n // 4:
        problems.append(
            f"correct option is >{round((GIVEAWAY_RATIO - 1) * 100)}% longer than every distractor "
            f"in question(s) {giveaways}; allowed at most {n // 4}")
    if longest > max(1, n // 2):
        problems.append(f"correct option is the longest in {longest} of {n} questions; allowed at most {max(1, n // 2)}")
    if problems:
        raise BuildError("quiz answers are guessable by length:\n  - " + "\n  - ".join(problems)
                         + "\nShorten the correct answers or make the distractors as specific.")


def place_answers(quiz: list[dict]) -> list[dict]:
    """Shuffle options so each position holds the answer about equally often.

    Seeded from the quiz text, so rebuilding the same quiz gives the same page.
    """
    seed = hashlib.sha256(json.dumps(quiz, sort_keys=True).encode("utf-8")).hexdigest()
    rng = random.Random(seed)
    positions: list[int] = []
    while len(positions) < len(quiz):
        cycle = list(range(OPTIONS_PER_QUESTION))
        rng.shuffle(cycle)
        positions.extend(cycle)
    placed = []
    for q, answer in zip(quiz, positions):
        options = list(q["distractors"])
        rng.shuffle(options)
        options.insert(answer, q["correct"])
        placed.append({"question": q["question"], "options": options,
                       "answer": answer, "explanation": q["explanation"]})
    return placed


def check_body(body: str) -> None:
    found = [label for pattern, label in FORBIDDEN_BODY if pattern.search(body)]
    if found:
        raise BuildError("body contains:\n  - " + "\n  - ".join(found))
    if not re.search(r"<h2\b", body, re.I):
        raise BuildError("body has no <h2> sections; the table of contents is built from them")


def render_html(title: str, meta: str, body: str, quiz: list[dict] | None) -> str:
    check_body(body)
    template = TEMPLATE.read_text(encoding="utf-8")
    quiz_section = ""
    quiz_json = "[]"
    if quiz:
        quiz_section = ('<h2 id="quiz">Quiz</h2>\n<p>Pick an answer to see whether it is right and why.</p>\n'
                        '<div class="quiz" id="xd-quiz"></div>')
        # Escape "<" so no quiz text can close the surrounding <script> element.
        quiz_json = json.dumps(quiz, ensure_ascii=False).replace("<", "\\u003c")
    return (template
            .replace("{{TITLE}}", html.escape(title))
            .replace("{{META}}", html.escape(meta))
            .replace("{{QUIZ_SECTION}}", quiz_section)
            .replace("{{QUIZ_JSON}}", quiz_json)
            .replace("{{BODY}}", body))


def render_md(title: str, meta: str, body: str, quiz: list[dict] | None) -> str:
    parts = [f"# {title}", ""]
    if meta:
        parts += [f"_{meta}_", ""]
    parts += [body.strip(), ""]
    if quiz:
        parts += ["## Quiz", ""]
        for i, q in enumerate(quiz, 1):
            parts.append(f"**{i}. {q['question']}**")
            parts.append("")
            for oi, option in enumerate(q["options"]):
                parts.append(f"- {chr(65 + oi)}. {option}")
            parts += ["", "<details><summary>Answer</summary>", "",
                      f"{chr(65 + q['answer'])}. {q['explanation']}", "", "</details>", ""]
    return "\n".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--title", required=True)
    parser.add_argument("--meta", default="", help="one line under the title, e.g. 'main...feature-x · 9 files'")
    parser.add_argument("--body", required=True, type=Path, help="HTML fragment (html) or Markdown (md)")
    parser.add_argument("--quiz", type=Path, help="quiz JSON; omit for no quiz on the page")
    parser.add_argument("--format", choices=("html", "md"), default="html")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    try:
        body = args.body.read_text(encoding="utf-8")
        quiz = None
        if args.quiz:
            raw = load_quiz(args.quiz)
            audit_lengths(raw)
            quiz = place_answers(raw)
        render = render_html if args.format == "html" else render_md
        output = render(args.title, args.meta, body, quiz)
    except (BuildError, OSError) as error:
        print(f"build failed: {error}", file=sys.stderr)
        return 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output, encoding="utf-8")
    if quiz:
        counts = [sum(q["answer"] == p for q in quiz) for p in range(OPTIONS_PER_QUESTION)]
        print("answer positions A-D:", counts)
    print(args.out.resolve())
    return 0


if __name__ == "__main__":
    sys.exit(main())
