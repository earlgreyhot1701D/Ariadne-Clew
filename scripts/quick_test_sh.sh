#!/bin/bash
set -e

echo "🚀 Quick Ariadne Clew Test"
echo "=========================="

# Check if we're in the right directory
if [[ ! -f "package.json" || ! -d "backend" ]]; then
    echo "❌ Run this from the project root directory"
    exit 1
fi

echo "📦 Installing dependencies..."
cd backend && pip install -q -r requirements.txt && cd ..
npm install --silent

echo "🧪 Running backend tests..."
cd backend && python -m pytest tests/ -q && cd ..

echo "🔍 Running linter..."
npm run lint --silent

echo "💨 Running smoke test..."
python smoke_test.py

echo ""
echo "🎉 All tests passed! Your app is ready to go."
echo ""
echo "To start development:"
echo "  make dev    (or manually start backend/frontend)"
echo ""
echo "Available commands:"
echo "  make help   - See all available commands"