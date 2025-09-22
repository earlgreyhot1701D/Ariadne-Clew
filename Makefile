.PHONY: help install test smoke quick lint format typecheck clean dev

# Default target
help:
	@echo "Ariadne Clew Development Commands"
	@echo "================================="
	@echo "make install    - Install all dependencies"
	@echo "make test       - Run backend unit tests (pytest)"
	@echo "make smoke      - Run end-to-end smoke tests"
	@echo "make quick      - Run quick local test script"
	@echo "make lint       - Run Python linting (flake8)"
	@echo "make format     - Format Python code (black)"
	@echo "make typecheck  - Run type checks (mypy)"
	@echo "make dev        - Start development servers"
	@echo "make clean      - Clean up build artifacts"

# Install dependencies
install:
	@echo "📦 Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "📦 Installing frontend dependencies..."
	npm install
	@echo "✅ Installation complete"

# Run unit tests
test:
	@echo "🧪 Running backend unit tests with pytest..."
	cd backend && python -m pytest tests/ -v
	@echo "✅ Unit tests complete"

# Run smoke tests
smoke:
	@echo "💨 Running smoke tests..."
	python scripts/smoke_test.py
	@echo "✅ Smoke tests complete"

# Quick local test runner
quick:
	@echo "⚡ Running quick test script..."
	bash scripts/quick_test_sh.sh
	@echo "✅ Quick test complete"

# Linting (Python)
lint:
	@echo "🔍 Running Python linter (flake8)..."
	flake8 backend
	@echo "✅ Linting complete"

# Formatting (Python)
format:
	@echo "🎨 Formatting Python code with black..."
	black backend scripts
	@echo "✅ Formatting complete"

# Type checking (Python)
typecheck:
	@echo "🔎 Running mypy type checks..."
	mypy backend
	@echo "✅ Type checking complete"

# Start development servers
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

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	@echo "✅ Cleanup complete"

# Full test suite
test-all: lint typecheck test smoke
	@echo "🎉 All tests (lint, typecheck, pytest, smoke) passed!"
