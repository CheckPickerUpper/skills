#!/usr/bin/env bash
set -euo pipefail

# Cuts a release from the changesets already pushed to main: starts the Release
# workflow, follows it to completion, and prints the published release page.

WORKFLOW="release.yml"

dispatched_after="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
gh workflow run "$WORKFLOW" --ref main

# workflow_dispatch does not return the run it created, so find the first run
# created at or after the dispatch.
run_id=""
for _ in $(seq 30); do
  run_id="$(gh run list --workflow "$WORKFLOW" --event workflow_dispatch --limit 5 \
    --json databaseId,createdAt \
    --jq "[.[] | select(.createdAt >= \"$dispatched_after\")] | last | .databaseId // empty")"
  [ -n "$run_id" ] && break
  sleep 2
done

if [ -z "$run_id" ]; then
  echo "error: the Release workflow was dispatched but no run appeared within 60s" >&2
  exit 1
fi

gh run watch "$run_id" --exit-status
gh release view --json url --jq .url
