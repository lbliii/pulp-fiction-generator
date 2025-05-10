#!/bin/bash

# Run tests for the Pulp Fiction Generator
# This script runs unit tests by default, and optionally integration tests

set -e

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Activate virtual environment if it exists
if [ -d "$PROJECT_ROOT/.venv" ]; then
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source "$PROJECT_ROOT/.venv/Scripts/activate"
    else
        source "$PROJECT_ROOT/.venv/bin/activate"
    fi
    echo "Activated virtual environment"
fi

# Parse command line arguments
RUN_UNIT_TESTS=true
RUN_INTEGRATION_TESTS=false
VERBOSE=false

for arg in "$@"; do
    case $arg in
        --all)
            RUN_INTEGRATION_TESTS=true
            ;;
        --integration-only)
            RUN_UNIT_TESTS=false
            RUN_INTEGRATION_TESTS=true
            ;;
        --unit-only)
            RUN_INTEGRATION_TESTS=false
            ;;
        -v|--verbose)
            VERBOSE=true
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --all                Run all tests, including integration tests"
            echo "  --integration-only   Run only integration tests"
            echo "  --unit-only          Run only unit tests (default)"
            echo "  -v, --verbose        Run tests in verbose mode"
            echo "  --help               Show this help message"
            exit 0
            ;;
    esac
done

# Set pytest arguments
PYTEST_ARGS="-xvs" # By default, show test output and stop on first failure

# Change to project root directory
cd "$PROJECT_ROOT"

# Run unit tests
if [ "$RUN_UNIT_TESTS" = true ]; then
    echo "Running unit tests..."
    if [ "$VERBOSE" = true ]; then
        python -m pytest tests/unit $PYTEST_ARGS
    else
        python -m pytest tests/unit -v
    fi
    echo "Unit tests completed."
fi

# Run integration tests
if [ "$RUN_INTEGRATION_TESTS" = true ]; then
    echo "Running integration tests..."
    if [ "$VERBOSE" = true ]; then
        python -m pytest tests/integration $PYTEST_ARGS
    else
        python -m pytest tests/integration -v
    fi
    echo "Integration tests completed."
fi

echo "All tests completed successfully!" 