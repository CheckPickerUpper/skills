"""Read, write and inspect conductor-mode settings and live agent usage.

Settings live in $XDG_CONFIG_HOME/checkpickerupper/conductor-mode.toml
(default ~/.config/checkpickerupper) and the repository's .checkpickerupper/.
Project settings replace global settings; each usage kind replaces its table
whole. `show --kind K` exits 3 for missing top-level settings or that kind's
usage policy. `usage --kind K` prints one JSON row, including failures.
"""

import argparse
import asyncio
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tomllib
from typing import NoReturn, NotRequired, TypedDict

CONFIG_FILE = "conductor-mode.toml"
MERGE_OWNERS = ("conductor", "implementer")
SETTING_KEYS = ("max_implementers", "merge", "review_skills")
AGENT_KINDS = ("codex", "claude", "pi")
MODE_KEYS = {
    "ignore": (),
    "finish-in-flight": ("at_percent",),
    "stop-at-commit": ("at_percent",),
    "finish-in-flight-then-stop": ("wind_down_at_percent", "stop_at_percent"),
}
EXIT_MISSING = 3
READ_TIMEOUT_SECONDS = 5
CLAUDE_MAX_AGE_SECONDS = 600
SKILL_NAME = re.compile(r"[a-z0-9][a-z0-9_-]*(:[a-z0-9][a-z0-9_-]*)?")

FOLDER_README = """# CheckPickerUpper skill config

Settings read by [CheckPickerUpper skills](https://github.com/CheckPickerUpper/skills),
one TOML file per skill, such as `conductor-mode.toml`. A project's
`.checkpickerupper/` folder overrides the global `~/.config/checkpickerupper/`.

<!--
MIT License

Copyright (c) 2026 ChequePickerUpper
https://github.com/CheckPickerUpper/skills/blob/main/LICENSE
-->
"""


class UsagePolicy(TypedDict):
    mode: str
    at_percent: NotRequired[int]
    wind_down_at_percent: NotRequired[int]
    stop_at_percent: NotRequired[int]
    spend_credits: NotRequired[bool]


class Settings(TypedDict, total=False):
    max_implementers: int
    merge: str
    review_skills: list[str]
    usage: dict[str, UsagePolicy]


@dataclass(frozen=True)
class Reading:
    used_percent: float
    window_minutes: int | None
    resets_at: str | None
    credits_usable: bool = False


@dataclass(frozen=True)
class Unavailable:
    reason: str


@dataclass(frozen=True)
class UsageRow:
    kind: str
    mode: str | None
    used_percent: float | None
    window_minutes: int | None
    resets_at: str | None
    state: str
    reason: str


def global_folder() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(base) / "checkpickerupper"


def project_folder(project_dir: str) -> Path:
    found = subprocess.run(
        ["git", "-C", project_dir, "rev-parse", "--show-toplevel"],
        capture_output=True, text=True,
    )
    if found.returncode != 0:
        sys.exit(f"{project_dir} is not inside a git repository, so it has no project config")
    return Path(found.stdout.strip()) / ".checkpickerupper"


def invalid(path: Path, kind: str, key: str, allowed: str) -> NoReturn:
    sys.exit(f"{path}: usage.{kind}.{key}: allowed {allowed}")


def usage_policy(path: Path, kind: str, raw: object) -> UsagePolicy:
    if kind not in AGENT_KINDS:
        invalid(path, kind, kind, f"kinds {list(AGENT_KINDS)}")
    if not isinstance(raw, dict):
        invalid(path, kind, kind, "a table")
    mode = raw.get("mode")
    if not isinstance(mode, str) or mode not in MODE_KEYS:
        invalid(path, kind, "mode", f"modes {list(MODE_KEYS)} (required)")
    allowed = {"mode", *MODE_KEYS[mode]}
    if kind == "codex":
        allowed.add("spend_credits")
    for key in raw:
        if key not in allowed:
            invalid(path, kind, str(key), f"keys {sorted(allowed)} for mode {mode}")
    policy: UsagePolicy = {"mode": mode}
    for key in MODE_KEYS[mode]:
        value = raw.get(key)
        if type(value) is not int or not 1 <= value <= 100:
            invalid(path, kind, key, "an int in 1..100 (required; bool is excluded)")
        policy[key] = value
    if mode == "finish-in-flight-then-stop":
        if policy["wind_down_at_percent"] >= policy["stop_at_percent"]:
            invalid(path, kind, "wind_down_at_percent", "1..100 and wind_down_at_percent < stop_at_percent")
    if kind == "codex":
        credits = raw.get("spend_credits")
        if type(credits) is not bool:
            invalid(path, kind, "spend_credits", "true or false (required for codex)")
        policy["spend_credits"] = credits
    return policy


def validated(path: Path, raw: dict[str, object]) -> Settings:
    unknown = sorted(set(raw) - {*SETTING_KEYS, "usage"})
    if unknown:
        sys.exit(f"{path}: unknown settings {unknown}; known settings are {[*SETTING_KEYS, 'usage']}")
    settings: Settings = {}
    if "max_implementers" in raw:
        value = raw["max_implementers"]
        if type(value) is not int or value < 1:
            sys.exit(f"{path}: max_implementers must be a whole number of at least 1, not {value!r}")
        settings["max_implementers"] = value
    if "merge" in raw:
        owner = raw["merge"]
        if not isinstance(owner, str) or owner not in MERGE_OWNERS:
            sys.exit(f"{path}: merge must be one of {list(MERGE_OWNERS)}, not {owner!r}")
        settings["merge"] = owner
    if "review_skills" in raw:
        names = raw["review_skills"]
        if not isinstance(names, list) or any(type(name) is not str or not SKILL_NAME.fullmatch(name) for name in names):
            sys.exit(f'{path}: review_skills must be a list of skill names such as ["code-review"], not {names!r}')
        if len(set(names)) != len(names):
            sys.exit(f"{path}: review_skills lists a skill more than once: {names!r}")
        settings["review_skills"] = names
    if "usage" in raw:
        tables = raw["usage"]
        if not isinstance(tables, dict):
            invalid(path, "<kind>", "usage", f"a table of kinds {list(AGENT_KINDS)}")
        settings["usage"] = {kind: usage_policy(path, kind, table) for kind, table in tables.items()}
    return settings


def read_settings(path: Path) -> Settings:
    if not path.is_file():
        return {}
    try:
        with path.open("rb") as handle:
            return validated(path, tomllib.load(handle))
    except (OSError, tomllib.TOMLDecodeError) as error:
        sys.exit(f"{path}: {error}")


def render(settings: Settings) -> str:
    lines = []
    if "max_implementers" in settings:
        lines.append(f"max_implementers = {settings['max_implementers']}")
    if "merge" in settings:
        lines.append(f'merge = "{settings["merge"]}"')
    if "review_skills" in settings:
        lines.append("review_skills = [" + ", ".join(json.dumps(name) for name in settings["review_skills"]) + "]")
    for kind, policy in settings.get("usage", {}).items():
        lines.extend(("", f"[usage.{kind}]"))
        for key, value in policy.items():
            lines.append(f"{key} = {json.dumps(value)}")
    return "\n".join(lines) + "\n"


def resolve(project_dir: str) -> tuple[Settings, dict[str, Path], list[Path]]:
    layers = [global_folder() / CONFIG_FILE]
    in_git = subprocess.run(
        ["git", "-C", project_dir, "rev-parse", "--show-toplevel"], capture_output=True
    ).returncode == 0
    if in_git:
        layers.append(project_folder(project_dir) / CONFIG_FILE)
    raw: dict[str, object] = {}
    sources: dict[str, Path] = {}
    usage: dict[str, UsagePolicy] = {}
    for path in layers:
        settings = read_settings(path)
        for key in SETTING_KEYS:
            if key in settings:
                raw[key] = settings[key]
                sources[key] = path
        for kind, policy in settings.get("usage", {}).items():
            usage[kind] = policy
            sources[f"usage.{kind}"] = path
    if any(key.startswith("usage.") for key in sources):
        raw["usage"] = usage
    return validated(Path("resolved conductor-mode.toml"), raw), sources, layers


def show(project_dir: str, kind: str | None = None) -> None:
    settings, sources, layers = resolve(project_dir)
    resolved = {
        key: {"value": settings[key], "from": str(sources[key])}
        for key in SETTING_KEYS if key in settings
    }
    resolved["usage"] = {
        agent: {"value": policy, "from": str(sources[f"usage.{agent}"])}
        for agent, policy in settings.get("usage", {}).items()
    }
    print(json.dumps(resolved, indent=2))
    missing = [key for key in SETTING_KEYS if key not in settings]
    if kind is not None and kind not in settings.get("usage", {}):
        missing.append(f"usage.{kind}")
    if missing:
        searched = ", ".join(str(path) for path in layers)
        print(f"not set: {', '.join(missing)} (searched {searched})", file=sys.stderr)
        sys.exit(EXIT_MISSING)


def write(scope: str, project_dir: str, changes: dict[str, object], kind: str | None,
          policy: dict[str, object]) -> None:
    folder = global_folder() if scope == "global" else project_folder(project_dir)
    path = folder / CONFIG_FILE
    settings = read_settings(path)
    raw: dict[str, object] = dict(settings)
    raw.update(changes)
    if kind is not None:
        tables = dict(settings.get("usage", {}))
        tables[kind] = usage_policy(path, kind, policy)
        raw["usage"] = tables
    checked = validated(path, raw)
    rendered = render(checked)
    validated(path, tomllib.loads(rendered))
    folder.mkdir(parents=True, exist_ok=True)
    readme = folder / "README.md"
    if not readme.exists():
        readme.write_text(FOLDER_README)
    path.write_text(rendered)
    print(path)


def mapping(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict) or any(not isinstance(key, str) for key in value):
        raise ValueError(f"{label} must be an object")
    return value


def percentage(value: object, label: str) -> float:
    if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 100:
        raise ValueError(f"{label} must be a number in 0..100")
    return float(value)


def iso_time(value: object, label: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be an ISO 8601 timestamp")
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError(f"{label} must include a timezone")
    return parsed


def epoch_time(value: object, label: str) -> str:
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(f"{label} must be epoch seconds")
    return datetime.fromtimestamp(value, timezone.utc).isoformat()


def codex_reading(result: object) -> Reading:
    limits = mapping(mapping(result, "result").get("rateLimits"), "rateLimits")
    windows = [mapping(limits[key], key) for key in ("primary", "secondary") if limits.get(key) is not None]
    if not windows:
        raise ValueError("rateLimits has no primary or secondary window")
    readings = []
    for window in windows:
        used = percentage(window.get("usedPercent"), "usedPercent")
        minutes = window.get("windowDurationMins")
        if type(minutes) is not int or minutes <= 0:
            raise ValueError("windowDurationMins must be a positive int")
        reset = epoch_time(window.get("resetsAt"), "resetsAt")
        readings.append(Reading(used, minutes, reset))
    credits = mapping(limits.get("credits"), "credits")
    if any(type(credits.get(key)) is not bool for key in ("hasCredits", "unlimited")):
        raise ValueError("credits.hasCredits and credits.unlimited must be bools")
    highest = max(readings, key=lambda reading: reading.used_percent)
    return Reading(highest.used_percent, highest.window_minutes, highest.resets_at,
                   credits["hasCredits"] or credits["unlimited"])


async def read_codex(socket_path: Path, timeout_seconds: float = READ_TIMEOUT_SECONDS) -> Reading | Unavailable:
    try:
        from websockets.asyncio.client import unix_connect
        from websockets.exceptions import WebSocketException
    except ImportError as error:
        return Unavailable(f"websockets library unavailable: {error}")
    try:
        async with asyncio.timeout(timeout_seconds):
            async with unix_connect(str(socket_path), open_timeout=timeout_seconds, close_timeout=1) as connection:
                await connection.send(json.dumps({"id": 1, "method": "initialize", "params": {
                    "clientInfo": {"name": "conductor-mode", "version": "1"}}}))
                for request_id in (1, 2):
                    while True:
                        reply = mapping(json.loads(await connection.recv()), "JSON-RPC response")
                        if reply.get("id") == request_id:
                            break
                    if "error" in reply:
                        raise ValueError(f"{('initialize' if request_id == 1 else 'account/rateLimits/read')} error response: {reply['error']}")
                    if "result" not in reply:
                        raise ValueError("JSON-RPC response missing result")
                    if request_id == 1:
                        await connection.send(json.dumps({"method": "initialized"}))
                        await connection.send(json.dumps({"id": 2, "method": "account/rateLimits/read", "params": {}}))
                return codex_reading(reply["result"])
    except TimeoutError:
        return Unavailable(f"Codex socket {socket_path}: timeout after {timeout_seconds}s")
    except (OSError, WebSocketException, ValueError, OverflowError) as error:
        return Unavailable(f"Codex socket {socket_path}: {type(error).__name__}: {error}")


def read_claude(path: Path, now: datetime) -> Reading | Unavailable:
    try:
        with path.open() as handle:
            data = mapping(json.load(handle), "Claude usage")
        received = iso_time(data.get("received_at"), "received_at")
        age = (now - received).total_seconds()
        if age > CLAUDE_MAX_AGE_SECONDS:
            return Unavailable(f"Claude usage {path}: stale reading ({int(age)} seconds old)")
        if age < 0:
            raise ValueError("received_at is in the future")
        limits = mapping(data.get("rate_limits"), "rate_limits")
        readings = []
        for key, minutes in (("five_hour", 300), ("seven_day", 10080)):
            if limits.get(key) is None:
                continue
            window = mapping(limits[key], key)
            used = percentage(window.get("used_percentage"), f"{key}.used_percentage")
            reset = window.get("resets_at")
            resets_at = epoch_time(reset, f"{key}.resets_at") if reset is not None else None
            readings.append(Reading(used, minutes, resets_at))
        if not readings:
            raise ValueError("rate_limits has no five_hour or seven_day window")
        return max(readings, key=lambda reading: reading.used_percent)
    except (OSError, ValueError, OverflowError) as error:
        return Unavailable(f"Claude usage {path}: {type(error).__name__}: {error}")


def usage_state(kind: str, policy: UsagePolicy | None, reading: Reading | Unavailable) -> UsageRow:
    mode = policy["mode"] if policy else None
    used = reading.used_percent if isinstance(reading, Reading) else None
    minutes = reading.window_minutes if isinstance(reading, Reading) else None
    reset = reading.resets_at if isinstance(reading, Reading) else None
    state = "normal"
    reason = "below usage thresholds"
    can_continue = kind == "codex" and policy is not None and policy.get("spend_credits") is True and isinstance(reading, Reading) and reading.credits_usable
    if used is not None and used >= 100 and not can_continue:
        state, reason = "exhausted", "usage is full; this kind cannot continue with usable credits"
    elif mode == "ignore":
        reason = reading.reason if isinstance(reading, Unavailable) else "usage policy is ignore"
    elif policy is None:
        state, reason = "unknown", f"usage.{kind} is not set; ask for this kind's usage policy"
    elif isinstance(reading, Unavailable):
        state, reason = "unknown", reading.reason
    elif mode == "finish-in-flight-then-stop":
        if reading.used_percent >= policy["stop_at_percent"]:
            state, reason = "stop", "stop_at_percent reached"
        elif reading.used_percent >= policy["wind_down_at_percent"]:
            state, reason = "wind-down", "wind_down_at_percent reached"
    elif reading.used_percent >= policy["at_percent"]:
        state = "wind-down" if mode == "finish-in-flight" else "stop"
        reason = "at_percent reached"
    return UsageRow(kind, mode, used, minutes, reset, state, reason)


def usage(project_dir: str, kind: str) -> None:
    settings, _, _ = resolve(project_dir)
    if kind == "codex":
        reading = asyncio.run(read_codex(Path.home() / ".codex/app-server-control/app-server-control.sock"))
    elif kind == "claude":
        base = os.environ.get("XDG_STATE_HOME") or str(Path.home() / ".local/state")
        reading = read_claude(Path(base) / "dotfiles/usage/claude.json", datetime.now(timezone.utc))
    else:
        reading = Unavailable("pi has no usage reader")
    print(json.dumps(asdict(usage_state(kind, settings.get("usage", {}).get(kind), reading))))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("show", "usage"):
        command = commands.add_parser(name)
        command.add_argument("--project-dir", default=".")
        command.add_argument("--kind", choices=AGENT_KINDS, required=name == "usage")
    write_command = commands.add_parser("write")
    write_command.add_argument("--scope", choices=("global", "project"), required=True)
    write_command.add_argument("--project-dir", default=".")
    write_command.add_argument("--max-implementers", type=int)
    write_command.add_argument("--merge", choices=MERGE_OWNERS)
    write_command.add_argument("--review-skills")
    write_command.add_argument("--usage-kind", choices=AGENT_KINDS)
    write_command.add_argument("--usage-mode", choices=tuple(MODE_KEYS))
    for key in ("at-percent", "wind-down-at-percent", "stop-at-percent"):
        write_command.add_argument(f"--{key}", type=int)
    write_command.add_argument("--spend-credits", choices=("true", "false"))
    arguments = parser.parse_args()
    if arguments.command == "show":
        show(arguments.project_dir, arguments.kind)
    elif arguments.command == "usage":
        usage(arguments.project_dir, arguments.kind)
    else:
        changes = {key: getattr(arguments, key) for key in ("max_implementers", "merge") if getattr(arguments, key) is not None}
        if arguments.review_skills is not None:
            changes["review_skills"] = [name.strip() for name in arguments.review_skills.split(",") if name.strip()]
        policy = {key: getattr(arguments, key) for key in ("at_percent", "wind_down_at_percent", "stop_at_percent") if getattr(arguments, key) is not None}
        if arguments.usage_mode is not None:
            policy["mode"] = arguments.usage_mode
        if arguments.spend_credits is not None:
            policy["spend_credits"] = arguments.spend_credits == "true"
        if policy and arguments.usage_kind is None:
            parser.error("usage options require --usage-kind")
        if not changes and arguments.usage_kind is None:
            parser.error("write needs a setting or --usage-kind with --usage-mode")
        write(arguments.scope, arguments.project_dir, changes, arguments.usage_kind, policy)


if __name__ == "__main__":
    main()
