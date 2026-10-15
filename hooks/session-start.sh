#!/bin/sh
set -eu

root="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
sheet="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/pstack-models.md"

if ! normalized=$(sh "$root/skills/setup/scripts/read-sheet.sh" "$sheet"); then
  normalized=
fi
if printf '%s\n' "$normalized" | grep -qx 'session hook: off'; then
  exit 0
fi

cat "$root/hooks/session-start-context.md"
