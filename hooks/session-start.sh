#!/bin/sh
set -eu

# Each runtime's hooks file passes its own name.
# Literal plugin paths, so a static reader of the hooks files can follow them.
case "${1:-}" in
  claude)
    sheet="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/pstack-models.md"
    reader="${CLAUDE_PLUGIN_ROOT}/skills/setup-pstack/scripts/read-sheet.sh"
    ;;
  *)
    echo "session-start.sh: unknown runtime '${1:-}' (expected claude)" >&2
    exit 2
    ;;
esac

# A sheet that cannot be decoded counts as missing, so injection stays on.
if ! { [ -f "$sheet" ] && [ -r "$sheet" ] && normalized=$(sh "$reader" "$sheet"); }; then
  normalized=
fi
if printf '%s\n' "$normalized" | grep -qx 'session hook: off'; then
  exit 0
fi

cat "${CLAUDE_PLUGIN_ROOT}/hooks/session-start-context.md"
