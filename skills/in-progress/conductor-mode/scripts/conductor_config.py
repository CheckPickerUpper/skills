"""Read and write conductor-mode settings from CheckPickerUpper config folders.

Usage:
  python3 conductor_config.py show [--project-dir DIR]
  python3 conductor_config.py write --scope global|project [--project-dir DIR]
                                    [--max-implementers N] [--merge conductor|implementer]
                                    [--review-skills NAME,NAME,...]

`--review-skills ""` records an explicit empty list: no review skills.

Settings live in `conductor-mode.toml` inside a CheckPickerUpper config folder:
the global folder `$XDG_CONFIG_HOME/checkpickerupper` (default
`~/.config/checkpickerupper`) and the project folder `.checkpickerupper` at the
repository root. A project value overrides the global one; a project
`review_skills` list replaces the global list rather than adding to it.

`show` prints each setting with the file it came from. It exits 3 when a
setting is set in neither file, so the caller knows to ask the user.
"""

import argparse
import json
import re
import os
import subprocess
import sys
import tomllib
from pathlib import Path

CONFIG_FILE = "conductor-mode.toml"
MERGE_OWNERS = ("conductor", "implementer")
SETTING_KEYS = ("max_implementers", "merge", "review_skills")
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


def global_folder() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(base) / "checkpickerupper"


def project_folder(project_dir: str) -> Path:
    found = subprocess.run(
        ["git", "-C", project_dir, "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
    )
    if found.returncode != 0:
        sys.exit(f"{project_dir} is not inside a git repository, so it has no project config")
    return Path(found.stdout.strip()) / ".checkpickerupper"


def validated(path: Path, raw: dict) -> dict:
    unknown = sorted(set(raw) - set(SETTING_KEYS))
    if unknown:
        sys.exit(f"{path}: unknown settings {unknown}; known settings are {list(SETTING_KEYS)}")
    if "max_implementers" in raw:
        value = raw["max_implementers"]
        if type(value) is not int or value < 1:
            sys.exit(f"{path}: max_implementers must be a whole number of at least 1, not {value!r}")
    if "merge" in raw and raw["merge"] not in MERGE_OWNERS:
        sys.exit(f"{path}: merge must be one of {list(MERGE_OWNERS)}, not {raw['merge']!r}")
    if "review_skills" in raw:
        names = raw["review_skills"]
        if type(names) is not list or any(type(name) is not str or not SKILL_NAME.fullmatch(name) for name in names):
            sys.exit(f"{path}: review_skills must be a list of skill names such as [\"code-review\"], not {names!r}")
        if len(set(names)) != len(names):
            sys.exit(f"{path}: review_skills lists a skill more than once: {names!r}")
    return raw


def read_settings(path: Path) -> dict:
    if not path.is_file():
        return {}
    with path.open("rb") as handle:
        return validated(path, tomllib.load(handle))


def render(settings: dict) -> str:
    lines = []
    if "max_implementers" in settings:
        lines.append(f"max_implementers = {settings['max_implementers']}")
    if "merge" in settings:
        lines.append(f'merge = "{settings["merge"]}"')
    if "review_skills" in settings:
        lines.append("review_skills = [" + ", ".join(f'"{name}"' for name in settings["review_skills"]) + "]")
    return "\n".join(lines) + "\n"


def show(project_dir: str) -> None:
    layers = [global_folder() / CONFIG_FILE]
    in_git = subprocess.run(
        ["git", "-C", project_dir, "rev-parse", "--show-toplevel"], capture_output=True
    ).returncode == 0
    if in_git:
        layers.append(project_folder(project_dir) / CONFIG_FILE)

    resolved = {}
    for path in layers:
        for key, value in read_settings(path).items():
            resolved[key] = {"value": value, "from": str(path)}

    print(json.dumps(resolved, indent=2))
    missing = [key for key in SETTING_KEYS if key not in resolved]
    if missing:
        searched = ", ".join(str(path) for path in layers)
        print(f"not set: {', '.join(missing)} (searched {searched})", file=sys.stderr)
        sys.exit(EXIT_MISSING)


def write(scope: str, project_dir: str, max_implementers: int, merge: str, review_skills: list) -> None:
    folder = global_folder() if scope == "global" else project_folder(project_dir)
    path = folder / CONFIG_FILE
    settings = read_settings(path)
    if max_implementers is not None:
        settings["max_implementers"] = max_implementers
    if merge is not None:
        settings["merge"] = merge
    if review_skills is not None:
        settings["review_skills"] = review_skills
    validated(path, settings)

    folder.mkdir(parents=True, exist_ok=True)
    readme = folder / "README.md"
    if not readme.exists():
        readme.write_text(FOLDER_README)
    path.write_text(render(settings))
    print(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    show_command = commands.add_parser("show")
    show_command.add_argument("--project-dir", default=".")
    write_command = commands.add_parser("write")
    write_command.add_argument("--scope", choices=("global", "project"), required=True)
    write_command.add_argument("--project-dir", default=".")
    write_command.add_argument("--max-implementers", type=int)
    write_command.add_argument("--merge", choices=MERGE_OWNERS)
    write_command.add_argument("--review-skills")
    arguments = parser.parse_args()

    if arguments.command == "show":
        show(arguments.project_dir)
    else:
        review_skills = None
        if arguments.review_skills is not None:
            review_skills = [name.strip() for name in arguments.review_skills.split(",") if name.strip()]
        if arguments.max_implementers is None and arguments.merge is None and review_skills is None:
            parser.error("write needs at least one of --max-implementers, --merge, --review-skills")
        write(arguments.scope, arguments.project_dir, arguments.max_implementers, arguments.merge, review_skills)


if __name__ == "__main__":
    main()
