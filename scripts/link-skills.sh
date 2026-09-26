#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"

usage() {
  cat <<'USAGE'
Usage: ./scripts/link-skills.sh [--client <registered-agent>] [--replace-existing]

The client may also be passed as one positional argument. With no client,
Claude is selected for backwards compatibility. --replace-existing moves a
conflicting existing skill directory to a recoverable backup before linking
the repo copy. Registered agents are listed in scripts/agent-targets.json.
USAGE
}

CLIENT="claude"
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
    --client)
      if [ "$#" -lt 2 ]; then
        echo "error: --client requires one value" >&2
        usage >&2
        exit 2
      fi
      CLIENT="$2"
      shift 2
      ;;
    --client=*)
      CLIENT="${1#--client=}"
      shift
      ;;
    -*)
      echo "error: unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
    *)
      if [ "$CLIENT" != "claude" ]; then
        echo "error: a positional client cannot be combined with --client" >&2
        usage >&2
        exit 2
      fi
      CLIENT="$1"
      shift
      ;;
  esac
done

if ! command -v python3 >/dev/null 2>&1; then
  echo "error: python3 is required to read skill client metadata" >&2
  exit 2
fi

if ! DEST="$(python3 "$REPO/scripts/skill-targets.py" --client "$CLIENT" --destination)"; then
  exit 2
fi

if [ -z "$DEST" ] || [ "$DEST" = "/" ]; then
  echo "error: refusing an empty or root skill destination" >&2
  exit 2
fi

if [ -L "$DEST" ]; then
  resolved="$(readlink -f "$DEST")"
  case "$resolved" in
    "$REPO"|"$REPO"/*)
      echo "error: $DEST is a symlink into this repo ($resolved)." >&2
      exit 1
      ;;
  esac
fi

mkdir -p "$DEST"

found=0
backup_dir=""
while IFS= read -r -d '' skill_md; do
  found=1
  src="$(dirname "$skill_md")"
  name="$(basename "$src")"
  target="$DEST/$name"

  if python3 "$REPO/scripts/skill-targets.py" --client "$CLIENT" "$skill_md"; then
    if [ -L "$target" ]; then
      resolved="$(readlink -f "$target")"
      expected="$(readlink -f "$src")"
      if [ "$resolved" != "$expected" ]; then
        echo "error: refusing to replace foreign symlink $target -> $resolved" >&2
        exit 1
      fi
      echo "kept $name in $CLIENT"
    elif [ -e "$target" ]; then
      if [ "$REPLACE_EXISTING" -ne 1 ]; then
        echo "error: refusing to overwrite existing path $target" >&2
        echo "hint: rerun with --replace-existing to move it to a recoverable backup" >&2
        exit 1
      fi
      if [ -z "$backup_dir" ]; then
        backup_dir="$(mktemp -d "$(dirname "$DEST")/.checkpickerupper-skill-backups-${CLIENT}.XXXXXX")"
      fi
      mv "$target" "$backup_dir/$name"
      ln -s "$src" "$target"
      echo "replaced $name for $CLIENT; previous copy moved to $backup_dir/$name"
    else
      ln -s "$src" "$target"
      echo "linked $name -> $src for $CLIENT"
    fi
    continue
  else
    status=$?
    if [ "$status" -ne 1 ]; then
      exit "$status"
    fi
    if [ -L "$target" ]; then
      resolved="$(readlink -f "$target")"
      expected="$(readlink -f "$src")"
      if [ "$resolved" = "$expected" ]; then
        unlink "$target"
        echo "removed $name from $CLIENT"
      fi
    fi
  fi
done < <(find "$REPO/skills" -name SKILL.md -not -path '*/node_modules/*' -not -path '*/deprecated/*' -print0 | sort -z)

if [ "$found" -eq 0 ]; then
  echo "error: no skills found under $REPO/skills" >&2
  exit 1
fi

echo "verified $CLIENT skill links in $DEST"
