#!/usr/bin/env python3
"""Stand-in for the `gh` and `herdr` executables that conductor_board.py runs.

Replay (default): print the response recorded for this exact argv from
$BOARD_RESPONSES, or exit 1 naming the argv when none was recorded.
Record ($BOARD_RECORD=1): run the real executable, redact the response, and save it.

The recorded repository is private and this one is public, so recording keeps
each response's shape, numbers, states, edges and timestamps, and replaces
titles, bodies, logins, labels and the repository's name.
"""

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

PRIVATE_NAMES = (("venoble/venoble-application", "example-org/example-app"),
                 ("venoble-application", "example-app"), ("venoble", "example-org"))
PUBLIC_LOGINS = {"example-org"}


def response_file(argv: list[str]) -> Path:
    key = re.sub(r"[^A-Za-z0-9]+", "_", " ".join(argv)).strip("_")
    return Path(os.environ["BOARD_RESPONSES"]) / f"{key}.json"


def redact(value: object) -> object:
    if isinstance(value, list):
        return [redact(item) for item in value]
    if not isinstance(value, dict):
        return value
    if "login" in value:
        # An account's id, avatar and URLs identify it as surely as its login.
        def account_field(key: str, item: object) -> object:
            if key == "login":
                return item if item in PUBLIC_LOGINS else "member"
            if isinstance(item, bool) or key == "type":
                return item
            return 0 if isinstance(item, int) else "" if isinstance(item, str) else item
        return {key: account_field(key, item) for key, item in value.items()}
    out = {}
    for key, item in value.items():
        if key == "title" and isinstance(item, str):
            item = f"{'Milestone' if 'open_issues' in value else 'Issue'} {value.get('number', '')}".strip()
        elif key in ("body", "description", "homepage") and isinstance(item, str):
            item = ""
        elif key == "labels":
            item = []
        elif key == "headRefName":
            item = "-".join(re.findall(r"[0-9]+", item) + ["topic"])
        elif key in ("terminal_title", "terminal_title_stripped"):
            item = "agent"
        elif key in ("cwd", "foreground_cwd"):
            item = "/redacted"
        out[key] = redact(item)
    return out


def record(tool: str, argv: list[str]) -> None:
    here = str(Path(__file__).resolve().parent / "bin")
    search = os.pathsep.join(p for p in os.environ["PATH"].split(os.pathsep) if Path(p).resolve() != Path(here))
    real = shutil.which(tool, path=search)
    done = subprocess.run([real, *argv], capture_output=True, text=True)
    sys.stderr.write(done.stderr)
    if done.returncode != 0:
        sys.exit(done.returncode)
    text = done.stdout
    sys.stdout.write(done.stdout)
    for private, public in PRIVATE_NAMES:
        text = text.replace(private, public)
    stdout = redact(json.loads(text))
    if tool == "herdr":
        stdout["result"]["agents"] = stdout["result"]["agents"][:1]
    public_argv = json.loads(json.dumps(argv).replace("venoble/venoble-application", "example-org/example-app"))
    response_file([tool, *public_argv]).write_text(json.dumps({"argv": [tool, *public_argv], "stdout": stdout},
                                                              indent=1) + "\n")


# Commands that change something. Recording runs the real executable, so it must never be handed one of these.
WRITES = (["gh", "pr", "merge"], ["herdr", "worktree", "remove"])


def main() -> None:
    tool, argv = Path(sys.argv[0]).name, sys.argv[1:]
    if os.environ.get("BOARD_RECORD") == "1":
        if [tool, *argv][:3] in WRITES:
            sys.exit(f"refusing to record a command that writes: {tool} {' '.join(argv)}")
        record(tool, argv)
        return
    # Every call is logged, so a test can show that a write was, or was not, attempted.
    with (Path(os.environ["BOARD_RESPONSES"]) / "calls.log").open("a") as log:
        log.write(json.dumps([tool, *argv]) + "\n")
    path = response_file([tool, *argv])
    if not path.is_file():
        sys.exit(f"no recorded response for: {tool} {' '.join(argv)}")
    recorded = json.loads(path.read_text())
    if "sequence" in recorded:
        # The same read answers differently over time (a PR is open, then merged): the Nth call gets the Nth answer.
        counter = path.with_suffix(".count")
        call = int(counter.read_text()) if counter.is_file() else 0
        counter.write_text(str(call + 1))
        recorded = recorded["sequence"][min(call, len(recorded["sequence"]) - 1)]
    sys.stderr.write(recorded.get("stderr", ""))
    if "stdout" in recorded:
        print(json.dumps(recorded["stdout"]))
    sys.exit(recorded.get("exit", 0))


if __name__ == "__main__":
    main()
