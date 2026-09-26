#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"

usage() {
  cat <<'USAGE'
Usage: ./scripts/link-skills-all.sh [--replace-existing]

Without --replace-existing, existing real skill directories are preserved and
cause a clear failure. With it, conflicting directories are moved to
recoverable per-agent backups before the repo copies are linked.
USAGE
}

REPLACE_EXISTING=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --help|-h)
      usage
      exit 0
      ;;
    --replace-existing)
      REPLACE_EXISTING=1
      shift
      ;;
    *)
      echo "error: unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if ! command -v python3 >/dev/null 2>&1; then
  echo "error: python3 is required to read the agent registry" >&2
  exit 2
fi

if ! clients="$(python3 "$REPO/scripts/skill-targets.py" --list-clients)"; then
  exit 2
fi

while IFS= read -r client; do
  [ -n "$client" ] || continue
  if [ "$REPLACE_EXISTING" -eq 1 ]; then
    "$REPO/scripts/link-skills.sh" --client "$client" --replace-existing
  else
    "$REPO/scripts/link-skills.sh" --client "$client"
  fi
done <<<"$clients"
