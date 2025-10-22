#!/bin/bash

# PWC Contract Analysis System - Test Runner Script
# This script provides easy access to all testing functionality

set -e  # Exit on any error

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

# Function to check if API is running
check_api_running() {
    if curl -s http://localhost:8000/healthz > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to wait for API to be ready
wait_for_api() {
    print_status "Waiting for API to be ready..."
    local timeout=60
    local count=0

    while ! check_api_running; do
        if [ $count -ge $timeout ]; then
            print_error "API did not start within $timeout seconds"
            exit 1
        fi
        sleep 1
        count=$((count + 1))
    done

    print_success "API is ready!"
}

# Function to install dependencies
install_deps() {
    print_status "Installing test dependencies..."

    if [ -f "src/python/projects/api/requirements-test.txt" ]; then
        pip install -r src/python/projects/api/requirements-test.txt
    else
        print_error "Test requirements file not found"
        exit 1
    fi

    if [ -f "load_tests/requirements.txt" ]; then
        pip install -r load_tests/requirements.txt
    else
        print_warning "Load test requirements file not found"
    fi

    print_success "Dependencies installed!"
}

# Function to run unit tests
run_unit_tests() {
    print_status "Running unit tests..."

    cd src/python/projects/api

    if python -m pytest tests/ -v --tb=short; then
        print_success "Unit tests passed!"
    else
        print_error "Unit tests failed!"
        exit 1
    fi

    cd - > /dev/null
}

# Function to run unit tests with coverage
run_unit_tests_coverage() {
    print_status "Running unit tests with coverage..."

    cd src/python/projects/api

    if python -m pytest tests/ -v --cov=api --cov-report=html --cov-report=term; then
        print_success "Unit tests with coverage completed!"
        print_status "Coverage report available at: htmlcov/index.html"
    else
        print_error "Unit tests failed!"
        exit 1
    fi

    cd - > /dev/null
}

# Function to run load tests
run_load_tests() {
    print_status "Running load tests..."

    if ! check_api_running; then
        print_error "API is not running. Please start it with: docker-compose up -d"
        exit 1
    fi

    if locust -f load_tests/locustfile.py \
        --host=http://localhost:8000 \
        --users=10 \
        --spawn-rate=2 \
        --run-time=60s \
        --headless; then
        print_success "Load tests completed!"
    else
        print_error "Load tests failed!"
        exit 1
    fi
}

# Function to run stress tests
run_stress_tests() {
    print_status "Running stress tests..."

    if ! check_api_running; then
        print_error "API is not running. Please start it with: docker-compose up -d"
        exit 1
    fi

    if locust -f load_tests/stress_test.py \
        --host=http://localhost:8000 \
        --users=20 \
        --spawn-rate=3 \
        --run-time=120s \
        --headless; then
        print_success "Stress tests completed!"
    else
        print_error "Stress tests failed!"
        exit 1
    fi
}

# Function to generate load test report
generate_load_report() {
    print_status "Generating load test report..."

    if ! check_api_running; then
        print_error "API is not running. Please start it with: docker-compose up -d"
        exit 1
    fi

    local timestamp=$(date +%Y%m%d_%H%M%S)
    local report_file="load_test_report_${timestamp}.html"

    if locust -f load_tests/locustfile.py \
        --host=http://localhost:8000 \
        --users=25 \
        --spawn-rate=3 \
        --run-time=300s \
        --headless \
        --html="$report_file"; then
        print_success "Load test report generated: $report_file"
    else
        print_error "Load test report generation failed!"
        exit 1
    fi
}

# Function to run all tests
run_all_tests() {
    print_status "Running complete test suite..."

    # Run unit tests first
    run_unit_tests

    # Check if API is running for load tests
    if check_api_running; then
        run_load_tests
    else
        print_warning "API not running - skipping load tests"
        print_status "To run load tests, start API with: docker-compose up -d"
    fi

    print_success "All available tests completed!"
}

# Function to setup test environment
setup_test_env() {
    print_status "Setting up test environment..."

    # Install dependencies
    install_deps

    # Create necessary directories
    mkdir -p src/python/projects/api/htmlcov
    mkdir -p test_reports

    print_success "Test environment setup complete!"
}

# Function to clean test artifacts
clean_test_artifacts() {
    print_status "Cleaning test artifacts..."

    # Remove coverage files
    rm -rf src/python/projects/api/htmlcov/
    rm -f src/python/projects/api/.coverage
    rm -rf src/python/projects/api/.pytest_cache/

    # Remove load test reports
    rm -f load_test_report*.html
    rm -f performance_results*.csv
    rm -f baseline_performance*.csv
    rm -f current_performance*.csv

    # Remove test cache
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true

    print_success "Test artifacts cleaned!"
}

# Function to show usage
show_usage() {
    echo "PWC Contract Analysis System - Test Runner"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup              Setup test environment and install dependencies"
    echo "  unit               Run unit tests"
    echo "  unit-coverage      Run unit tests with coverage report"
    echo "  load               Run basic load tests (requires running API)"
    echo "  stress             Run stress tests (requires running API)"
    echo "  load-report        Generate detailed load test report"
    echo "  all                Run all available tests"
    echo "  clean              Clean test artifacts"
    echo "  deps               Install test dependencies"
    echo ""
    echo "Examples:"
    echo "  $0 setup           # Setup test environment"
    echo "  $0 unit            # Run unit tests"
    echo "  $0 all             # Run all tests"
    echo "  $0 load-report     # Generate load test report"
    echo ""
    echo "Prerequisites:"
    echo "  - For load tests: API must be running (docker-compose up -d)"
    echo "  - Python environment with pip available"
    echo ""
}

# Main script logic
case "${1:-help}" in
    "setup")
        setup_test_env
        ;;
    "deps")
        install_deps
        ;;
    "unit")
        run_unit_tests
        ;;
    "unit-coverage")
        run_unit_tests_coverage
        ;;
    "load")
        run_load_tests
        ;;
    "stress")
        run_stress_tests
        ;;
    "load-report")
        generate_load_report
        ;;
    "all")
        run_all_tests
        ;;
    "clean")
        clean_test_artifacts
        ;;
    "help"|*)
        show_usage
        ;;
esac