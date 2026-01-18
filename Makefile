# Real Estate MCP Server - Makefile
# Usage: make <target>

.PHONY: help install dev test lint fix format clean \
        docker-up docker-down docker-build docker-logs docker-shell \
        seed pgadmin inspector

# Default target
help:
	@echo "Real Estate MCP Server"
	@echo ""
	@echo "Development:"
	@echo "  make install    - Install dependencies with uv"
	@echo "  make dev        - Run development server"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Check code with ruff"
	@echo "  make fix        - Fix code issues with ruff"
	@echo "  make format     - Format code with ruff"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up      - Start all services"
	@echo "  make docker-down    - Stop all services"
	@echo "  make docker-build   - Rebuild containers"
	@echo "  make docker-logs    - View container logs"
	@echo "  make docker-shell   - Shell into mcp-server container"
	@echo ""
	@echo "Database:"
	@echo "  make seed       - Seed database with sample data"
	@echo "  make pgadmin    - Start pgAdmin (http://localhost:5050)"
	@echo ""
	@echo "Testing:"
	@echo "  make inspector  - Run MCP Inspector"

# =============================================================================
# Development
# =============================================================================

install:
	uv sync --all-extras

dev:
	uv run uvicorn src.main:app --reload --port 8000

test:
	uv run pytest -v

lint:
	uv run ruff check .

fix:
	uv run ruff check . --fix

format:
	uv run ruff format .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# =============================================================================
# Docker
# =============================================================================

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-build:
	docker-compose up -d --build

docker-logs:
	docker-compose logs -f

docker-shell:
	docker-compose exec mcp-server /bin/sh

# =============================================================================
# Database
# =============================================================================

seed:
	docker-compose --profile seed up seed

pgadmin:
	docker-compose --profile tools up -d pgadmin
	@echo "pgAdmin available at http://localhost:5050"

# =============================================================================
# Testing Tools
# =============================================================================

inspector:
	npx -y @modelcontextprotocol/inspector --config mcp-inspector.json --server real-estate-mcp
