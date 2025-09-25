#!/bin/bash

# Xiaozhi ESP32 Server - Test Runner Script
# This script runs all tests for the project

set -e  # Exit on any error

echo "🧪 Xiaozhi ESP32 Server - Test Suite"
echo "===================================="

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
if [ ! -f "main/xiaozhi-server/config.yaml" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Python Backend Tests
echo ""
print_status "Running Python Backend Tests..."
echo "----------------------------------------"

if [ -d "main/xiaozhi-server/test" ]; then
    cd main/xiaozhi-server
    
    # Check if Python is available
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python not found. Please install Python 3.8+"
        exit 1
    fi
    
    # Install test dependencies if needed
    if [ -f "requirements.txt" ]; then
        print_status "Installing Python dependencies..."
        $PYTHON_CMD -m pip install -r requirements.txt > /dev/null 2>&1 || print_warning "Failed to install some dependencies"
    fi
    
    # Run Python tests
    if $PYTHON_CMD test/test_runner.py; then
        print_success "Python backend tests passed!"
    else
        print_error "Python backend tests failed!"
        exit 1
    fi
    
    cd ../..
else
    print_warning "Python test directory not found, skipping Python tests"
fi

# Java Backend Tests
echo ""
print_status "Running Java Backend Tests..."
echo "-----------------------------------"

if [ -d "main/manager-api" ] && [ -f "main/manager-api/pom.xml" ]; then
    cd main/manager-api
    
    # Check if Maven is available
    if ! command -v mvn &> /dev/null; then
        print_warning "Maven not found, skipping Java tests"
    else
        # Run Java tests
        if mvn test -q; then
            print_success "Java backend tests passed!"
        else
            print_error "Java backend tests failed!"
            exit 1
        fi
    fi
    
    cd ../..
else
    print_warning "Java project directory not found, skipping Java tests"
fi

# Frontend Tests
echo ""
print_status "Running Frontend Tests..."
echo "-------------------------------"

if [ -d "main/manager-web" ] && [ -f "main/manager-web/package.json" ]; then
    cd main/manager-web
    
    # Check if Node.js is available
    if ! command -v npm &> /dev/null; then
        print_warning "Node.js/npm not found, skipping frontend tests"
    else
        # Install dependencies if needed
        if [ ! -d "node_modules" ]; then
            print_status "Installing frontend dependencies..."
            npm install > /dev/null 2>&1 || print_warning "Failed to install some dependencies"
        fi
        
        # Check if test dependencies are installed
        if npm list jest @vue/test-utils vue-jest > /dev/null 2>&1; then
            # Run frontend tests
            if npm test -- --passWithNoTests > /dev/null 2>&1; then
                print_success "Frontend tests passed!"
            else
                print_error "Frontend tests failed!"
                exit 1
            fi
        else
            print_warning "Frontend test dependencies not installed, skipping frontend tests"
            print_status "To install test dependencies, run: npm install --save-dev jest @vue/test-utils vue-jest babel-jest"
        fi
    fi
    
    cd ../..
else
    print_warning "Frontend project directory not found, skipping frontend tests"
fi

# Summary
echo ""
echo "===================================="
print_success "All available tests completed successfully!"
echo ""
print_status "Test Summary:"
print_status "✓ Python Backend Tests"
print_status "✓ Java Backend Tests" 
print_status "✓ Frontend Tests"
echo ""
print_status "For detailed test documentation, see: docs/testing-guide.md"
echo ""

# Optional: Run specific test categories
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --python-only    Run only Python tests"
    echo "  --java-only      Run only Java tests"
    echo "  --frontend-only  Run only frontend tests"
    echo "  --help, -h       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --python-only"
    echo "  $0 --java-only"
    echo "  $0 --frontend-only"
fi

# Handle specific test categories
case "$1" in
    --python-only)
        print_status "Running Python tests only..."
        cd main/xiaozhi-server
        $PYTHON_CMD test/test_runner.py
        ;;
    --java-only)
        print_status "Running Java tests only..."
        cd main/manager-api
        mvn test -q
        ;;
    --frontend-only)
        print_status "Running frontend tests only..."
        cd main/manager-web
        npm test -- --passWithNoTests
        ;;
esac
