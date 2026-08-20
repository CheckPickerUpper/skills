#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"

declare -a DESTINATIONS=(
  "${CODEX_HOME:-$HOME/.codex}/skills"
  "${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
  "${PI_SKILLS_DIR:-$HOME/.pi/agent/skills}"
)

if [ -n "${SKILL_CLIENT_DIRS:-}" ]; then
  IFS=: read -r -a EXTRA_DESTINATIONS <<< "$SKILL_CLIENT_DIRS"
  DESTINATIONS+=("${EXTRA_DESTINATIONS[@]}")
fi

mapfile -t SKILL_DIRS < <(
  find "$REPO/skills" -mindepth 3 -maxdepth 3 -type f -name SKILL.md -print |
    sort |
    while IFS= read -r skill_md; do
      dirname "$skill_md"
    done
)

if [ "${#SKILL_DIRS[@]}" -eq 0 ]; then
  echo "error: no published skills found under $REPO/skills" >&2
  exit 1
fi

linked=0
for destination in "${DESTINATIONS[@]}"; do
  [ -n "$destination" ] || continue
  mkdir -p "$destination"
  for source in "${SKILL_DIRS[@]}"; do
    name="$(basename "$source")"
    target="$destination/$name"
    if [ -e "$target" ] || [ -L "$target" ]; then
      if [ ! -L "$target" ]; then
        echo "error: refusing to overwrite existing directory $target" >&2
        exit 1
      fi
      resolved="$(readlink -f "$target")"
      expected="$(readlink -f "$source")"
      if [ "$resolved" != "$expected" ]; then
        echo "error: refusing to replace foreign symlink $target -> $resolved" >&2
        exit 1
      fi
    else
      ln -s "$source" "$target"
    fi
    linked=$((linked + 1))
  done
  echo "installed ${#SKILL_DIRS[@]} skills in $destination"
done

echo "verified $linked client skill links"
