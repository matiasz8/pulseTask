UV ?= uv
PYTHON ?= 3.12

.PHONY: check-uv venv sync doctor-gtk test lint typecheck run ci install-desktop uninstall-desktop flatpak-build flatpak-install flatpak-run flatpak-validate metrics-report

check-uv:
	@command -v $(UV) >/dev/null 2>&1 || (echo "uv is required. Install from https://docs.astral.sh/uv/getting-started/installation/" && exit 1)

venv: check-uv
	$(UV) venv --python $(PYTHON) --system-site-packages

sync: check-uv
	$(UV) sync --extra dev

doctor-gtk: check-uv
	$(UV) run python -c "import gi; gi.require_version('Gtk', '4.0'); gi.require_version('Adw', '1'); print('GTK bindings OK')"

test: check-uv
	$(UV) run pytest

lint: check-uv
	$(UV) run ruff check .

typecheck: check-uv
	$(UV) run mypy src

run: check-uv
	$(UV) run pulsetask

ci: lint typecheck test

install-desktop:
	bash scripts/install-local-desktop.sh

uninstall-desktop:
	bash scripts/uninstall-local-desktop.sh

flatpak-build:
	flatpak-builder --force-clean build-flatpak packaging/flatpak/com.matiasz8.pulsetask.json

flatpak-install: flatpak-build
	flatpak-builder --user --install --force-clean build-flatpak packaging/flatpak/com.matiasz8.pulsetask.json

flatpak-run:
	flatpak run com.matiasz8.pulsetask

flatpak-validate:
	bash scripts/validate-flatpak-metadata.sh

metrics-report: check-uv
	$(UV) run pulsetask-metrics
