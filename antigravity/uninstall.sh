#!/usr/bin/env bash
set -euo pipefail
DEST="$HOME/.gemini/antigravity-cli/plugins/gauntlet-loop"
rm -rf "$DEST"
echo "Removed global Gauntlet plugin: $DEST"
echo "Workspace installs: remove <workspace>/.agents/plugins/gauntlet-loop."
