#!/usr/bin/env python3
"""Record the lines of real Codex rollouts that conductor_board.py reads, redacted.

Usage: record_rollouts.py THREAD_ID...

For each thread, writes board_fixtures/rollouts/<originator>-<turn>-<id>.jsonl
with three kinds of line: the `session_meta` first line, the last turn event
(task_started, task_complete or turn_aborted) and the rollout's last line.
Each keeps only its type, `payload.type` and timestamp; the first line also
keeps the thread id, cwd, originator and sub-agent parent. Prompts, messages,
accounts and instructions are dropped. A cwd under ~/dev is kept relative to
it with the private repository's name replaced; any other cwd is redacted.
"""

import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
DEV = Path.home() / "dev"
PRIVATE_NAMES = (("venoble-application", "example-app"), ("venoble", "example-org"))
TURN_EVENTS = {"task_started", "task_complete", "turn_aborted"}


def sessions() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "sessions"


def public_cwd(cwd: str) -> str:
    if not (cwd == str(DEV) or cwd.startswith(f"{DEV}/")):
        return "/redacted"
    relative = "~/dev" + cwd[len(str(DEV)):]
    for private, public in PRIVATE_NAMES:
        relative = relative.replace(private, public)
    return relative


def event(row: dict) -> dict:
    payload = row.get("payload")
    kept = {"timestamp": row["timestamp"], "type": row["type"]}
    if isinstance(payload, dict) and "type" in payload:
        kept["payload"] = {"type": payload["type"]}
    return kept


def meta(row: dict) -> dict:
    payload = row["payload"]
    source = payload.get("source")
    spawn = source.get("subagent", {}).get("thread_spawn", {}) if isinstance(source, dict) else {}
    kept_source = {"subagent": {"thread_spawn": {"parent_thread_id": spawn["parent_thread_id"]}}} if spawn else source
    return {"timestamp": row["timestamp"], "type": row["type"],
            "payload": {"id": payload["id"], "timestamp": payload["timestamp"], "cwd": public_cwd(payload["cwd"]),
                        "originator": payload["originator"], "source": kept_source}}


def record(thread_id: str) -> Path:
    [path] = sessions().glob(f"*/*/*/rollout-*-{thread_id}.jsonl")
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    turns = [row for row in rows if isinstance(row.get("payload"), dict) and row["payload"].get("type") in TURN_EVENTS]
    kept = [meta(rows[0])] + [event(row) for row in (turns[-1:] + [rows[-1]]) if row is not rows[0]]
    unique = [row for index, row in enumerate(kept) if row not in kept[:index]]
    originator = rows[0]["payload"]["originator"].lower().replace(" ", "-").replace("_", "-")
    turn = turns[-1]["payload"]["type"] if turns else "no-turn"
    out = HERE / "rollouts" / f"{originator}-{turn}-{thread_id}.jsonl"
    out.parent.mkdir(exist_ok=True)
    out.write_text("".join(json.dumps(row) + "\n" for row in unique))
    return out


if __name__ == "__main__":
    for thread in sys.argv[1:]:
        print(record(thread))
