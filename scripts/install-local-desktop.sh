#!/usr/bin/env bash
set -euo pipefail

APP_ID="com.matiasz8.pulsetask"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ICON_SRC="$ROOT_DIR/src/pulse_task/ui/assets/$APP_ID.svg"

DESKTOP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
SEARCH_PROVIDER_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/gnome-shell/search-providers"
ICON_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor/scalable/apps"
BIN_DIR="${XDG_BIN_HOME:-$HOME/.local/bin}"
LAUNCHER_PATH="$BIN_DIR/$APP_ID"
SEARCH_PROVIDER_SRC="$ROOT_DIR/data/org.gnome.Pulse-search-provider.desktop"
SEARCH_PROVIDER_DEST="$SEARCH_PROVIDER_DIR/org.gnome.Pulse-search-provider.desktop"

mkdir -p "$DESKTOP_DIR" "$SEARCH_PROVIDER_DIR" "$ICON_DIR" "$BIN_DIR"

cat >"$LAUNCHER_PATH" <<EOF
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$ROOT_DIR"

if [[ -x "\$ROOT_DIR/.venv/bin/pulsetask" ]]; then
	exec "\$ROOT_DIR/.venv/bin/pulsetask"
fi

if command -v pulsetask >/dev/null 2>&1; then
	exec "\$(command -v pulsetask)"
fi

if command -v uv >/dev/null 2>&1; then
	cd "\$ROOT_DIR"
	exec uv run pulsetask
fi

echo "PulseTask launcher error: no runtime found (missing .venv/bin/pulsetask and uv)." >&2
exit 1
EOF
chmod +x "$LAUNCHER_PATH"

cat >"$DESKTOP_DIR/$APP_ID.desktop" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=PulseTask
Comment=Visible deadlines and real focus
Exec=$LAUNCHER_PATH
TryExec=$LAUNCHER_PATH
Icon=$APP_ID
Terminal=false
Categories=Utility;Office;
StartupNotify=true
StartupWMClass=$APP_ID
EOF

install -m 0644 "$ICON_SRC" "$ICON_DIR/$APP_ID.svg"
install -m 0644 "$ICON_SRC" "$ICON_DIR/org.gnome.Pulse.svg"
install -m 0644 "$SEARCH_PROVIDER_SRC" "$SEARCH_PROVIDER_DEST"

command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$DESKTOP_DIR" || true
command -v gtk-update-icon-cache >/dev/null 2>&1 && gtk-update-icon-cache -f -t "${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor" || true

echo "Installed desktop entry and icon for $APP_ID"
