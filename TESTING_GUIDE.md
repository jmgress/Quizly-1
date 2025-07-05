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
cd backend

# Individual test files
python test_backend.py          # Basic functionality
python test_logging_config.py   # Logging configuration
python test_llm_config.py       # LLM configuration
python test_openai.py          # OpenAI integration
python test_ai_integration.py   # AI integration

# Run with pytest
python -m pytest -v
```

#### Frontend Tests
```bash
cd frontend

# Run React tests
npm test                        # Interactive mode
npm test -- --watchAll=false   # One-time run
npm test -- --coverage         # With coverage report
```

## Test Structure

### Backend Tests (`/backend/`)
- `test_backend.py` - Basic database and API functionality
- `test_logging_config.py` - Logging configuration and endpoints
- `test_llm_config.py` - LLM provider configuration
- `test_openai.py` - OpenAI API integration
- `test_ai_integration.py` - AI question generation

### Frontend Tests (`/frontend/src/components/__tests__/`)
- `Question.test.js` - Question component testing
- `ScoreDisplay.test.js` - Score display component
- `SubjectSelection.test.js` - Subject selection component
- `AdminQuestions.test.js` - Admin questions management
- `LoggingSettings.test.js` - Logging settings component

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
pytest test_backend.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run with specific pattern
pytest -k "test_database"
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
cd backend
pytest --cov=. --cov-report=html
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
