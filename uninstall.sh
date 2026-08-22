#!/usr/bin/env bash
set -euo pipefail
DEST="${CLAUDE_GAUNTLET_HOME:-$HOME/.claude/plugins/local/gauntlet-loop}"
WRAPPER="${HOME}/.local/bin/claude-gauntlet"
rm -rf "$DEST"
rm -f "$WRAPPER"
echo "Removed Gauntlet Loop local plugin and launcher."
