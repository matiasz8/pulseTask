UV ?= uv
PYTHON ?= 3.12

.PHONY: check-uv venv sync test lint typecheck run ci

check-uv:
	@command -v $(UV) >/dev/null 2>&1 || (echo "uv is required. Install from https://docs.astral.sh/uv/getting-started/installation/" && exit 1)

venv: check-uv
	$(UV) venv --python $(PYTHON)

sync: check-uv
	$(UV) sync --extra dev

test: check-uv
	$(UV) run pytest

lint: check-uv
	$(UV) run ruff check .

typecheck: check-uv
	$(UV) run mypy src

run: check-uv
	$(UV) run pulsetask

ci: lint typecheck test
