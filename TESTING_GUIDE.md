# 🧪 Quizly Testing Guide

## Quick Start

### Run All Tests
```bash
# From project root
./run_tests.sh
```

### Run Individual Test Suites

#### Backend Tests
```bash
./run_tests.sh backend unit       # Run backend unit tests
./run_tests.sh backend integration # Run backend integration tests
```

#### Frontend Tests
```bash
./run_tests.sh frontend unit          # React unit tests
./run_tests.sh frontend integration   # React integration tests
```

## Test Structure

### Backend Tests (`/tests/backend`)
- `unit/` - Core backend units
- `integration/` - API and AI integration tests

### Frontend Tests (`/tests/frontend`)
- `unit/components/*.test.js` - React component tests
- `integration/*.test.js` - Frontend integration tests

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
# Run all pytest tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/backend/unit/test_database.py

# Run with coverage
pytest --cov=backend --cov-report=html

# Run with specific pattern
pytest -k "test_database"
```

### Frontend Testing
```bash
# Run all tests
./run_tests.sh frontend

# Run specific test file
CI=true npm test -- --config=jest.config.js tests/frontend/unit/components/Question.test.js

# Run with coverage
./run_tests.sh frontend unit
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

### Backend Coverage
```bash
cd backend
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

### Frontend Coverage
```bash
./run_tests.sh frontend unit
open frontend/coverage/lcov-report/index.html
```

## Debugging Tests

### Backend Debug
```bash
# Run with debug output
pytest -v -s

# Run specific test with debug
pytest -v -s tests/backend/unit/test_database.py::test_database
```

### Frontend Debug
```bash
# Run with debug output
CI=true npm test -- --config=jest.config.js --verbose

# Debug specific test
CI=true npm test -- --config=jest.config.js --testNamePattern="Question Component"
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
