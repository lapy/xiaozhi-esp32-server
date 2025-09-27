# Testing Guide for Xiaozhi ESP32 Server

This document provides comprehensive testing guidelines for all the functionality added to the Xiaozhi ESP32 Server project.

## Overview

The testing suite covers:
- **Weather Plugin**: OpenWeatherMap API integration and caching
- **News Plugin**: RSS feed parsing and content fetching
- **SMS Service**: Twilio SMS integration
- **Frontend Components**: Vue.js components and internationalization
- **Configuration Management**: System parameters and plugin configuration

## Test Structure

```
main/xiaozhi-server/test/
├── test_weather_plugin.py      # Weather plugin unit tests
├── test_news_plugin.py         # News plugin unit tests
└── test_runner.py              # Python test runner

main/manager-api/src/test/java/xiaozhi/
├── AllTests.java                              # Test suite configuration
├── modules/sms/service/imp/
│   └── TwilioSmsServiceTest.java             # SMS service tests
└── modules/sys/service/impl/
    └── SysParamsServiceImplTest.java         # System parameters tests

main/manager-web/src/tests/
├── setup.js                   # Test environment setup
└── unit/
    └── plugins.test.js        # Frontend plugin tests

main/manager-web/
├── jest.config.js             # Jest configuration
└── package.json               # Test dependencies
```

## Running Tests

### Python Backend Tests

```bash
# Run all Python tests
cd main/xiaozhi-server
python test/test_runner.py

# Run specific test modules
python test/test_runner.py weather
python test/test_runner.py news

# Run individual test files
python -m unittest test.test_weather_plugin
python -m unittest test.test_news_plugin
```

### Java Backend Tests

```bash
# Run all Java tests
cd main/manager-api
mvn test

# Run specific test classes
mvn test -Dtest=TwilioSmsServiceTest
mvn test -Dtest=SysParamsServiceImplTest

# Run with coverage
mvn test jacoco:report
```

### Frontend Tests

```bash
# Install test dependencies
cd main/manager-web
npm install --save-dev @vue/test-utils vue-jest babel-jest jest

# Run all frontend tests
npm test

# Run with coverage
npm run test:coverage

# Run specific test files
npm test plugins.test.js
```

## Test Categories

### 1. Weather Plugin Tests

**File**: `test_weather_plugin.py`

**Coverage**:
- ✅ Weather condition mapping
- ✅ API data fetching (success/failure scenarios)
- ✅ Report formatting
- ✅ Caching functionality
- ✅ IP-based location detection
- ✅ Configuration validation
- ✅ Error handling

**Key Test Cases**:
```python
def test_get_weather_condition(self):
    """Test weather condition mapping."""
    
def test_fetch_weather_data_success(self):
    """Test successful weather data fetching."""
    
def test_get_weather_cache_hit(self):
    """Test weather plugin with cache hit."""
    
def test_get_weather_no_api_key(self):
    """Test weather plugin without API key."""
```

### 2. News Plugin Tests

**File**: `test_news_plugin.py`

**Coverage**:
- ✅ RSS feed parsing
- ✅ News source configuration
- ✅ Category mapping
- ✅ Content detail fetching
- ✅ Source rotation and fallback
- ✅ Caching functionality
- ✅ Error handling

**Key Test Cases**:
```python
def test_get_news_sources(self):
    """Test news sources configuration."""
    
def test_fetch_news_from_rss_success(self):
    """Test successful RSS news fetching."""
    
def test_get_news_detail_success(self):
    """Test news plugin detail mode."""
    
def test_get_news_source_rotation(self):
    """Test news plugin source rotation functionality."""
```

### 3. SMS Service Tests

**File**: `TwilioSmsServiceTest.java`

**Coverage**:
- ✅ SMS sending functionality
- ✅ Configuration validation
- ✅ Error handling
- ✅ Exception scenarios
- ✅ Parameter validation

**Key Test Cases**:
```java
@Test
void testSendVerificationCodeSms_Success() {
    // Test successful SMS sending
}

@Test
void testSendVerificationCodeSms_MissingAccountSid() {
    // Test missing configuration
}

@Test
void testSendVerificationCodeSms_TwilioException() {
    // Test exception handling
}
```

### 4. System Parameters Tests

**File**: `SysParamsServiceImplTest.java`

**Coverage**:
- ✅ SMS parameter detection
- ✅ Configuration validation
- ✅ Parameter completeness checking
- ✅ Error scenarios

**Key Test Cases**:
```java
@Test
void testDetectingSMSParameters_AllTwilioParametersPresent() {
    // Test complete configuration
}

@Test
void testDetectingSMSParameters_MissingAccountSid() {
    // Test missing parameters
}
```

### 5. Frontend Plugin Tests

**File**: `plugins.test.js`

**Coverage**:
- ✅ Plugin integration
- ✅ Configuration handling
- ✅ Error scenarios
- ✅ Language/locale functionality
- ✅ Component behavior

**Key Test Cases**:
```javascript
describe('Weather Plugin Tests', () => {
  test('should handle weather plugin configuration correctly')
  test('should handle weather plugin API key validation')
  test('should handle weather plugin location fallback')
})

describe('News Plugin Tests', () => {
  test('should handle news plugin basic functionality')
  test('should handle news plugin category mapping')
  test('should handle news plugin detail mode')
})
```

## Test Data and Mocking

### Mock Data

**Weather API Response**:
```python
current_data = {
    "name": "New York",
    "sys": {"country": "US"},
    "main": {
        "temp": 20,
        "feels_like": 18,
        "humidity": 65,
        "pressure": 1013
    },
    "weather": [{"description": "clear sky"}],
    "wind": {"speed": 3.5, "deg": 180}
}
```

**News RSS Response**:
```python
news_items = [
    {
        "title": "Breaking News Title",
        "link": "https://example.com/news1",
        "description": "This is breaking news content",
        "pubDate": "Mon, 01 Jan 2024 12:00:00 GMT"
    }
]
```

### Mocking Strategies

**Python**:
- `unittest.mock.patch` for API calls
- `unittest.mock.Mock` for connection objects
- `unittest.mock.MagicMock` for complex objects

**Java**:
- `@Mock` annotations with Mockito
- `MockedStatic` for static method mocking
- `when().thenReturn()` for behavior stubbing

**JavaScript**:
- `jest.fn()` for function mocking
- `jest.mock()` for module mocking
- `@vue/test-utils` for component testing

## Coverage Requirements

### Backend (Python/Java)
- **Minimum Coverage**: 80%
- **Critical Paths**: 95%
- **Error Handling**: 90%

### Frontend (JavaScript/Vue)
- **Minimum Coverage**: 70%
- **Component Logic**: 80%
- **User Interactions**: 75%

## Continuous Integration

### GitHub Actions Configuration

```yaml
name: Tests
on: [push, pull_request]
jobs:
  python-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run Python tests
        run: python test/test_runner.py

  java-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up JDK
        uses: actions/setup-java@v2
        with:
          java-version: '11'
      - name: Run Java tests
        run: mvn test

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '16'
      - name: Install dependencies
        run: npm install
      - name: Run frontend tests
        run: npm test
```

## Test Maintenance

### Adding New Tests

1. **Identify Test Category**: Determine if it's unit, integration, or e2e
2. **Create Test File**: Follow naming convention `test_*.py` or `*Test.java`
3. **Write Test Cases**: Cover happy path, edge cases, and error scenarios
4. **Update Documentation**: Add test descriptions to this guide
5. **Run Tests**: Ensure all tests pass before committing

### Test Best Practices

**Python**:
- Use descriptive test method names
- Follow AAA pattern (Arrange, Act, Assert)
- Mock external dependencies
- Test both success and failure scenarios

**Java**:
- Use `@ExtendWith(MockitoExtension.class)` for Mockito
- Test exception scenarios with `assertThrows`
- Verify mock interactions with `verify()`
- Use `@BeforeEach` for test setup

**JavaScript**:
- Use `describe` blocks for grouping related tests
- Mock API calls and external dependencies
- Test component props and events
- Use async/await for asynchronous operations

## Troubleshooting

### Common Issues

**Python Tests**:
- Import errors: Check PYTHONPATH and module structure
- Mock failures: Verify mock setup and call expectations
- API errors: Ensure proper mocking of external calls

**Java Tests**:
- Mockito errors: Check annotation usage and static mocking
- Compilation errors: Verify test dependencies in pom.xml
- Assertion failures: Review expected vs actual values

**Frontend Tests**:
- Component mounting errors: Check Vue plugin setup
- Mock failures: Verify Jest mock configuration
- Async test failures: Ensure proper async/await usage

### Debug Commands

```bash
# Python debug
python -m pdb test/test_runner.py

# Java debug
mvn test -Dmaven.surefire.debug

# Frontend debug
npm test -- --verbose --no-cache
```

## Performance Testing

### Load Testing

For the news and weather plugins, consider:
- API rate limiting
- Cache performance
- Memory usage
- Response times

### Stress Testing

Test scenarios:
- High concurrent requests
- Large RSS feed parsing
- Multiple weather API calls
- Cache eviction scenarios

## Security Testing

### API Security

- API key validation
- Input sanitization
- Rate limiting
- Error message sanitization

### Data Security

- Sensitive data handling
- Cache security
- Configuration security
- User input validation

## Conclusion

This comprehensive testing suite ensures the reliability and maintainability of all added functionality. Regular test execution and maintenance are crucial for maintaining code quality and preventing regressions.

For questions or issues with the testing suite, please refer to the individual test files or contact the development team.
