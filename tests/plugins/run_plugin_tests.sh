#!/bin/bash
# Run all plugin system tests with coverage

set -e

echo "Running plugin system coverage tests..."

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR/../.."

# Make sure coverage is installed
pip show coverage > /dev/null 2>&1 || pip install coverage

# Reset coverage data
python -m coverage erase

# Run the plugin tests with coverage
python -m coverage run -a tests/plugins/plugin_coverage.py
python -m coverage run -a tests/plugins/plugin_hooks_coverage.py
python -m coverage run -a tests/plugins/plugin_manager_coverage.py

# Generate a coverage report
echo -e "\nGenerating coverage report...\n"
python -m coverage report -m --include="*/pulp_fiction_generator/plugins/*"

# Optionally generate an HTML report if specified
if [[ "$1" == "--html" ]]; then
    echo -e "\nGenerating HTML coverage report..."
    python -m coverage html --include="*/pulp_fiction_generator/plugins/*" -d coverage/plugins
    echo "HTML report generated at coverage/plugins/index.html"
fi

echo -e "\nPlugin system tests completed!" 