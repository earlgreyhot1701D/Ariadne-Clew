.PHONY: help install test test-backend test-agent integration smoke quick lint format typecheck clean dev

# Default target
help:
	@echo "Ariadne Clew Development Commands"
	@echo "================================="
	@echo "make install      - Install all dependencies"
	@echo "make test         - Run all tests (backend + agent + integration)"
	@echo "make test-backend - Run backend unit tests only"
	@echo "make test-agent   - Run agent unit tests only"
	@echo "make integration  - Run integration tests"
	@echo "make smoke        - Run end-to-end smoke tests"
	@echo "make quick        - Run quick local test script"
	@echo "make lint         - Run Python linting"
	@echo "make format       - Format Python code"
	@echo "make typecheck    - Run type checks"
	@echo "make dev          - Start development servers"
	@echo "make clean        - Clean up build artifacts"

# Install dependencies
install:
	@echo "📦 Installing dependencies from requirements.txt..."
	pip install -r requirements.txt
	@echo "📦 Installing frontend dependencies..."
	npm install
	@echo "✅ Installation complete"

# Run all tests
test: test-backend test-agent integration
	@echo "🎉 All tests passed!"

# Run backend unit tests (your original Flask API)
test-backend:
	@echo "🧪 Running backend unit tests..."
	cd backend && python -m pytest tests/ -v
	@echo "✅ Backend tests complete"

# Run agent unit tests (root-level agent modules)
test-agent:
	@echo "🧪 Running agent unit tests..."
	python -m pytest tests/ -v
	@echo "✅ Agent tests complete"

# Run integration tests (full pipeline)
integration:
	@echo "🔄 Running integration tests..."
	python integration_test.py
	@echo "✅ Integration tests complete"

# Run smoke tests (your original)
smoke:
	@echo "💨 Running smoke tests..."
	python scripts/smoke_test.py
	@echo "✅ Smoke tests complete"

# Quick local test runner (your original)
quick:
	@echo "⚡ Running quick test script..."
	bash scripts/quick_test_sh.sh
	@echo "✅ Quick test complete"

# Linting (updated to include root-level code)
lint:
	@echo "🔍 Running Python linter..."
	ruff . --exclude=public,infra
	@echo "✅ Linting complete"

# Formatting (updated to include root-level code)
format:
	@echo "🎨 Formatting Python code..."
	black . --exclude="public|infra"
	@echo "✅ Formatting complete"

# Type checking (updated to include root-level code)
typecheck:
	@echo "🔬 Running type checks..."
	mypy . --exclude="public|infra"
	@echo "✅ Type checking complete"

# Start development servers (your original)
dev:
	@echo "🚀 Starting development servers..."
	@echo "Backend will be at http://localhost:5001"
	@echo "Frontend will be at http://localhost:8000"
	@echo "Press Ctrl+C to stop both servers"
	@make -j2 dev-backend dev-frontend

dev-backend:
	cd backend && python app.py

dev-frontend:
	cd public && python -m http.server 8000

# Clean up (your original)
clean:
	@echo "🧹 Cleaning up..."
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	@echo "✅ Cleanup complete"

# Full quality check
quality: format lint typecheck
	@echo "✨ All quality checks passed!"

# Full test suite (comprehensive)
test-all: quality test smoke
	@echo "🏆 Complete test suite passed!"
