#!/usr/bin/env bash
set -euo pipefail

APP_ID="com.matiasz8.pulsetask"
DESKTOP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
SEARCH_PROVIDER_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/gnome-shell/search-providers"
ICON_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor/scalable/apps"
BIN_DIR="${XDG_BIN_HOME:-$HOME/.local/bin}"

rm -f "$DESKTOP_DIR/$APP_ID.desktop"
rm -f "$SEARCH_PROVIDER_DIR/org.gnome.Pulse-search-provider.desktop"
rm -f "$ICON_DIR/$APP_ID.svg"
rm -f "$ICON_DIR/org.gnome.Pulse.svg"
rm -f "$BIN_DIR/$APP_ID"

command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$DESKTOP_DIR" || true
command -v gtk-update-icon-cache >/dev/null 2>&1 && gtk-update-icon-cache -f -t "${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor" || true

echo "Uninstalled desktop entry and icon for $APP_ID"
