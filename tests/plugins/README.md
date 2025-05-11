# Plugin System Test Scripts

These standalone test scripts measure code coverage for the Pulp Fiction Generator plugin system components. They're designed to be run independently of the main test framework to avoid dependency issues that can occur in the main test suite.

## Available Test Scripts

- **plugin_coverage.py**: Tests the core plugin registry and plugin base classes
- **plugin_hooks_coverage.py**: Tests the plugin hook system for event handling
- **plugin_manager_coverage.py**: Tests plugin discovery and management functionality

## Running the Tests

You can run the tests individually:

```bash
python tests/plugins/plugin_coverage.py
python tests/plugins/plugin_hooks_coverage.py
python tests/plugins/plugin_manager_coverage.py
```

Or run them together with coverage measurement:

```bash
python -m coverage run -a tests/plugins/plugin_coverage.py && \
python -m coverage run -a tests/plugins/plugin_hooks_coverage.py && \
python -m coverage run -a tests/plugins/plugin_manager_coverage.py && \
python -m coverage report -m --include="*/pulp_fiction_generator/plugins/*"
```

## Test Coverage

The combined tests provide approximately 96% coverage of the plugin system code. The tests verify:

1. **Plugin Registry**: Registration, retrieval, and error handling of plugins
2. **Plugin Base Classes**: Functionality of the base plugin classes and metaclasses
3. **Plugin Hooks**: Registration and execution of plugin hooks
4. **Plugin Manager**: Discovery of plugins from multiple sources

## Implementation Details

These tests use mock plugin implementations to test the system without requiring actual plugins. The mock plugins simulate both normal operation and error conditions to ensure robust error handling.

## Integration with Main Test Suite

While these scripts can be run standalone, they complement the unit tests in `tests/unit/test_plugin_system.py` and `tests/unit/test_model_plugin.py`. The main difference is that these scripts focus more on coverage, while the unit tests focus on correctness and edge cases. 