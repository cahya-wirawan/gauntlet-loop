#!/usr/bin/env bash
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="${CLAUDE_GAUNTLET_HOME:-$HOME/.claude/plugins/local/gauntlet-loop}"
BIN_DIR="${HOME}/.local/bin"
WRAPPER="${BIN_DIR}/claude-gauntlet"

mkdir -p "$(dirname "$DEST")" "$BIN_DIR"
rm -rf "$DEST"
cp -R "$SRC" "$DEST"

cat > "$WRAPPER" <<EOF
#!/usr/bin/env bash
exec claude --plugin-dir "$DEST" "\$@"
EOF
chmod +x "$WRAPPER"

echo "Installed Gauntlet Loop plugin:"
echo "  $DEST"
echo
echo "Created launcher:"
echo "  $WRAPPER"
echo
echo "Run:"
echo "  claude-gauntlet"
echo
echo "Then invoke:"
echo "  /gauntlet-loop:gauntlet <your task>"
