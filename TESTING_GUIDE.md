# 🧪 Quizly Testing Guide

## Quick Start

### Run All Tests
```bash
# From project root
./run_tests.sh
```

### Run Individual Test Suites

The `./run_tests.sh` script is the recommended way to run specific suites:
```bash
# From project root
./run_tests.sh backend          # Run all backend tests
./run_tests.sh backend unit     # Run backend unit tests
./run_tests.sh backend integration # Run backend integration tests
./run_tests.sh frontend         # Run all frontend tests
```

For more granular control or debugging:

#### Backend Tests (using pytest directly from project root)
```bash
# Run all backend tests
python -m pytest tests/backend/

# Run backend unit tests
python -m pytest tests/backend/unit/

# Run a specific backend test file
python -m pytest tests/backend/unit/test_config_manager.py

# Run tests with verbose output
python -m pytest -v tests/backend/
```

#### Frontend Tests
```bash
cd frontend

# Run React tests (interactive mode)
npm test

# Run React tests once
npm test -- --watchAll=false

# Run React tests with coverage
npm test -- --coverage --watchAll=false
```

## Test Structure

Tests are organized in a centralized `tests/` directory at the project root for backend tests, and within `frontend/src/tests/` for frontend tests.

### Backend Tests (`tests/backend/`)
- **`tests/backend/unit/`**: Unit tests for individual modules and functions.
    - `test_config_manager.py`: Tests for `backend/config_manager.py`.
    - `test_logging_config.py`: Tests for `backend/logging_config.py`.
    - `test_database.py` (if created, currently in `test_backend.py`): Tests for `backend/database.py`.
    - `test_backend.py`: General backend unit tests.
    - `test_logging.py`: Basic logging output tests.
    - `manual_test_openai.py`: Manual script for testing OpenAI connection (not run by default).
- **`tests/backend/integration/`**: Integration tests for component interactions and API endpoints.
    - `test_api_endpoints.py`: Tests for FastAPI endpoints.
    - `test_ai_integration.py`: Tests for AI provider integration and question generation.
    - `test_ai_integration_simple.py`: Simpler AI integration component checks.
- **`tests/backend/fixtures/`**: (Planned for shared fixtures, e.g., `mock_data.py`, `test_config.py`) - Currently empty.

### Frontend Tests (`frontend/src/tests/`)
- **`frontend/src/tests/unit/components/`**: Unit tests for React components.
    - `Question.test.js`
    - `ScoreDisplay.test.js`
    - `SubjectSelection.test.js`
    - `AdminQuestions.test.js`
    - `LoggingSettings.test.js`
    - `__snapshots__/`: Jest snapshot files.
- **`frontend/src/tests/unit/utils/`**: (Planned for utility function tests) - Currently empty.
- **`frontend/src/tests/integration/`**: (Planned for frontend integration tests, e.g., `user_flows.test.js`) - Currently empty.

### Shared Tests (`tests/shared/`)
- (Planned for shared helpers across backend/frontend, e.g., `test_helpers.py`, `test_helpers.js`) - Currently empty.

## Testing Dependencies

### Backend
```bash
# Install testing dependencies
pip install -r requirements-dev.txt

# Or install individually
pip install pytest pytest-asyncio httpx pytest-cov
```

### Frontend
```bash
# Dependencies are already in package.json
npm install
```

## Test Commands Reference

### Backend Testing
```bash
# From project root:

# Run all backend tests
python -m pytest tests/backend/

# Run with verbose output
python -m pytest -v tests/backend/

# Run specific test file (e.g., unit test for config_manager)
python -m pytest tests/backend/unit/test_config_manager.py

# Run tests in a specific directory (e.g., all integration tests)
python -m pytest tests/backend/integration/

# Run with coverage report (HTML report will be in htmlcov/)
python -m pytest tests/backend/ --cov=backend --cov-report=html

# Run tests matching a specific keyword expression
python -m pytest -k "database" tests/backend/
```

### Frontend Testing
```bash
# From frontend/ directory:

# Run all tests (interactive mode)
npm test

# Run all tests once
npm test -- --watchAll=false

# Run specific test file (Jest will try to match the filename)
npm test Question.test.js --watchAll=false

# Run with coverage report
npm test -- --coverage --watchAll=false

# Run in CI mode (often implies --watchAll=false and specific reporters)
# The ./run_tests.sh script handles CI flags for frontend tests.
# Equivalent direct command from frontend/ for CI-like run:
CI=true npm test -- --coverage --watchAll=false
```

## Test Results

### Expected Outputs
- ✅ **Backend Tests**: Database, API endpoints, logging, LLM configuration
- ✅ **Frontend Tests**: React components, user interactions, rendering
- ✅ **Integration Tests**: AI question generation, API communication

### Common Issues
1. **Port conflicts**: Stop running servers before tests
2. **Missing dependencies**: Install requirements-dev.txt
3. **API key issues**: Configure OpenAI API key for AI tests
4. **Database issues**: Tests use temporary databases

## Continuous Integration

The `run_tests.sh` script is designed to be CI-friendly:
- Returns proper exit codes
- Provides colored output
- Handles timeouts for long-running tests
- Generates test summaries

## Coverage Reports

The `./run_tests.sh` script generates coverage reports:
- Backend: `coverage.xml` and terminal summary. `pytest tests/backend/ --cov=backend --cov-report=html` (from root) generates an HTML report in `htmlcov/`.
- Frontend: `frontend/coverage/` (includes LCOV and HTML).

### Backend Coverage (HTML Report)
```bash
# From project root
python -m pytest tests/backend/ --cov=backend --cov-report=html
# Then open htmlcov/index.html in your browser
```

### Frontend Coverage (HTML Report)
```bash
# From project root, run:
./run_tests.sh frontend
# Or from frontend/ directory:
# npm test -- --coverage --watchAll=false
# Then open frontend/coverage/lcov-report/index.html in your browser
```

## Debugging Tests

### Backend Debug
```bash
# Run with debug output
pytest -v -s

# Run specific test with debug
pytest -v -s test_backend.py::test_database
```

### Frontend Debug
```bash
# Run with debug output
npm test -- --verbose

# Debug specific test
npm test -- --testNamePattern="Question Component"
```

## Writing New Tests

### Backend Test Template
```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_my_endpoint():
    response = client.get("/api/my-endpoint")
    assert response.status_code == 200
    assert response.json() == {"expected": "result"}
```

### Frontend Test Template
```javascript
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import MyComponent from '../MyComponent';

test('renders component correctly', () => {
  render(<MyComponent />);
  expect(screen.getByText('Expected Text')).toBeInTheDocument();
});
```

## Performance Testing

For performance testing, consider adding:
- `locust` for load testing
- `pytest-benchmark` for performance benchmarks
- `lighthouse` for frontend performance

Happy Testing! 🎉
