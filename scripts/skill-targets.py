#!/usr/bin/env python3
"""Check whether a skill is published for one registered agent."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


AGENT_TARGETS_PATH = Path(__file__).with_name("agent-targets.json")


class MetadataError(ValueError):
    """Raised when the target metadata is missing or malformed."""


class AgentRegistryError(ValueError):
    """Raised when the registered agent destinations are malformed."""


def _load_agent_targets() -> dict[str, dict[str, str]]:
    try:
        raw_targets = json.loads(AGENT_TARGETS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise AgentRegistryError(f"{AGENT_TARGETS_PATH}: cannot read agent registry: {error}") from error

    if not isinstance(raw_targets, dict) or not raw_targets:
        raise AgentRegistryError(f"{AGENT_TARGETS_PATH}: agent registry must be a non-empty object")

    targets: dict[str, dict[str, str]] = {}
    for client, config in raw_targets.items():
        if not isinstance(client, str) or not client:
            raise AgentRegistryError(f"{AGENT_TARGETS_PATH}: every agent name must be a non-empty string")
        if not isinstance(config, dict):
            raise AgentRegistryError(f"{AGENT_TARGETS_PATH}: {client} must have an object configuration")
        destination_env = config.get("destination_env")
        default_destination = config.get("default_destination")
        if not isinstance(destination_env, str) or not destination_env:
            raise AgentRegistryError(f"{AGENT_TARGETS_PATH}: {client}.destination_env must be a string")
        if not isinstance(default_destination, str) or not default_destination:
            raise AgentRegistryError(
                f"{AGENT_TARGETS_PATH}: {client}.default_destination must be a non-empty string"
            )
        targets[client] = {
            "destination_env": destination_env,
            "default_destination": default_destination,
        }
    return targets


def supported_clients() -> tuple[str, ...]:
    """Return the registered agent names in registry order."""

    return tuple(_load_agent_targets())


def _destination_for(client: str) -> Path:
    targets = _load_agent_targets()
    try:
        target = targets[client]
    except KeyError as error:
        supported = ", ".join(targets)
        raise AgentRegistryError(
            f"unsupported client: {client}; registered clients: {supported}"
        ) from error
    environment_name = target["destination_env"]
    destination = os.environ.get(environment_name, target["default_destination"])
    if not destination:
        raise AgentRegistryError(f"{environment_name} cannot be empty")
    return Path(destination).expanduser()


def _without_comment(value: str) -> str:
    quote: str | None = None
    escaped = False
    for index, character in enumerate(value):
        if escaped:
            escaped = False
            continue
        if character == "\\" and quote == '"':
            escaped = True
            continue
        if character in {'"', "'"}:
            if quote == character:
                quote = None
            elif quote is None:
                quote = character
        elif character == "#" and quote is None and (index == 0 or value[index - 1].isspace()):
            return value[:index].rstrip()
    return value.strip()


def _scalar(value: str, source: Path, location: str) -> str:
    value = _without_comment(value.strip())
    if not value:
        raise MetadataError(f"{source}: {location} must name a client")
    if value.startswith('"') or value.startswith("'"):
        if len(value) < 2 or value[-1] != value[0]:
            raise MetadataError(f"{source}: {location} has an unterminated quoted client")
        if value[0] == '"':
            try:
                value = json.loads(value)
            except json.JSONDecodeError as error:
                raise MetadataError(f"{source}: {location} has invalid quoting: {error}") from error
        else:
            value = value[1:-1].replace("''", "'")
    if not value or any(character.isspace() for character in value):
        raise MetadataError(f"{source}: {location} must be one client name")
    return value


def _inline_list(value: str, source: Path) -> list[str]:
    value = _without_comment(value.strip())
    if not value.startswith("[") or not value.endswith("]"):
        raise MetadataError(f"{source}: clients must be a YAML list")

    body = value[1:-1]
    items: list[str] = []
    current: list[str] = []
    quote: str | None = None
    escaped = False
    for character in body:
        if escaped:
            current.append(character)
            escaped = False
            continue
        if character == "\\" and quote == '"':
            current.append(character)
            escaped = True
            continue
        if character in {'"', "'"}:
            quote = None if quote == character else character if quote is None else quote
            current.append(character)
        elif character == "," and quote is None:
            items.append("".join(current).strip())
            current = []
        else:
            current.append(character)
    if quote is not None:
        raise MetadataError(f"{source}: clients has an unterminated quoted value")
    if current or body.strip():
        items.append("".join(current).strip())
    if any(not item for item in items):
        raise MetadataError(f"{source}: clients contains an empty item")
    return [_scalar(item, source, f"clients[{index}]") for index, item in enumerate(items)]


def _frontmatter(skill_path: Path) -> list[str]:
    lines = skill_path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise MetadataError(f"{skill_path}: SKILL.md must start with YAML frontmatter")
    try:
        closing = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration as error:
        raise MetadataError(f"{skill_path}: frontmatter has no closing ---") from error
    return lines[1:closing]


def declared_clients(skill_path: Path) -> tuple[str, ...] | None:
    """Return the explicit client allow-list, or None for the universal default."""

    lines = _frontmatter(skill_path)
    clients: list[str] | None = None
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith("#") or line.startswith((" ", "\t")):
            index += 1
            continue
        if not line.startswith("clients:"):
            index += 1
            continue
        if clients is not None:
            raise MetadataError(f"{skill_path}: clients is declared more than once")

        value = line[len("clients:") :].strip()
        if value:
            clients = _inline_list(value, skill_path)
            index += 1
            continue

        clients = []
        child_index = index + 1
        while child_index < len(lines):
            child = lines[child_index]
            if not child.strip() or child.lstrip().startswith("#"):
                child_index += 1
                continue
            if not child.startswith((" ", "\t")):
                break
            stripped = child.strip()
            if stripped == "-" or not stripped.startswith("- "):
                raise MetadataError(f"{skill_path}: clients must contain YAML list items")
            clients.append(_scalar(stripped[2:], skill_path, f"clients[{len(clients)}]"))
            child_index += 1
        if not clients:
            raise MetadataError(f"{skill_path}: clients must contain at least one client")
        index = child_index

    if clients is None:
        return None
    if not clients:
        raise MetadataError(f"{skill_path}: clients must contain at least one client")
    registered_clients = supported_clients()
    unknown = sorted(set(clients) - set(registered_clients))
    if unknown:
        supported = ", ".join(registered_clients)
        raise MetadataError(
            f"{skill_path}: unknown client(s): {', '.join(unknown)}; supported clients: {supported}"
        )
    if len(set(clients)) != len(clients):
        raise MetadataError(f"{skill_path}: clients contains a duplicate client")
    return tuple(clients)


def is_targeted_to(skill_path: Path, client: str) -> bool:
    clients = declared_clients(skill_path)
    return clients is None or client in clients


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client")
    parser.add_argument("--destination", action="store_true")
    parser.add_argument("--list-clients", action="store_true")
    parser.add_argument("skill", type=Path, nargs="?")
    args = parser.parse_args()
    try:
        if args.list_clients:
            if args.client or args.destination or args.skill:
                parser.error("--list-clients cannot be combined with another argument")
            print("\n".join(supported_clients()))
            return 0
        if not args.client:
            parser.error("--client is required unless --list-clients is used")
        if args.destination:
            if args.skill:
                parser.error("--destination cannot be combined with a skill path")
            print(_destination_for(args.client))
            return 0
        if not args.skill:
            parser.error("a skill path is required unless --destination is used")
        if args.client not in supported_clients():
            _destination_for(args.client)
        return 0 if is_targeted_to(args.skill, args.client) else 1
    except (OSError, AgentRegistryError, MetadataError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
