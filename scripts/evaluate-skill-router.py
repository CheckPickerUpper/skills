#!/usr/bin/env python3
"""Run lightweight positive, negative, and near-miss routing evaluations."""

from __future__ import annotations

import sys
from pathlib import Path

from skill_artifacts import REPOSITORY_ROOT, MetadataError, _load_yaml, route_prompt


def main() -> int:
    catalog_path = REPOSITORY_ROOT / "generated" / "skill-catalog.json"
    cases_path = REPOSITORY_ROOT / "evals" / "router-cases.yaml"
    if not catalog_path.is_file():
        print("error: generated/skill-catalog.json is missing; run the generator first", file=sys.stderr)
        return 2
    if not cases_path.is_file():
        print("error: evals/router-cases.yaml is missing", file=sys.stderr)
        return 2
    try:
        import json

        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        payload = _load_yaml(cases_path.read_text(encoding="utf-8"), str(cases_path))
    except (OSError, ValueError, MetadataError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    if not isinstance(payload, dict) or not isinstance(payload.get("cases"), list):
        print("error: evals/router-cases.yaml must contain a cases list", file=sys.stderr)
        return 2

    failures: list[str] = []
    seen: set[str] = set()
    for case in payload["cases"]:
        if not isinstance(case, dict):
            failures.append("case is not a mapping")
            continue
        name = str(case.get("name", "unnamed case"))
        prompt = case.get("prompt")
        expected = case.get("expected")
        if not isinstance(prompt, str):
            failures.append(f"{name}: prompt is not a string")
            continue
        seen.add(expected) if isinstance(expected, str) else None
        matches = route_prompt(prompt, catalog)
        actual = matches[0]["name"] if matches else None
        if actual != expected:
            failures.append(f"{name}: expected {expected!r}, got {actual!r}")
        near_miss_of = case.get("near_miss_of")
        if near_miss_of:
            target = next((skill for skill in catalog["skills"] if skill["name"] == near_miss_of), None)
            if target is None:
                failures.append(f"{name}: near-miss target {near_miss_of!r} is not in the catalog")
            else:
                prompt_tokens = set(prompt.lower().split())
                alias_tokens = set(" ".join(target["aliases"]).lower().split())
                if not prompt_tokens.intersection(alias_tokens):
                    failures.append(f"{name}: near miss shares no vocabulary with {near_miss_of}")
                if any(" ".join(prompt.lower().split()) == alias.lower() for alias in target["aliases"]):
                    failures.append(f"{name}: near miss exactly matches an alias")

    required = {"grill-with-docs", "to-spec", "to-tickets", "implement", "tdd", "code-review"}
    missing = required - seen
    if missing:
        failures.append("missing chain evals: " + ", ".join(sorted(missing)))
    if failures:
        print("router evals failed:")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    print(f"passed {len(payload['cases'])} router evals")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
