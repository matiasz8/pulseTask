#!/usr/bin/env bash
set -euo pipefail

APP_ID="com.matiasz8.pulsetask"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DESKTOP_SRC="$ROOT_DIR/resources/linux/$APP_ID.desktop"
ICON_SRC="$ROOT_DIR/src/pulse_task/ui/assets/$APP_ID.svg"

DESKTOP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
ICON_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor/scalable/apps"

mkdir -p "$DESKTOP_DIR" "$ICON_DIR"
install -m 0644 "$DESKTOP_SRC" "$DESKTOP_DIR/$APP_ID.desktop"
install -m 0644 "$ICON_SRC" "$ICON_DIR/$APP_ID.svg"

command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$DESKTOP_DIR" || true
command -v gtk-update-icon-cache >/dev/null 2>&1 && gtk-update-icon-cache -f -t "${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor" || true

echo "Installed desktop entry and icon for $APP_ID"
