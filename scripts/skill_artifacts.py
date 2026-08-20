#!/usr/bin/env python3
"""Build and validate the generated surfaces for this skills repository.

SKILL.md frontmatter is the only authored metadata source.  This module emits
Codex's agents/openai.yaml files, the published catalog, the router reference,
the public skill docs, and the plugin skill list from that source.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import TypeAlias


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PUBLISHED_BUCKETS = ("engineering", "productivity", "misc")
SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HEX_COLOR_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}$")
TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
STOP_WORDS = {
    "a",
    "an",
    "and",
    "for",
    "i",
    "in",
    "is",
    "it",
    "me",
    "my",
    "of",
    "on",
    "the",
    "this",
    "to",
    "we",
    "with",
}

YamlScalar: TypeAlias = str | bool | int | float | None
YamlValue: TypeAlias = YamlScalar | list["YamlValue"] | dict[str, "YamlValue"]
SkillData: TypeAlias = dict[str, object]


class MetadataError(ValueError):
    """Raised when authored skill metadata cannot produce a valid surface."""


def _load_yaml(text: str, source: str) -> YamlValue:
    """Load YAML with PyYAML, with a small fallback for the repository subset."""

    try:
        import yaml  # type: ignore
    except ImportError:
        return _load_simple_yaml(text, source)
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError as error:  # pragma: no cover - the parser owns the detail
        raise MetadataError(f"{source}: invalid YAML: {error}") from error


def _split_inline_values(value: str) -> list[str]:
    values: list[str] = []
    current: list[str] = []
    quote: str | None = None
    for character in value[1:-1]:
        if character in {'"', "'"}:
            if quote == character:
                quote = None
            elif quote is None:
                quote = character
        if character == "," and quote is None:
            values.append("".join(current).strip())
            current = []
        else:
            current.append(character)
    if current:
        values.append("".join(current).strip())
    return values


def _simple_scalar(value: str) -> YamlValue:
    value = value.strip()
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value in {"null", "Null", "NULL", "~"}:
        return None
    if value.startswith("[") and value.endswith("]"):
        return [_simple_scalar(item) for item in _split_inline_values(value)]
    if value.startswith('"') and value.endswith('"'):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    return value


def _load_simple_yaml(text: str, source: str) -> YamlValue:
    """Parse the small map/list YAML subset used by SKILL.md frontmatter."""

    lines = [
        (len(line) - len(line.lstrip(" ")), line.strip())
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not lines:
        return {}
    root: dict[str, YamlValue] = {}
    stack: list[tuple[int, YamlValue]] = [(-1, root)]
    index = 0
    while index < len(lines):
        indent, content = lines[index]
        while stack and stack[-1][0] >= indent:
            stack.pop()
        if not stack:
            raise MetadataError(f"{source}: invalid indentation near {content!r}")
        parent = stack[-1][1]
        if content.startswith("- "):
            if not isinstance(parent, list):
                raise MetadataError(f"{source}: list item has no list parent")
            item = content[2:].strip()
            if ":" in item:
                key, raw_value = item.split(":", 1)
                item_map: dict[str, YamlValue] = {key.strip(): _simple_scalar(raw_value)}
                parent.append(item_map)
                stack.append((indent, item_map))
            else:
                parent.append(_simple_scalar(item))
            index += 1
            continue
        if ":" not in content:
            raise MetadataError(f"{source}: expected a mapping entry near {content!r}")
        key, raw_value = content.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        if raw_value:
            if not isinstance(parent, dict):
                raise MetadataError(f"{source}: mapping entry has no map parent")
            parent[key] = _simple_scalar(raw_value)
        else:
            next_indent = lines[index + 1][0] if index + 1 < len(lines) else -1
            next_content = lines[index + 1][1] if index + 1 < len(lines) else ""
            child: YamlValue = [] if next_indent > indent and next_content.startswith("- ") else {}
            if not isinstance(parent, dict):
                raise MetadataError(f"{source}: mapping entry has no map parent")
            parent[key] = child
            stack.append((indent, child))
        index += 1
    return root


def _frontmatter(skill_path: Path) -> dict[str, YamlValue]:
    lines = skill_path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise MetadataError(f"{skill_path}: SKILL.md must start with YAML frontmatter")
    closing = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if closing is None:
        raise MetadataError(f"{skill_path}: frontmatter has no closing ---")
    parsed = _load_yaml("\n".join(lines[1:closing]), str(skill_path))
    if not isinstance(parsed, dict):
        raise MetadataError(f"{skill_path}: frontmatter must be a mapping")
    return parsed


def _mapping(value: YamlValue | None, location: str) -> dict[str, YamlValue]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise MetadataError(f"{location}: expected a mapping")
    return value


def _string(value: YamlValue | None, location: str, *, required: bool = False) -> str | None:
    if value is None:
        if required:
            raise MetadataError(f"{location}: required string is missing")
        return None
    if not isinstance(value, str) or not value.strip():
        raise MetadataError(f"{location}: expected a non-empty string")
    return value.strip()


def _string_list(value: YamlValue | None, location: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        raise MetadataError(f"{location}: expected a list of non-empty strings")
    return [item.strip() for item in value]


def _boolean(value: YamlValue | None, location: str) -> bool | None:
    if value is None:
        return None
    if not isinstance(value, bool):
        raise MetadataError(f"{location}: expected true or false")
    return value


def _contains_key(value: object, wanted: str) -> bool:
    if isinstance(value, dict):
        return any(key == wanted or _contains_key(item, wanted) for key, item in value.items())
    if isinstance(value, list):
        return any(_contains_key(item, wanted) for item in value)
    return False


def kebab_to_title_case(name: str) -> str:
    """Derive the stable picker name; authored display names are not accepted."""

    return " ".join(segment[:1].upper() + segment[1:].lower() for segment in name.split("-"))


def _first_sentence(text: str) -> str:
    sentence = re.split(r"(?<=[.!?])\s+", text.strip(), maxsplit=1)[0]
    return sentence.rstrip(".")


def _default_prompt(name: str, short_description: str) -> str:
    return f"Use ${name} for {short_description.rstrip('.')}."


def _validate_icon(skill_dir: Path, value: str, location: str) -> str:
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise MetadataError(f"{location}: icon path must stay relative to the skill directory")
    resolved = (skill_dir / candidate).resolve()
    if not resolved.is_relative_to(skill_dir.resolve()):
        raise MetadataError(f"{location}: icon path escapes the skill directory")
    if not resolved.is_file():
        raise MetadataError(f"{location}: icon file does not exist: {value}")
    return value


def _validate_tools(value: YamlValue | None, location: str) -> list[dict[str, str]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise MetadataError(f"{location}: expected a list")
    allowed = {"type", "value", "description", "transport", "command", "url"}
    tools: list[dict[str, str]] = []
    for index, raw_tool in enumerate(value):
        tool_location = f"{location}[{index}]"
        tool = _mapping(raw_tool, tool_location)
        unknown = set(tool) - allowed
        if unknown:
            raise MetadataError(f"{tool_location}: unsupported fields: {', '.join(sorted(unknown))}")
        tool_type = _string(tool.get("type"), f"{tool_location}.type", required=True)
        tool_value = _string(tool.get("value"), f"{tool_location}.value", required=True)
        if tool_type != "mcp":
            raise MetadataError(f"{tool_location}.type: only 'mcp' dependencies are supported")
        normalized = {"type": tool_type, "value": tool_value}
        for field in ("description", "transport", "command", "url"):
            field_value = _string(tool.get(field), f"{tool_location}.{field}")
            if field_value is not None:
                normalized[field] = field_value
        tools.append(normalized)
    return tools


def discover_skill_paths(root: Path = REPOSITORY_ROOT) -> list[Path]:
    paths: list[Path] = []
    for bucket in PUBLISHED_BUCKETS:
        bucket_dir = root / "skills" / bucket
        if not bucket_dir.is_dir():
            continue
        paths.extend(sorted(bucket_dir.glob("*/SKILL.md")))
    return paths


def load_skills(root: Path = REPOSITORY_ROOT) -> list[SkillData]:
    skills: list[SkillData] = []
    for skill_path in discover_skill_paths(root):
        frontmatter = _frontmatter(skill_path)
        skill_dir = skill_path.parent
        bucket = skill_dir.parent.name
        name = _string(frontmatter.get("name"), f"{skill_path}.name", required=True)
        assert name is not None
        if not SKILL_NAME_PATTERN.fullmatch(name):
            raise MetadataError(f"{skill_path}.name: must be lowercase kebab-case")
        if name != skill_dir.name:
            raise MetadataError(f"{skill_path}: name {name!r} must match directory {skill_dir.name!r}")
        if _contains_key(frontmatter, "display_name"):
            raise MetadataError(f"{skill_path}: display_name is forbidden; it is derived from name")
        description = _string(frontmatter.get("description"), f"{skill_path}.description", required=True)
        assert description is not None
        if len(description) > 1024:
            raise MetadataError(f"{skill_path}.description: maximum length is 1024 characters")
        short_description = _string(frontmatter.get("short_description"), f"{skill_path}.short_description")
        if short_description is None:
            short_description = _first_sentence(description)[:140]
        if len(short_description) > 1024:
            raise MetadataError(f"{skill_path}.short_description: maximum length is 1024 characters")

        openai = _mapping(frontmatter.get("openai"), f"{skill_path}.openai")
        unknown_openai = set(openai) - {"interface", "dependencies", "policy"}
        if unknown_openai:
            raise MetadataError(f"{skill_path}.openai: unsupported fields: {', '.join(sorted(unknown_openai))}")
        interface = _mapping(openai.get("interface"), f"{skill_path}.openai.interface")
        unknown_interface = set(interface) - {"default_prompt", "icon_small", "icon_large", "brand_color"}
        if unknown_interface:
            raise MetadataError(
                f"{skill_path}.openai.interface: unsupported fields: {', '.join(sorted(unknown_interface))}"
            )
        dependencies = _mapping(openai.get("dependencies"), f"{skill_path}.openai.dependencies")
        unknown_dependencies = set(dependencies) - {"tools"}
        if unknown_dependencies:
            raise MetadataError(
                f"{skill_path}.openai.dependencies: unsupported fields: {', '.join(sorted(unknown_dependencies))}"
            )
        policy = _mapping(openai.get("policy"), f"{skill_path}.openai.policy")
        unknown_policy = set(policy) - {"allow_implicit_invocation", "products"}
        if unknown_policy:
            raise MetadataError(f"{skill_path}.openai.policy: unsupported fields: {', '.join(sorted(unknown_policy))}")

        top_level_allow = _boolean(frontmatter.get("allow_implicit_invocation"), f"{skill_path}.allow_implicit_invocation")
        disabled = _boolean(frontmatter.get("disable-model-invocation"), f"{skill_path}.disable-model-invocation")
        policy_allow = _boolean(policy.get("allow_implicit_invocation"), f"{skill_path}.openai.policy.allow_implicit_invocation")
        if top_level_allow is not None and disabled is not None and top_level_allow == disabled:
            raise MetadataError(
                f"{skill_path}: allow_implicit_invocation and disable-model-invocation contradict each other"
            )
        derived_allow = None if disabled is None else not disabled
        for candidate, location in ((derived_allow, "disable-model-invocation"), (policy_allow, "openai.policy")):
            if candidate is not None and top_level_allow is not None and candidate != top_level_allow:
                raise MetadataError(f"{skill_path}: invocation policy disagrees with {location}")
        allow_implicit_invocation = (
            top_level_allow
            if top_level_allow is not None
            else derived_allow
            if derived_allow is not None
            else policy_allow
            if policy_allow is not None
            else True
        )

        default_prompt = _string(interface.get("default_prompt"), f"{skill_path}.openai.interface.default_prompt")
        if default_prompt is None:
            default_prompt = _default_prompt(name, short_description)
        if len(default_prompt) > 1024:
            raise MetadataError(f"{skill_path}.openai.interface.default_prompt: maximum length is 1024 characters")
        if f"${name}" not in default_prompt:
            raise MetadataError(f"{skill_path}.openai.interface.default_prompt: must mention ${name}")

        icon_small = _string(interface.get("icon_small"), f"{skill_path}.openai.interface.icon_small")
        icon_large = _string(interface.get("icon_large"), f"{skill_path}.openai.interface.icon_large")
        if icon_small is not None:
            icon_small = _validate_icon(skill_dir, icon_small, f"{skill_path}.openai.interface.icon_small")
        if icon_large is not None:
            icon_large = _validate_icon(skill_dir, icon_large, f"{skill_path}.openai.interface.icon_large")
        brand_color = _string(interface.get("brand_color"), f"{skill_path}.openai.interface.brand_color")
        if brand_color is not None and not HEX_COLOR_PATTERN.fullmatch(brand_color):
            raise MetadataError(f"{skill_path}.openai.interface.brand_color: expected a six-digit hex color")

        products = _string_list(policy.get("products"), f"{skill_path}.openai.policy.products")
        tools = _validate_tools(dependencies.get("tools"), f"{skill_path}.openai.dependencies.tools")
        catalog = _mapping(frontmatter.get("catalog"), f"{skill_path}.catalog")
        stage = _string(catalog.get("stage"), f"{skill_path}.catalog.stage") or bucket
        aliases = _string_list(catalog.get("aliases"), f"{skill_path}.catalog.aliases")
        if not aliases:
            aliases = [name.replace("-", " ")]
        when = _string(catalog.get("when"), f"{skill_path}.catalog.when") or description
        where_it_fits = _string(catalog.get("where_it_fits"), f"{skill_path}.catalog.where_it_fits") or f"{bucket.title()} workflow."
        signals = _string_list(catalog.get("success_signals"), f"{skill_path}.catalog.success_signals")
        if not signals:
            signals = ["The skill's stated outcome is complete and can be checked by the next stage."]
        predecessors = _string_list(catalog.get("predecessors"), f"{skill_path}.catalog.predecessors")
        raw_order = catalog.get("order", 99)
        if not isinstance(raw_order, int) or isinstance(raw_order, bool):
            raise MetadataError(f"{skill_path}.catalog.order: expected an integer")

        skills.append(
            {
                "name": name,
                "display_name": kebab_to_title_case(name),
                "description": description,
                "short_description": short_description,
                "bucket": bucket,
                "path": skill_dir.relative_to(root).as_posix(),
                "skill_path": skill_path,
                "allow_implicit_invocation": allow_implicit_invocation,
                "default_prompt": default_prompt,
                "icon_small": icon_small,
                "icon_large": icon_large,
                "brand_color": brand_color,
                "dependencies": {"tools": tools} if tools else None,
                "products": products,
                "stage": stage,
                "order": raw_order,
                "aliases": aliases,
                "when": when,
                "where_it_fits": where_it_fits,
                "success_signals": signals,
                "predecessors": predecessors,
            }
        )
    return sorted(skills, key=lambda item: (item["bucket"], item["name"]))


def _quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_openai_yaml(skill: SkillData) -> str:
    lines = [
        "# Generated by scripts/generate-skill-artifacts.py. Do not edit.",
        "interface:",
        f"  display_name: {_quote(skill['display_name'])}",
        f"  short_description: {_quote(skill['short_description'])}",
        f"  default_prompt: {_quote(skill['default_prompt'])}",
    ]
    for field in ("icon_small", "icon_large", "brand_color"):
        if skill[field] is not None:
            lines.append(f"  {field}: {_quote(skill[field])}")
    if skill["dependencies"]:
        lines.extend(["", "dependencies:", "  tools:"])
        for tool in skill["dependencies"]["tools"]:
            lines.append("    - type: " + _quote(tool["type"]))
            lines.append("      value: " + _quote(tool["value"]))
            for field in ("description", "transport", "command", "url"):
                if field in tool:
                    lines.append(f"      {field}: {_quote(tool[field])}")
    lines.extend(["", "policy:", f"  allow_implicit_invocation: {'true' if skill['allow_implicit_invocation'] else 'false'}"])
    if skill["products"]:
        lines.append("  products:")
        lines.extend(f"    - {_quote(product)}" for product in skill["products"])
    return "\n".join(lines) + "\n"


def render_doc(skill: SkillData) -> str:
    predecessor_text = ", ".join(f"`${name}`" for name in skill["predecessors"]) or "None"
    dependency_lines = [
        f"- `{tool['value']}` ({tool['type']})"
        + (f": {tool['description']}" if tool.get("description") else "")
        for tool in (skill["dependencies"] or {}).get("tools", [])
    ] or ["- No external tool dependency is declared."]
    signal_lines = "\n".join(f"- {signal}" for signal in skill["success_signals"])
    return f"""<!-- Generated from {skill['path']}/SKILL.md. Do not edit. -->
# {skill['display_name']}

## What it does

{skill['short_description']}

## When to reach for it

{skill['when']}

## Where it fits

{skill['where_it_fits']} The catalog stage is `{skill['stage']}`. Previous stages: {predecessor_text}.

## Prerequisites

{chr(10).join(dependency_lines)}

## It is working if

{signal_lines}

## Invocation

Use `${skill['name']}` when you want this skill explicitly. It is {'available for implicit selection' if skill['allow_implicit_invocation'] else 'explicit-only'}.
"""


def _catalog_entry(skill: SkillData, root: Path) -> dict[str, object]:
    return {
        "name": skill["name"],
        "display_name": skill["display_name"],
        "bucket": skill["bucket"],
        "path": skill["path"],
        "docs": f"docs/{skill['bucket']}/{skill['name']}.md",
        "description": skill["description"],
        "short_description": skill["short_description"],
        "allow_implicit_invocation": skill["allow_implicit_invocation"],
        "stage": skill["stage"],
        "order": skill["order"],
        "aliases": skill["aliases"],
        "predecessors": skill["predecessors"],
        "default_prompt": skill["default_prompt"],
        "brand_color": skill["brand_color"],
        "dependencies": skill["dependencies"],
        "products": skill["products"],
    }


def render_catalog_json(skills: list[SkillData], root: Path = REPOSITORY_ROOT) -> str:
    payload = {
        "version": 1,
        "generated_from": "skills/{engineering,productivity,misc}/**/SKILL.md",
        "display_name_rule": "kebab_to_title_case(name)",
        "skills": [_catalog_entry(skill, root) for skill in skills],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def render_catalog_markdown(skills: list[SkillData], docs_prefix: str = "") -> str:
    ordered = sorted(skills, key=lambda item: (item["order"], item["name"]))
    chain = [skill for skill in ordered if skill["order"] < 99]
    lines = [
        "<!-- Generated by scripts/generate-skill-artifacts.py. Do not edit. -->",
        "# Skill catalog and router",
        "",
        "The catalog is derived from each published `SKILL.md`. The picker name is always derived from `name`; no display-name override is accepted.",
        "",
        "## Workflow chain",
        "",
        "| Step | Skill | Use it for | Previous stage |",
        "| --- | --- | --- | --- |",
    ]
    for skill in chain:
        predecessors = ", ".join(f"`${name}`" for name in skill["predecessors"]) or "None"
        lines.append(f"| {skill['order']} · {skill['stage']} | `${skill['name']}` | {skill['short_description']} | {predecessors} |")
    lines.extend(
        [
            "",
            "## Routing rules",
            "",
            "1. Honor an explicit `$skill-name` first.",
            "2. Otherwise choose one exact intent phrase from the aliases below; do not route from a generic word alone.",
            "3. If no alias is a clear match, ask for the missing intent instead of guessing.",
            "4. Use the exact kebab-case skill name when proposing the next step. The display name is derived and never authored.",
            "",
            "| Skill | Intent aliases | Explicit-only |",
            "| --- | --- | --- |",
        ]
    )
    for skill in sorted(skills, key=lambda item: item["name"]):
        aliases = ", ".join(f"“{alias}”" for alias in skill["aliases"])
        explicit_only = "yes" if not skill["allow_implicit_invocation"] else "no"
        lines.append(f"| `${skill['name']}` | {aliases} | {explicit_only} |")
    lines.extend(["", "## All published skills", "", "| Skill | Bucket | Stage | Docs |", "| --- | --- | --- | --- |"])
    for skill in sorted(skills, key=lambda item: (item["bucket"], item["name"])):
        docs_path = f"docs/{skill['bucket']}/{skill['name']}.md"
        lines.append(f"| `${skill['name']}` | {skill['bucket']} | {skill['stage']} | [{skill['display_name']}]({docs_prefix}{docs_path}) |")
    return "\n".join(lines) + "\n"


def route_prompt(prompt: str, catalog: dict[str, object]) -> list[dict[str, object]]:
    """Return deterministic intent matches for the lightweight router/evals."""

    normalized = " ".join(TOKEN_PATTERN.findall(prompt.lower()))
    matches: list[dict[str, object]] = []
    for skill in catalog.get("skills", []):
        name_phrase = skill["name"].replace("-", " ")
        score = 0
        if f"${skill['name']}" in prompt.lower():
            score += 1000
        if name_phrase in normalized:
            score += 80
        for alias in skill.get("aliases", []):
            alias_phrase = " ".join(TOKEN_PATTERN.findall(alias.lower()))
            if alias_phrase and alias_phrase in normalized:
                score += 100 + len(alias_phrase.split())
        if score:
            matches.append({"name": skill["name"], "score": score})
    return sorted(matches, key=lambda item: (-item["score"], item["name"]))


def _write_or_check(path: Path, content: str, check: bool, failures: list[str]) -> None:
    if check:
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            failures.append(str(path.relative_to(REPOSITORY_ROOT)))
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.is_file() or path.read_text(encoding="utf-8") != content:
        path.write_text(content, encoding="utf-8")


def generate(check: bool = False, root: Path = REPOSITORY_ROOT) -> int:
    skills = load_skills(root)
    failures: list[str] = []
    for skill in skills:
        _write_or_check(skill["skill_path"].parent / "agents" / "openai.yaml", render_openai_yaml(skill), check, failures)
        _write_or_check(root / "docs" / skill["bucket"] / f"{skill['name']}.md", render_doc(skill), check, failures)

    catalog_json = render_catalog_json(skills, root)
    catalog_markdown = render_catalog_markdown(skills, docs_prefix="../")
    _write_or_check(root / "generated" / "skill-catalog.json", catalog_json, check, failures)
    _write_or_check(root / "generated" / "skill-catalog.md", catalog_markdown, check, failures)
    router_reference = root / "skills" / "productivity" / "skill-router" / "references" / "skill-catalog.md"
    if router_reference.parent.parent.is_dir():
        _write_or_check(router_reference, render_catalog_markdown(skills, docs_prefix="../../../../"), check, failures)

    plugin = {
        "name": "checkpickerupper-skills",
        "skills": [f"./{skill['path']}" for skill in skills],
    }
    _write_or_check(root / ".claude-plugin" / "plugin.json", json.dumps(plugin, indent=2) + "\n", check, failures)

    if failures:
        print("stale generated files:")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    print(f"{'checked' if check else 'generated'} {len(skills)} skills")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail when generated files are missing or stale")
    args = parser.parse_args()
    try:
        return generate(check=args.check)
    except MetadataError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
