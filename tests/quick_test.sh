#!/bin/bash

# Quick Test Runner for JobSim
# Runs basic tests without full coverage analysis

set -e

echo "🧪 JobSim Quick Test Runner"
echo "============================"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Please run this script from the JobSim project root directory"
    exit 1
fi

# Install test dependencies if needed
if ! command -v pytest &> /dev/null; then
    echo "⚠️  Installing test dependencies..."
    pip install pytest pytest-cov pytest-mock
fi

# Run basic tests
echo ""
echo "🔍 Running basic tests..."
cd src && python -m pytest ../tests/unit/ ../tests/integration/ -v --tb=short

echo ""
echo "✅ Quick test completed!"
echo "Run './tests/run_tests.sh' for full test suite with coverage"
