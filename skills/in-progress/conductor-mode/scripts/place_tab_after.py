"""Move a herdr tab so it sits directly after another tab in the same workspace.

Usage: python3 place_tab_after.py <tab_id> <after_tab_id>

The herdr CLI has no tab-move command; the server's `tab.move` method does,
and `insert_index` counts positions in the current `tab.list` order, before
the moved tab is removed, so "after X" is X's current index plus one.
"""

import json
import os
import socket
import sys


def call(method: str, params: dict) -> dict:
    with socket.socket(socket.AF_UNIX) as connection:
        connection.connect(os.environ["HERDR_SOCKET_PATH"])
        request = {"id": "place-tab-after", "method": method, "params": params}
        connection.sendall((json.dumps(request) + "\n").encode())
        reply = b""
        while not reply.endswith(b"\n"):
            chunk = connection.recv(65536)
            if not chunk:
                break
            reply += chunk
    response = json.loads(reply)
    if "error" in response:
        sys.exit(f"herdr {method} failed: {json.dumps(response['error'])}")
    return response["result"]


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    tab_id, after_tab_id = sys.argv[1], sys.argv[2]
    workspace_id = after_tab_id.split(":")[0]
    if tab_id.split(":")[0] != workspace_id:
        sys.exit(f"{tab_id} and {after_tab_id} are in different workspaces")

    order = [tab["tab_id"] for tab in call("tab.list", {"workspace_id": workspace_id})["tabs"]]
    for required in (tab_id, after_tab_id):
        if required not in order:
            sys.exit(f"{required} is not a tab in workspace {workspace_id}")

    target_index = order.index(after_tab_id) + 1
    moved = call("tab.move", {"tab_id": tab_id, "insert_index": target_index})
    final_order = [tab["tab_id"] for tab in moved["tabs"]]
    if final_order.index(tab_id) != final_order.index(after_tab_id) + 1:
        sys.exit(f"{tab_id} did not land after {after_tab_id}: {final_order}")
    print(" ".join(final_order))


if __name__ == "__main__":
    main()
