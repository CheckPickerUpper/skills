"""Read, write and inspect conductor-mode settings and live agent usage.

Settings live in $XDG_CONFIG_HOME/checkpickerupper/conductor-mode.toml
(default ~/.config/checkpickerupper) and the repository's .checkpickerupper/.
Project settings replace global settings; each usage kind replaces its table
whole. Global [credits].codex owns the separate account spending choice.
`show --kind K` exits 3 for missing settings, including credits.codex when
Codex uses finish-in-flight. `usage --kind K` prints one JSON row, including failures.
"""

import argparse
import asyncio
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tomllib
from typing import ClassVar, Literal, NoReturn, TypedDict

from usage_readers import Reading, Unavailable, read_claude, read_codex

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


@dataclass(frozen=True)
class IgnorePolicy:
    mode: ClassVar[Literal["ignore"]] = "ignore"


@dataclass(frozen=True)
class FinishInFlightPolicy:
    at_percent: int
    mode: ClassVar[Literal["finish-in-flight"]] = "finish-in-flight"


@dataclass(frozen=True)
class StopAtCommitPolicy:
    at_percent: int
    mode: ClassVar[Literal["stop-at-commit"]] = "stop-at-commit"


@dataclass(frozen=True)
class FinishThenStopPolicy:
    wind_down_at_percent: int
    stop_at_percent: int
    mode: ClassVar[Literal["finish-in-flight-then-stop"]] = "finish-in-flight-then-stop"


UsagePolicy = IgnorePolicy | FinishInFlightPolicy | StopAtCommitPolicy | FinishThenStopPolicy


class CreditsSettings(TypedDict, total=False):
    codex: bool


class Settings(TypedDict, total=False):
    max_implementers: int
    merge: str
    review_skills: list[str]
    usage: dict[str, UsagePolicy]
    credits: CreditsSettings


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
    if kind == "pi" and mode != "ignore":
        invalid(path, kind, "mode", "modes ['ignore'] (pi has no usage reader)")
    if not isinstance(mode, str) or mode not in MODE_KEYS:
        invalid(path, kind, "mode", f"modes {list(MODE_KEYS)} (required)")
    allowed = {"mode", *MODE_KEYS[mode]}
    for key in raw:
        if key not in allowed:
            invalid(path, kind, str(key), f"keys {sorted(allowed)} for mode {mode}")
    thresholds: dict[str, int] = {}
    for key in MODE_KEYS[mode]:
        value = raw.get(key)
        if type(value) is not int or not 1 <= value <= 100:
            invalid(path, kind, key, "an int in 1..100 (required; bool is excluded)")
        thresholds[key] = value
    if mode == "finish-in-flight-then-stop":
        if thresholds["wind_down_at_percent"] >= thresholds["stop_at_percent"]:
            invalid(path, kind, "wind_down_at_percent", "1..100 and wind_down_at_percent < stop_at_percent")
    if mode == "ignore":
        return IgnorePolicy()
    if mode == "finish-in-flight":
        return FinishInFlightPolicy(thresholds["at_percent"])
    if mode == "stop-at-commit":
        return StopAtCommitPolicy(thresholds["at_percent"])
    return FinishThenStopPolicy(thresholds["wind_down_at_percent"], thresholds["stop_at_percent"])


def policy_values(policy: UsagePolicy) -> dict[str, object]:
    return {"mode": policy.mode, **asdict(policy)}


def settings_values(settings: Settings) -> dict[str, object]:
    raw: dict[str, object] = {key: settings[key] for key in SETTING_KEYS if key in settings}
    if "credits" in settings:
        raw["credits"] = settings["credits"]
    if "usage" in settings:
        raw["usage"] = {kind: policy_values(policy) for kind, policy in settings["usage"].items()}
    return raw


def validated(path: Path, raw: dict[str, object], scope: Literal["global", "project"] = "global") -> Settings:
    unknown = sorted(set(raw) - {*SETTING_KEYS, "usage", "credits"})
    if unknown:
        sys.exit(f"{path}: unknown settings {unknown}; known settings are {[*SETTING_KEYS, 'usage', 'credits']}")
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
    if "credits" in raw:
        if scope == "project":
            sys.exit(f"{path}: credits: allowed only in the global file")
        credits = raw["credits"]
        if not isinstance(credits, dict):
            sys.exit(f"{path}: credits: allowed a table with codex = true|false")
        if any(key != "codex" for key in credits):
            sys.exit(f"{path}: credits: unknown keys {list(credits)}; allowed keys ['codex']")
        if "codex" in credits and type(credits["codex"]) is not bool:
            sys.exit(f"{path}: credits.codex: allowed true or false")
        settings["credits"] = {"codex": credits["codex"]} if "codex" in credits else {}
    return settings


def read_settings(path: Path, scope: Literal["global", "project"] = "global") -> Settings:
    if not path.is_file():
        return {}
    try:
        with path.open("rb") as handle:
            return validated(path, tomllib.load(handle), scope)
    except (OSError, tomllib.TOMLDecodeError, UnicodeDecodeError) as error:
        sys.exit(f"{path}: config error {type(error).__name__}: {error}")


def render(settings: Settings) -> str:
    lines = []
    if "max_implementers" in settings:
        lines.append(f"max_implementers = {settings['max_implementers']}")
    if "merge" in settings:
        lines.append(f'merge = "{settings["merge"]}"')
    if "review_skills" in settings:
        lines.append("review_skills = [" + ", ".join(json.dumps(name) for name in settings["review_skills"]) + "]")
    if "credits" in settings:
        lines.extend(("", "[credits]"))
        if "codex" in settings["credits"]:
            lines.append(f"codex = {json.dumps(settings['credits']['codex'])}")
    for kind, policy in settings.get("usage", {}).items():
        lines.extend(("", f"[usage.{kind}]"))
        for key, value in policy_values(policy).items():
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
    for index, path in enumerate(layers):
        settings = read_settings(path, "global" if index == 0 else "project")
        if "credits" in settings:
            raw["credits"] = settings["credits"]
            sources["credits"] = path
        for key in SETTING_KEYS:
            if key in settings:
                raw[key] = settings[key]
                sources[key] = path
        for kind, policy in settings.get("usage", {}).items():
            usage[kind] = policy
            sources[f"usage.{kind}"] = path
    if any(key.startswith("usage.") for key in sources):
        raw["usage"] = {kind: policy_values(policy) for kind, policy in usage.items()}
    return validated(Path("resolved conductor-mode.toml"), raw), sources, layers


def show(project_dir: str, kind: str | None = None) -> None:
    settings, sources, layers = resolve(project_dir)
    resolved = {
        key: {"value": settings[key], "from": str(sources[key])}
        for key in SETTING_KEYS if key in settings
    }
    resolved["usage"] = {
        agent: {"value": policy_values(policy), "from": str(sources[f"usage.{agent}"])}
        for agent, policy in settings.get("usage", {}).items()
    }
    if "credits" in settings:
        resolved["credits"] = {"value": settings["credits"], "from": str(sources["credits"])}
    print(json.dumps(resolved, indent=2))
    missing = [key for key in SETTING_KEYS if key not in settings]
    if kind is not None and kind not in settings.get("usage", {}):
        missing.append(f"usage.{kind}")
    if kind == "codex" and isinstance(settings.get("usage", {}).get(kind), FinishInFlightPolicy):
        if "codex" not in settings.get("credits", {}):
            missing.append("credits.codex")
    if missing:
        searched = ", ".join(str(path) for path in layers)
        print(f"not set: {', '.join(missing)} (searched {searched})", file=sys.stderr)
        sys.exit(EXIT_MISSING)


def write(scope: Literal["global", "project"], project_dir: str, changes: dict[str, object], kind: str | None,
          policy: dict[str, object]) -> None:
    folder = global_folder() if scope == "global" else project_folder(project_dir)
    path = folder / CONFIG_FILE
    settings = read_settings(path, scope)
    raw = settings_values(settings)
    raw.update(changes)
    if kind is not None:
        tables = {agent: policy_values(saved) for agent, saved in settings.get("usage", {}).items()}
        tables[kind] = policy
        raw["usage"] = tables
    checked = validated(path, raw, scope)
    rendered = render(checked)
    validated(path, tomllib.loads(rendered), scope)
    folder.mkdir(parents=True, exist_ok=True)
    readme = folder / "README.md"
    if not readme.exists():
        readme.write_text(FOLDER_README)
    path.write_text(rendered)
    print(path)


def ignored_usage(kind: str) -> UsageRow:
    return UsageRow(kind, "ignore", None, None, None, "normal", "usage ignored by policy")


def usage_state(kind: str, policy: UsagePolicy | None, reading: Reading | Unavailable,
                spend_credits: bool | None = None) -> UsageRow:
    if isinstance(policy, IgnorePolicy):
        return ignored_usage(kind)
    mode = policy.mode if policy else None
    if isinstance(reading, Unavailable):
        return UsageRow(kind, mode, None, None, None, "unknown", reading.reason)
    state = "normal"
    reason = "below usage thresholds"
    can_continue = (kind == "codex" and isinstance(policy, FinishInFlightPolicy)
                    and spend_credits is True and reading.credit_status == "usable")
    if reading.credit_status == "spend-control-reached":
        state, reason = "exhausted", "spendControlReached prevents credit spending"
    elif reading.used_percent >= 100 or reading.ordinary_usage == "blocked":
        if can_continue:
            state, reason = "wind-down", "ordinary usage is blocked; finish in flight with usable credits"
        else:
            state, reason = "exhausted", "ordinary usage is full or blocked; cannot continue with usable credits"
    elif policy is None:
        state, reason = "unknown", f"usage.{kind} is not set; ask for this kind's usage policy"
    elif kind == "codex" and isinstance(policy, FinishInFlightPolicy) and spend_credits is None:
        state, reason = "unknown", "credits.codex is not set; ask whether to spend credits"
    elif isinstance(policy, FinishThenStopPolicy):
        if reading.used_percent >= policy.stop_at_percent:
            state, reason = "stop", "stop_at_percent reached"
        elif reading.used_percent >= policy.wind_down_at_percent:
            state, reason = "wind-down", "wind_down_at_percent reached"
    elif reading.used_percent >= policy.at_percent:
        state = "wind-down" if isinstance(policy, FinishInFlightPolicy) else "stop"
        reason = "at_percent reached"
    return UsageRow(kind, mode, reading.used_percent, reading.window_minutes, reading.resets_at, state, reason)


def usage(project_dir: str, kind: str) -> None:
    settings, _, _ = resolve(project_dir)
    policy = settings.get("usage", {}).get(kind)
    if isinstance(policy, IgnorePolicy):
        row = ignored_usage(kind)
    else:
        if kind == "codex":
            reading = asyncio.run(read_codex(Path.home() / ".codex/app-server-control/app-server-control.sock"))
        elif kind == "claude":
            base = os.environ.get("XDG_STATE_HOME") or str(Path.home() / ".local/state")
            reading = read_claude(Path(base) / "dotfiles/usage/claude.json", datetime.now(timezone.utc))
        else:
            reading = Unavailable("pi has no usage reader")
        row = usage_state(kind, policy, reading, settings.get("credits", {}).get("codex"))
    print(json.dumps(asdict(row)))


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
    write_command.add_argument("--codex-spend-credits", choices=("true", "false"))
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
        if arguments.codex_spend_credits is not None:
            changes["credits"] = {"codex": arguments.codex_spend_credits == "true"}
        if policy and arguments.usage_kind is None:
            parser.error("usage options require --usage-kind")
        if not changes and arguments.usage_kind is None:
            parser.error("write needs a setting or --usage-kind with --usage-mode")
        write(arguments.scope, arguments.project_dir, changes, arguments.usage_kind, policy)


if __name__ == "__main__":
    main()
