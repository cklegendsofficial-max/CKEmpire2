# CK Empire Comprehensive Test Suite Guide

## Overview

The CK Empire project includes a comprehensive test suite designed to ensure code quality, security, and performance. This guide covers all aspects of the testing infrastructure.

## Test Suite Components

### 1. Unit Tests
- **Purpose**: Test individual functions and classes in isolation
- **Framework**: Pytest with coverage reporting
- **Coverage Target**: 90%+ code coverage
- **Location**: `backend/tests/`
- **Markers**: `@pytest.mark.unit`

### 2. Integration Tests
- **Purpose**: Test interactions between components
- **Framework**: Pytest with database fixtures
- **Location**: `backend/tests/`
- **Markers**: `@pytest.mark.integration`

### 3. API Tests
- **Purpose**: Test REST API endpoints
- **Framework**: Pytest with FastAPI TestClient
- **Location**: `backend/tests/test_api_comprehensive.py`
- **Markers**: `@pytest.mark.api`

### 4. End-to-End (E2E) Tests
- **Purpose**: Test complete user workflows
- **Framework**: Selenium WebDriver
- **Location**: `backend/tests/test_e2e_selenium.py`
- **Markers**: `@pytest.mark.e2e`

### 5. Load Tests
- **Purpose**: Test system performance under load
- **Framework**: Locust
- **Location**: `backend/tests/load/locustfile.py`
- **Markers**: `@pytest.mark.load`

### 6. Security Tests
- **Purpose**: Identify security vulnerabilities
- **Tools**: Bandit, Safety, Semgrep
- **Location**: Configuration files in `backend/`

### 7. Performance Tests
- **Purpose**: Measure and optimize performance
- **Framework**: Pytest-benchmark
- **Location**: `backend/tests/`
- **Markers**: `@pytest.mark.performance`

## Quick Start

### Prerequisites

1. **Install Dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

2. **Setup Test Database**:
```bash
# The test runner will automatically create test databases
```

3. **Install Additional Tools** (Optional):
```bash
# For E2E tests
pip install webdriver-manager

# For security tests
pip install bandit safety semgrep

# For load tests
pip install locust
```

### Running Tests

#### Run All Tests
```bash
cd backend
python run_tests.py --all
```

#### Run Specific Test Types
```bash
# Unit tests only
python run_tests.py --unit

# Integration tests only
python run_tests.py --integration

# E2E tests only
python run_tests.py --e2e

# Load tests only
python run_tests.py --load

# Security tests only
python run_tests.py --security

# Performance tests only
python run_tests.py --performance
```

#### Run with Coverage
```bash
python run_tests.py --unit --coverage
```

#### Clean and Run
```bash
python run_tests.py --clean --all
```

## Test Configuration

### Pytest Configuration (`pytest.ini`)

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --cov=.
    --cov-report=html
    --cov-report=xml
    --cov-report=term-missing
    --cov-fail-under=90
    --html=reports/pytest-report.html
    --json-report=reports/pytest-report.json
    --timeout=30
    --randomly-seed=42
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    security: Security tests
    performance: Performance tests
    load: Load tests
    api: API tests
    database: Database tests
    encryption: Encryption tests
    ai: AI service tests
    ethics: Ethics service tests
    cloud: Cloud service tests
    monitoring: Monitoring tests
```

### Test Fixtures (`conftest.py`)

The test suite includes comprehensive fixtures for:
- Database sessions
- API clients
- Authentication
- Mock services
- Sample data
- Performance testing
- Security testing

## Test Structure

### Database Tests
```python
@pytest.mark.database
@pytest.mark.unit
class TestDatabaseModels:
    def test_project_creation(self, db_session, sample_project_data):
        # Test project creation
        pass
```

### API Tests
```python
@pytest.mark.api
@pytest.mark.unit
class TestProjectEndpoints:
    def test_create_project_success(self, client, auth_headers, sample_project_data):
        # Test API endpoint
        pass
```

### E2E Tests
```python
@pytest.mark.e2e
@pytest.mark.selenium
class TestDashboardE2E:
    def test_dashboard_loads_successfully(self, driver, wait):
        # Test complete user workflow
        pass
```

## Load Testing

### Locust Configuration

The load testing suite includes:
- Multiple user types (regular, admin, read-only)
- Realistic API workflows
- Performance metrics collection
- Custom event handlers

### Running Load Tests

```bash
# Basic load test
locust -f tests/load/locustfile.py --host=http://localhost:8000

# Headless load test
locust -f tests/load/locustfile.py --host=http://localhost:8000 --headless --users 10 --spawn-rate 2 --run-time 60s
```

## Security Testing

### Bandit Configuration

Bandit scans for common security issues:
- SQL injection
- Command injection
- Hardcoded passwords
- Insecure cryptographic functions
- And many more...

### Safety Configuration

Safety checks for known vulnerabilities in dependencies:
- CVE database integration
- Dependency vulnerability scanning
- Severity-based reporting

### Running Security Tests

```bash
# Run Bandit
bandit -r . -f json -o reports/bandit-report.json

# Run Safety
safety check --json --output reports/safety-report.json

# Run Semgrep
semgrep --config=auto --json --output=reports/semgrep-report.json .
```

## Performance Testing

### Benchmark Configuration

Performance tests use pytest-benchmark for:
- Function execution time measurement
- Memory usage tracking
- Statistical analysis
- Performance regression detection

### Running Performance Tests

```bash
# Run performance tests
pytest -m performance --benchmark-only

# Compare with previous runs
pytest -m performance --benchmark-compare
```

## Test Reports

### Generated Reports

The test suite generates comprehensive reports:

1. **HTML Reports**:
   - `reports/unit-tests-report.html`
   - `reports/integration-tests-report.html`
   - `reports/e2e-tests-report.html`
   - `reports/load-test-report.html`
   - `reports/performance-tests-report.html`

2. **Coverage Reports**:
   - `reports/coverage-html/index.html`
   - `reports/coverage.xml`

3. **Security Reports**:
   - `reports/bandit-report.json`
   - `reports/safety-report.json`
   - `reports/semgrep-report.json`

4. **Summary Report**:
   - `reports/test-summary.json`

### Interpreting Results

#### Coverage Report
- **Target**: 90%+ code coverage
- **HTML Report**: Interactive coverage visualization
- **XML Report**: CI/CD integration

#### Security Report
- **Bandit**: Code security vulnerabilities
- **Safety**: Dependency vulnerabilities
- **Semgrep**: Advanced security patterns

#### Performance Report
- **Benchmark Results**: Execution time statistics
- **Regression Detection**: Performance changes over time
- **Memory Usage**: Memory consumption analysis

## Continuous Integration

### GitHub Actions

The test suite is integrated with GitHub Actions:

```yaml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          python run_tests.py --all
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

### Local Development

For local development:

1. **Pre-commit Hooks**:
```bash
pre-commit install
```

2. **Quick Test**:
```bash
python run_tests.py --unit
```

3. **Full Test Suite**:
```bash
python run_tests.py --all
```

## Best Practices

### Writing Tests

1. **Test Naming**: Use descriptive test names
2. **Test Isolation**: Each test should be independent
3. **Mocking**: Mock external dependencies
4. **Data Setup**: Use fixtures for test data
5. **Cleanup**: Clean up after tests

### Test Organization

1. **Group Related Tests**: Use test classes
2. **Use Markers**: Mark tests appropriately
3. **Separate Concerns**: Unit, integration, and E2E tests
4. **Maintain Fixtures**: Keep fixtures reusable

### Performance Considerations

1. **Test Speed**: Keep tests fast
2. **Parallel Execution**: Use pytest-xdist
3. **Resource Management**: Clean up resources
4. **Database Isolation**: Use separate test databases

## Troubleshooting

### Common Issues

1. **Database Connection**:
   - Ensure test database is created
   - Check database permissions

2. **E2E Test Failures**:
   - Verify frontend is running
   - Check WebDriver installation
   - Ensure browser compatibility

3. **Load Test Failures**:
   - Verify backend is running
   - Check network connectivity
   - Monitor system resources

4. **Security Test Failures**:
   - Review false positives
   - Update security rules
   - Check dependency versions

### Debugging

1. **Verbose Output**:
```bash
pytest -v -s
```

2. **Debug Specific Test**:
```bash
pytest tests/test_specific.py::TestClass::test_method -v -s
```

3. **Coverage Debug**:
```bash
coverage report --show-missing
```

## Maintenance

### Regular Tasks

1. **Update Dependencies**: Keep testing tools updated
2. **Review Security Reports**: Address security findings
3. **Monitor Performance**: Track performance regressions
4. **Update Test Data**: Keep test data current

### Adding New Tests

1. **Follow Naming Convention**: `test_*.py`
2. **Use Appropriate Markers**: Mark test types
3. **Add to Test Runner**: Update `run_tests.py`
4. **Update Documentation**: Document new tests

### Test Data Management

1. **Use Fixtures**: Create reusable test data
2. **Clean Up**: Ensure test data cleanup
3. **Version Control**: Track test data changes
4. **Backup**: Backup important test data

## Advanced Features

### Custom Test Markers

```python
@pytest.mark.slow
def test_slow_operation():
    # This test will be skipped in fast runs
    pass
```

### Parameterized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("test1", "result1"),
    ("test2", "result2"),
])
def test_parameterized(input, expected):
    assert function(input) == expected
```

### Custom Fixtures

```python
@pytest.fixture(scope="session")
def expensive_fixture():
    # Setup expensive resource
    yield resource
    # Cleanup
```

### Test Hooks

```python
def pytest_runtest_setup(item):
    # Setup before each test
    pass

def pytest_runtest_teardown(item):
    # Cleanup after each test
    pass
```

## Conclusion

The CK Empire test suite provides comprehensive testing coverage for all aspects of the application. Regular execution of the test suite ensures code quality, security, and performance while providing detailed reports for analysis and improvement.

For questions or issues with the test suite, please refer to the project documentation or create an issue in the project repository. 