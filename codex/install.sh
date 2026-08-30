#!/usr/bin/env bash
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="${1:-$(pwd)}"

mkdir -p "$DEST/.agents/skills" "$DEST/.codex/agents"

rm -rf "$DEST/.agents/skills/gauntlet-loop"
cp -R "$SRC/.agents/skills/gauntlet-loop" "$DEST/.agents/skills/gauntlet-loop"
cp -R "$SRC/.codex/agents/." "$DEST/.codex/agents/"

echo "Installed Codex Gauntlet skill into: $DEST"
echo
echo "Invoke in Codex with:"
echo '  $gauntlet-loop <your task>'
echo
echo "Optional: merge AGENTS.gauntlet-snippet.md into your repository AGENTS.md."
