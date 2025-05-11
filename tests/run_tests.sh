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
WITH_COVERAGE=false
COVERAGE_REPORT_TYPE="term"

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
        --with-coverage)
            WITH_COVERAGE=true
            ;;
        --coverage-html)
            WITH_COVERAGE=true
            COVERAGE_REPORT_TYPE="html"
            ;;
        --coverage-xml)
            WITH_COVERAGE=true
            COVERAGE_REPORT_TYPE="xml"
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --all                Run all tests, including integration tests"
            echo "  --integration-only   Run only integration tests"
            echo "  --unit-only          Run only unit tests (default)"
            echo "  -v, --verbose        Run tests in verbose mode"
            echo "  --with-coverage      Generate test coverage report (terminal)"
            echo "  --coverage-html      Generate HTML coverage report"
            echo "  --coverage-xml       Generate XML coverage report"
            echo "  --help               Show this help message"
            exit 0
            ;;
    esac
done

# Set pytest arguments
PYTEST_ARGS="-xvs" # By default, show test output and stop on first failure

# Add coverage arguments if enabled
if [ "$WITH_COVERAGE" = true ]; then
    echo "Running tests with coverage enabled"
    COVERAGE_ARGS="--cov=pulp_fiction_generator --cov-report=$COVERAGE_REPORT_TYPE"
    
    # Create the coverage directory if using HTML reports
    if [ "$COVERAGE_REPORT_TYPE" = "html" ]; then
        mkdir -p "$PROJECT_ROOT/coverage"
        COVERAGE_ARGS="$COVERAGE_ARGS:$PROJECT_ROOT/coverage"
        echo "Coverage report will be saved to $(realpath $PROJECT_ROOT/coverage)"
    fi
    
    # Add coverage exclusions
    COVERAGE_ARGS="$COVERAGE_ARGS --cov-config=$PROJECT_ROOT/.coveragerc"
    
    # Create a basic .coveragerc file if it doesn't exist
    if [ ! -f "$PROJECT_ROOT/.coveragerc" ]; then
        echo "Creating default .coveragerc file"
        cat > "$PROJECT_ROOT/.coveragerc" << EOF
[run]
omit = 
    */__pycache__/*
    */.venv/*
    */tests/*
    */plugins/*
    *__init__.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
    if __name__ == .__main__.:
    pass
EOF
    fi
else
    COVERAGE_ARGS=""
fi

# Change to project root directory
cd "$PROJECT_ROOT"

# Run unit tests
if [ "$RUN_UNIT_TESTS" = true ]; then
    echo "Running unit tests..."
    if [ "$VERBOSE" = true ]; then
        python -m pytest tests/unit $PYTEST_ARGS $COVERAGE_ARGS
    else
        python -m pytest tests/unit -v $COVERAGE_ARGS
    fi
    echo "Unit tests completed."
fi

# Run integration tests
if [ "$RUN_INTEGRATION_TESTS" = true ]; then
    echo "Running integration tests..."
    if [ "$VERBOSE" = true ]; then
        python -m pytest tests/integration $PYTEST_ARGS $COVERAGE_ARGS
    else
        python -m pytest tests/integration -v $COVERAGE_ARGS
    fi
    echo "Integration tests completed."
fi

# Generate a summary if coverage was enabled
if [ "$WITH_COVERAGE" = true ]; then
    if [ "$COVERAGE_REPORT_TYPE" = "html" ]; then
        echo "HTML coverage report generated at $PROJECT_ROOT/coverage/index.html"
    elif [ "$COVERAGE_REPORT_TYPE" = "xml" ]; then
        echo "XML coverage report generated at $PROJECT_ROOT/coverage.xml"
    else
        echo "Coverage report generated in terminal output"
    fi
fi

echo "All tests completed successfully!" 