.PHONY: install dev build start lint test clean help

# Web development commands
install:
	npm install

dev:
	npm run dev

build:
	npm run build

start:
	npm start

lint:
	npm run lint

# Aliases for convenience
run: dev

ci: build

test:
	@echo "Testing not yet configured for web version"

clean:
	rm -rf .next node_modules

help:
	@echo "PulseTask v2 - Web Application"
	@echo ""
	@echo "Available commands:"
	@echo "  make install    Install dependencies"
	@echo "  make dev        Start development server (http://localhost:3000)"
	@echo "  make build      Build for production"
	@echo "  make start      Start production server"
	@echo "  make lint       Run ESLint"
	@echo "  make run        Alias for 'make dev'"
	@echo "  make clean      Remove build artifacts and node_modules"
	@echo "  make help       Show this help message"
