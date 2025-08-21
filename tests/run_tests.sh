#!/bin/bash

# JobSim Test Runner
# This script runs the comprehensive test suite for JobSim

set -e  # Exit on any error

echo "🚀 JobSim Test Suite Runner"
echo "============================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    print_error "Please run this script from the JobSim project root directory"
    exit 1
fi

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    print_warning "pytest not found. Installing test dependencies..."
    pip install pytest pytest-cov pytest-mock
fi

# Check if psutil is installed (for performance tests)
if ! python -c "import psutil" &> /dev/null; then
    print_warning "psutil not found. Installing for performance tests..."
    pip install psutil
fi

# Create test results directory
mkdir -p test_results

print_status "Starting JobSim test suite..."

# Run all tests with coverage
echo ""
print_status "Running all tests with coverage..."
python -m pytest tests/ \
    --cov=src/jobsim \
    --cov-report=html:test_results/coverage_html \
    --cov-report=term-missing \
    --cov-report=xml:test_results/coverage.xml \
    -v \
    --tb=short

# Check test results
if [ $? -eq 0 ]; then
    print_success "All tests passed! 🎉"
else
    print_error "Some tests failed. Check the output above for details."
    exit 1
fi

echo ""
print_status "Running specific test categories..."

# Run unit tests
echo ""
print_status "Running unit tests..."
python -m pytest tests/unit/ -v --tb=short

# Run integration tests
echo ""
print_status "Running integration tests..."
python -m pytest tests/integration/ -v --tb=short

# Run end-to-end tests
echo ""
print_status "Running end-to-end tests..."
python -m pytest tests/e2e/ -v --tb=short

# Run CLI tests
echo ""
print_status "Running CLI tests..."
python -m pytest tests/cli/ -v --tb=short

# Run performance tests
echo ""
print_status "Running performance tests..."
python -m pytest tests/performance/ -v --tb=short

echo ""
print_status "Test suite completed!"
print_status "Coverage report available at: test_results/coverage_html/index.html"
print_status "Test results available at: test_results/test_results.xml"

# Summary
echo ""
echo "📊 Test Summary"
echo "==============="
echo "✅ Unit tests: Core component functionality"
echo "✅ Integration tests: Component interactions"
echo "✅ End-to-end tests: Complete workflows"
echo "✅ CLI tests: Command line interfaces"
echo "✅ Performance tests: Scalability and efficiency"

echo ""
print_success "JobSim test suite completed successfully! 🚀"
