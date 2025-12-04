# Tests

This folder contains test files for the excavator video analyzer project.

## Test Files

- **`test_cycle_analyzer.py`** - Tests for cycle time analysis functionality
- **`test_dual_averages.py`** - Tests for dual average feature
- **`test_html_quick.py`** - Quick tests for HTML report generation
- **`test_html_report.py`** - Comprehensive tests for HTML report system

## Running Tests

Run tests from the project root directory:

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_cycle_analyzer.py

# Or run individual test files directly
python tests/test_html_quick.py
```

## Test Coverage

The tests cover:
- Cycle time detection and analysis
- Performance metrics calculation
- HTML report generation
- Joystick analytics integration
- Multi-agent system coordination

## Adding New Tests

When adding new tests:
1. Create a new file with `test_` prefix
2. Import necessary modules from the project root
3. Follow existing test patterns
4. Document test purpose and expected behavior

