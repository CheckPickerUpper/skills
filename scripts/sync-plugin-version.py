#!/usr/bin/env python3
"""Copy package.json's version into .claude-plugin/plugin.json.

Runs as part of `npm run version`, right after `changeset version`, so the
Claude Code plugin reports the same version as the release that ships it.
"""

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PACKAGE_PATH = REPO / "package.json"
PLUGIN_PATH = REPO / ".claude-plugin" / "plugin.json"


def main() -> None:
    version = json.loads(PACKAGE_PATH.read_text())["version"]
    plugin = json.loads(PLUGIN_PATH.read_text())
    previous = plugin.get("version", "unset")
    # Rebuilt rather than assigned so the version sits right after the name.
    synced = {"name": plugin["name"], "version": version}
    synced.update((key, value) for key, value in plugin.items() if key not in synced)
    PLUGIN_PATH.write_text(json.dumps(synced, indent=2, ensure_ascii=False) + "\n")
    print(f"plugin.json version {previous} -> {version}")


if __name__ == "__main__":
    main()
