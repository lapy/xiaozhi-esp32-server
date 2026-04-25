# Xiaozhi Server Tests

This directory contains comprehensive tests for the Xiaozhi ESP32 Server functionality.

## Test Files

- `test_weather_plugin.py` - Tests for the weather plugin functionality
- `test_news_plugin.py` - Tests for the news plugin functionality  
- `test_runner.py` - Test runner script for executing all tests

## Running Tests

### Run All Tests
```bash
python test_runner.py
```

### Run Specific Test Modules
```bash
# Weather plugin tests only
python test_runner.py weather

# News plugin tests only
python test_runner.py news
```

### Run Individual Test Files
```bash
python -m unittest test_weather_plugin
python -m unittest test_news_plugin
```

### Run with Verbose Output
```bash
python -m unittest -v test_weather_plugin
```

## Test Coverage

The tests cover:

### Weather Plugin
- ✅ Weather condition mapping
- ✅ API data fetching (success/failure scenarios)
- ✅ Report formatting
- ✅ Caching functionality
- ✅ IP-based location detection
- ✅ Configuration validation
- ✅ Error handling

### News Plugin
- ✅ RSS feed parsing
- ✅ News source configuration
- ✅ Category mapping
- ✅ Content detail fetching
- ✅ Source rotation and fallback
- ✅ Caching functionality
- ✅ Error handling

## Dependencies

The tests require the following Python packages:
- `unittest` (built-in)
- `unittest.mock` (built-in)
- `requests` (for API mocking)
- `beautifulsoup4` (for HTML parsing)

## Mocking

Tests use `unittest.mock` to mock external dependencies:
- API calls (OpenWeatherMap, RSS feeds)
- Cache operations
- Network requests
- Configuration objects

## Test Data

Mock data is provided for:
- Weather API responses
- RSS feed XML content
- News article HTML
- Configuration objects
- Error scenarios

## Continuous Integration

These tests are designed to run in CI/CD environments and can be executed with:
```bash
# From project root
./run_tests.sh --python-only  # Linux/Mac
run_tests.bat --python-only   # Windows
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running from the project root directory
2. **Mock Failures**: Check that mocked methods are called with expected parameters
3. **API Errors**: Verify that external API calls are properly mocked

### Debug Mode

Run tests with debug output:
```bash
python -m pdb test_runner.py
```

## Contributing

When adding new functionality:

1. Create corresponding test files following the naming convention `test_*.py`
2. Add test cases for both success and failure scenarios
3. Update this README with new test descriptions
4. Ensure all tests pass before submitting changes

## Documentation

For detailed testing documentation, see: `docs/testing-guide.md`
