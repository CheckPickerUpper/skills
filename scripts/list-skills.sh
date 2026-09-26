#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"

usage() {
  cat <<'USAGE'
Usage: ./scripts/list-skills.sh [--client <registered-agent>]

With no client, list every skill. The client may also be passed as one
positional argument. Registered agents are listed in scripts/agent-targets.json.
USAGE
}

CLIENT=""
if [ "$#" -gt 0 ]; then
  case "$1" in
    --help|-h)
      usage
      exit 0
      ;;
    --client)
      if [ "$#" -ne 2 ]; then
        echo "error: --client requires one value" >&2
        usage >&2
        exit 2
      fi
      CLIENT="$2"
      ;;
    --client=*)
      if [ "$#" -ne 1 ]; then
        echo "error: --client=... cannot be combined with another argument" >&2
        exit 2
      fi
      CLIENT="${1#--client=}"
      ;;
    -*)
      echo "error: unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
    *)
      if [ "$#" -ne 1 ]; then
        echo "error: a positional client cannot be combined with another argument" >&2
        exit 2
      fi
      CLIENT="$1"
      ;;
  esac
fi

if [ -n "$CLIENT" ] && ! command -v python3 >/dev/null 2>&1; then
  echo "error: python3 is required to read skill client metadata" >&2
  exit 2
fi

if [ -n "$CLIENT" ]; then
  if ! python3 "$REPO/scripts/skill-targets.py" --client "$CLIENT" --destination >/dev/null; then
    exit 2
  fi
fi

cd "$REPO"
while IFS= read -r skill_md; do
  if [ -z "$CLIENT" ]; then
    printf '%s\n' "$skill_md"
    continue
  fi
  if python3 "$REPO/scripts/skill-targets.py" --client "$CLIENT" "$skill_md"; then
    printf '%s\n' "$skill_md"
  else
    status=$?
    if [ "$status" -ne 1 ]; then
      exit "$status"
    fi
  fi
done < <(find skills -name SKILL.md -not -path '*/node_modules/*' -not -path '*/deprecated/*' -print | sort)
