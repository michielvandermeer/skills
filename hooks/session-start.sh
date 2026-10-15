#!/bin/sh
set -eu

# Claude Code sets CLAUDE_PLUGIN_ROOT; run by hand, the plugin root is this script's parent directory.
root="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
sheet="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/pstack-models.md"

# A sheet that cannot be decoded counts as missing, so injection stays on.
if ! normalized=$(sh "$root/skills/setup-pstack/scripts/read-sheet.sh" "$sheet"); then
  normalized=
fi
if printf '%s\n' "$normalized" | grep -qx 'session hook: off'; then
  exit 0
fi

cat "$root/hooks/session-start-context.md"
