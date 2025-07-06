# 🧪 Quizly Testing Guide

## Quick Start

### Run All Tests
```bash
# From project root - uses centralized test structure
./run_tests.sh
```

### Run Individual Test Suites

#### Backend Tests
```bash
# Unit tests
cd tests/backend/unit

# Individual test files
python test_database.py          # Database functionality
python test_logging_config.py    # Logging configuration
python test_llm_config.py        # LLM configuration
python test_config_manager.py    # Configuration manager

# Integration tests
cd tests/backend/integration
python test_api_endpoints.py     # API endpoints
python test_ai_integration_simple.py  # AI integration

# Run with pytest
cd tests/backend
python -m pytest unit/ -v        # All unit tests
python -m pytest integration/ -v # All integration tests
python -m pytest -v              # All backend tests
```

#### Frontend Tests
```bash
# Note: Frontend tests moved to centralized structure
# Jest configuration needs updating for new paths
cd frontend

# Current (temporary) - runs original test files
npm test                        # Interactive mode
npm test -- --watchAll=false   # One-time run
npm test -- --coverage         # With coverage report

# Future (after Jest config update)
# npm test -- --testPathPattern=../tests/frontend/
```

## Test Structure

### Centralized Test Organization

All tests are now organized in a centralized `/tests/` directory structure:

```
tests/
├── backend/
│   ├── unit/              # Backend unit tests
│   ├── integration/       # Backend integration tests
│   └── fixtures/          # Test fixtures and mock data
├── frontend/
│   ├── unit/components/   # Frontend component tests
│   └── integration/       # Frontend integration tests
├── e2e/                   # End-to-end tests
└── shared/                # Shared test utilities
```

### Backend Tests (`/tests/backend/`)
- **Unit Tests** (`unit/`):
  - `test_database.py` - Database functionality and schema
  - `test_logging_config.py` - Logging configuration and endpoints
  - `test_llm_config.py` - LLM provider configuration
  - `test_config_manager.py` - Configuration management
- **Integration Tests** (`integration/`):
  - `test_api_endpoints.py` - API endpoint functionality
  - `test_ai_integration.py` - AI service integration
  - `test_ai_integration_simple.py` - Simple AI integration tests
  - `test_openai.py` - OpenAI API integration
  - `test_logging_integration.py` - Logging integration
  - `test_full_workflow.py` - Complete backend workflows

### Frontend Tests (`/tests/frontend/`)
- **Unit Tests** (`unit/components/`):
  - `Question.test.js` - Question component testing
  - `Quiz.test.js` - Quiz component testing
  - `ScoreDisplay.test.js` - Score display component
  - `SubjectSelection.test.js` - Subject selection component
  - `AdminQuestions.test.js` - Admin questions management
  - `LoggingSettings.test.js` - Logging settings component
- **Integration Tests** (`integration/`):
  - `user_flows.test.js` - User journey integration tests
  - `api_integration.test.js` - Frontend API integration tests

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
# Run all backend tests
cd tests/backend
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest unit/test_database.py

# Run with coverage
pytest --cov=../../backend --cov-report=html

# Run specific pattern
pytest -k "test_database"

# Run only unit tests
pytest unit/

# Run only integration tests
pytest integration/
```

### Frontend Testing
```bash
# Run all tests
npm test

# Run specific test file
npm test Question.test.js

# Run with coverage
npm test -- --coverage --watchAll=false

# Run in CI mode
CI=true npm test
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
cd tests/backend
pytest --cov=../../backend --cov-report=html
open htmlcov/index.html
```

### Frontend Coverage
```bash
cd frontend
npm test -- --coverage --watchAll=false
open coverage/lcov-report/index.html
```

## Debugging Tests

### Backend Debug
```bash
# Run with debug output
cd tests/backend
pytest -v -s

# Run specific test with debug
pytest -v -s unit/test_database.py::test_database

# Run with pdb debugger
pytest --pdb unit/test_database.py
```

### Frontend Debug
```bash
# Run with debug output
npm test -- --verbose

# Debug specific test
npm test -- --testNamePattern="Question Component"

# Run with Node.js debugger
node --inspect-brk node_modules/.bin/react-scripts test --runInBand --no-cache
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
