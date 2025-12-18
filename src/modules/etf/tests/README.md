# ETF Module Unit Tests

This directory contains structured unit tests for the ETF analysis API.

## Test Structure

- `conftest.py` - Shared fixtures and test configuration
- `test_router.py` - API endpoint tests (router layer)
- `test_service.py` - Service layer business logic tests

## Running Tests

### Recommended: Run Tests Independently (Outside Docker)

**Why?** Unit tests mock all dependencies and don't need external services. This is faster and better for development.

#### Option 1: Using pytest directly
```bash
# Install dependencies first
pip install -r requirements.txt

# Run all tests
pytest src/modules/etf/tests -v

# Run specific test file
pytest src/modules/etf/tests/test_router.py -v
pytest src/modules/etf/tests/test_service.py -v

# Run specific test
pytest src/modules/etf/tests/test_router.py::TestAnalyzeEndpoint::test_analyze_success -v

# Run with coverage
pytest src/modules/etf/tests --cov=src/modules/etf --cov-report=html
```

#### Option 2: Using the test script
```bash
python run_tests.py
```

### Alternative: Run Tests in Docker

Use this if you want to test in a containerized environment (e.g., CI/CD, integration tests).

```bash
# Run tests in Docker
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Or build and run manually
docker build -t etf-service .
docker run --rm etf-service python -m pytest src/modules/etf/tests -v
```

## Test Coverage

### Router Tests (`test_router.py`)
- ✅ Successful portfolio analysis
- ✅ Invalid CSV columns
- ✅ Invalid CSV format
- ✅ Empty CSV file
- ✅ No price data available
- ✅ No matching ticker data
- ✅ Missing file parameter

### Service Tests (`test_service.py`)
- ✅ Successful portfolio analysis
- ✅ Invalid CSV columns handling
- ✅ Empty CSV handling
- ✅ No price data exception
- ✅ No matching tickers exception
- ✅ Partial ticker matching
- ✅ Case-insensitive ticker matching
- ✅ NAV calculation correctness
- ✅ Filename extraction
- ✅ Default ETF name when no filename

## Dependencies

Tests require:
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `httpx` - HTTP client for testing (via FastAPI TestClient)

Install with:
```bash
pip install -r requirements.txt
```
