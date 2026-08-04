.PHONY: install dev dev-desktop build build-desktop start start-desktop lint test clean help

# Web development commands
install:
	npm install

dev:
	npm run dev

dev-desktop:
	npm run dev:desktop

build:
	npm run build

build-desktop:
	npm run build:desktop

start:
	npm start

start-desktop:
	npm run start:desktop

lint:
	npm run lint

# Aliases for convenience
run: dev
run-desktop: dev-desktop

ci: build

test:
	@echo "Testing not yet configured for web version"

clean:
	rm -rf .next node_modules

help:
	@echo "PulseTask v0.2.0 - Web & Desktop Application"
	@echo ""
	@echo "Web Commands:"
	@echo "  make install     Install dependencies"
	@echo "  make dev         Start web dev server (http://localhost:3000)"
	@echo "  make run         Alias for 'make dev'"
	@echo "  make build       Build web for production"
	@echo "  make start       Start web production server"
	@echo ""
	@echo "Desktop Commands (Ubuntu/Linux):"
	@echo "  make dev-desktop         Start desktop app with dev server"
	@echo "  make run-desktop         Alias for 'make dev-desktop'"
	@echo "  make build-desktop       Build desktop .deb installer"
	@echo "  make start-desktop       Run packaged desktop app"
	@echo ""
	@echo "Maintenance:"
	@echo "  make lint        Run ESLint"
	@echo "  make clean       Remove build artifacts and node_modules"
	@echo "  make help        Show this help message"
