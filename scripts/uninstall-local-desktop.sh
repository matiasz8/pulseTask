#!/usr/bin/env bash
set -euo pipefail

APP_ID="com.matiasz8.pulsetask"
DESKTOP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
ICON_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor/scalable/apps"

rm -f "$DESKTOP_DIR/$APP_ID.desktop"
rm -f "$ICON_DIR/$APP_ID.svg"

command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$DESKTOP_DIR" || true
command -v gtk-update-icon-cache >/dev/null 2>&1 && gtk-update-icon-cache -f -t "${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor" || true

echo "Uninstalled desktop entry and icon for $APP_ID"
