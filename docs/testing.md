# Testing Guide

This document provides information about the test organization, how to run tests, and how to analyze test coverage for the Pulp Fiction Generator.

## Test Organization

The test suite is organized into several directories:

- `tests/unit/`: Unit tests for individual components
- `tests/integration/`: Integration tests for component interactions
- `tests/visualization/`: Visualization tests and outputs

## Running Tests

The project includes a test runner script to make testing easier:

```bash
# Run only unit tests (default)
./tests/run_tests.sh

# Run all tests, including integration tests
./tests/run_tests.sh --all

# Run only integration tests
./tests/run_tests.sh --integration-only

# Run tests with verbose output
./tests/run_tests.sh --verbose
```

## Coverage Reporting

The test suite includes coverage reporting using pytest-cov. To run tests with coverage reporting:

```bash
# Generate a terminal coverage report
./tests/run_tests.sh --with-coverage

# Generate an HTML coverage report
./tests/run_tests.sh --coverage-html

# Generate an XML coverage report (for CI systems)
./tests/run_tests.sh --coverage-xml
```

When using HTML reports, the coverage output will be available in the `coverage/` directory. Open `coverage/index.html` in a web browser to view the detailed report.

## Writing Tests

When writing new tests, follow these guidelines:

1. **Test Organization**: Place unit tests in `tests/unit/` and integration tests in `tests/integration/`.
2. **Test Naming**: Name test files with the prefix `test_` followed by the module or component name.
3. **Pytest Markers**: Use pytest markers to categorize tests:
   ```python
   @pytest.mark.integration  # For integration tests
   def test_some_integration_feature():
       pass
   ```

4. **Mocking**: Use the `unittest.mock` module for mocking external dependencies.
5. **Test Coverage**: Aim for high test coverage, especially for core components.

## Plugin Testing

If you're developing plugins for the system, ensure you write tests for:

1. Registration and discovery of your plugin
2. Core functionality of your plugin
3. Integration with the main system

See `tests/unit/test_plugin_system.py` and `tests/unit/test_model_plugin.py` for examples of plugin testing.

## CI/CD Integration

The coverage reports can be integrated with CI/CD systems by using the XML output format:

```bash
./tests/run_tests.sh --coverage-xml
```

This will generate a `coverage.xml` file that can be consumed by services like Codecov, SonarQube, or GitHub Actions.

## Performance Testing

For performance-sensitive components, refer to the benchmarks in `tests/unit/test_benchmarks.py`. These tests measure the performance of key operations and can help identify regressions. 