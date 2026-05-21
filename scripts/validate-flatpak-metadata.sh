#!/usr/bin/env bash
set -euo pipefail

APP_ID="com.matiasz8.pulsetask"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="$ROOT_DIR/packaging/flatpak/$APP_ID.json"
METAINFO="$ROOT_DIR/resources/linux/$APP_ID.metainfo.xml"
DESKTOP="$ROOT_DIR/resources/linux/$APP_ID.desktop"

for file in "$MANIFEST" "$METAINFO" "$DESKTOP"; do
	if [[ ! -f "$file" ]]; then
		echo "Missing required packaging file: $file" >&2
		exit 1
	fi
done

if ! command -v appstreamcli >/dev/null 2>&1; then
	echo "appstreamcli is required to validate metainfo. Install package: appstream" >&2
	exit 1
fi

if ! command -v desktop-file-validate >/dev/null 2>&1; then
	echo "desktop-file-validate is required. Install package: desktop-file-utils" >&2
	exit 1
fi

python3 - "$MANIFEST" "$APP_ID" <<'PY'
import json
import sys
from pathlib import Path

manifest = Path(sys.argv[1])
app_id = sys.argv[2]
raw = json.loads(manifest.read_text(encoding="utf-8"))

assert raw["app-id"] == app_id, "Manifest app-id mismatch"
assert raw["command"] == "pulsetask", "Manifest command must be pulsetask"
assert raw["runtime"] == "org.gnome.Platform", "Manifest runtime must be org.gnome.Platform"
assert raw["sdk"] == "org.gnome.Sdk", "Manifest sdk must be org.gnome.Sdk"
assert isinstance(raw.get("modules"), list) and raw["modules"], "Manifest modules must be defined"

print("Manifest JSON checks passed")
PY

python3 - "$METAINFO" "$DESKTOP" "$APP_ID" <<'PY'
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

metainfo = Path(sys.argv[1])
desktop = Path(sys.argv[2])
app_id = sys.argv[3]

root = ET.fromstring(metainfo.read_text(encoding="utf-8"))
component_id = root.findtext("id")
launchable = root.find("launchable")
provides_binary = root.find("provides/binary")

assert component_id == app_id, "Metainfo component id mismatch"
assert launchable is not None and launchable.text == desktop.name, "Metainfo launchable mismatch"
assert provides_binary is not None and provides_binary.text == "pulsetask", "Metainfo binary missing"

print("Metainfo XML checks passed")
PY

desktop-file-validate "$DESKTOP"
appstreamcli validate --no-net "$METAINFO"

echo "Flatpak/AppStream metadata validation passed"
