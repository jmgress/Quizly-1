# 🧪 Quizly Centralized Test Organization

This directory contains all tests for the Quizly application, organized in a centralized structure for better maintainability and clarity.

## Directory Structure

```
tests/
├── backend/
│   ├── unit/                   # Unit tests for backend components
│   │   ├── test_database.py    # Database functionality tests
│   │   ├── test_logging_config.py  # Logging configuration tests
│   │   ├── test_llm_config.py  # LLM configuration tests
│   │   └── test_config_manager.py  # Configuration manager tests
│   ├── integration/            # Integration tests for backend
│   │   ├── test_ai_integration.py  # AI service integration tests
│   │   ├── test_ai_integration_simple.py  # Simple AI integration tests
│   │   ├── test_api_endpoints.py  # API endpoint tests
│   │   ├── test_logging_integration.py  # Logging integration tests
│   │   ├── test_openai.py      # OpenAI integration tests
│   │   └── test_full_workflow.py  # Complete backend workflow tests
│   └── fixtures/               # Test fixtures and mock data
│       ├── mock_data.py        # Mock data for testing
│       └── test_config.py      # Test configuration helpers
├── frontend/
│   ├── unit/                   # Unit tests for frontend components
│   │   ├── components/         # React component tests
│   │   │   ├── Question.test.js
│   │   │   ├── Quiz.test.js
│   │   │   ├── ScoreDisplay.test.js
│   │   │   ├── SubjectSelection.test.js
│   │   │   ├── AdminQuestions.test.js
│   │   │   └── LoggingSettings.test.js
│   │   └── utils/              # Utility function tests (future)
│   └── integration/            # Integration tests for frontend
│       ├── user_flows.test.js  # User flow integration tests
│       └── api_integration.test.js  # API integration tests
├── e2e/                        # End-to-end tests
│   ├── quiz_flow.test.js       # Quiz flow e2e tests
│   └── admin_flow.test.js      # Admin flow e2e tests
└── shared/                     # Shared test utilities
    ├── test_helpers.py         # Python test helpers
    ├── test_helpers.js         # JavaScript test helpers
    └── mock_server.py          # Mock server for testing
```

## Test Categories

### Backend Tests

#### Unit Tests (`backend/unit/`)
- **test_database.py**: Tests database operations, schema, and data integrity
- **test_logging_config.py**: Tests logging configuration and functionality
- **test_llm_config.py**: Tests LLM provider configuration
- **test_config_manager.py**: Tests configuration management functionality

#### Integration Tests (`backend/integration/`)
- **test_ai_integration.py**: Tests AI service integration (OpenAI, Ollama)
- **test_api_endpoints.py**: Tests API endpoint functionality
- **test_full_workflow.py**: Tests complete backend workflows
- **test_openai.py**: Tests OpenAI-specific integration

#### Fixtures (`backend/fixtures/`)
- **mock_data.py**: Sample questions, configurations, and test data
- **test_config.py**: Test configuration utilities and helpers

### Frontend Tests

#### Unit Tests (`frontend/unit/`)
- **components/**: React component unit tests
  - Component rendering
  - User interactions
  - Props handling
  - State management
- **utils/**: Utility function tests (future expansion)

#### Integration Tests (`frontend/integration/`)
- **user_flows.test.js**: User journey integration tests
- **api_integration.test.js**: Frontend-to-backend API integration tests

### End-to-End Tests (`e2e/`)
- **quiz_flow.test.js**: Complete quiz-taking workflows
- **admin_flow.test.js**: Admin functionality workflows

### Shared Utilities (`shared/`)
- **test_helpers.py**: Python test utilities and helpers
- **test_helpers.js**: JavaScript test utilities and helpers
- **mock_server.py**: Mock server for testing API interactions

## Running Tests

### Backend Tests

```bash
# Run all backend tests
cd tests/backend
python -m pytest

# Run specific test categories
python -m pytest unit/
python -m pytest integration/

# Run specific test files
python unit/test_database.py
python integration/test_ai_integration_simple.py
```

### Frontend Tests

```bash
# Run all frontend tests
cd tests/frontend
npm test

# Run specific test files
npm test -- Question.test.js
npm test -- --testPathPattern=unit/components/
```

### All Tests

```bash
# Run complete test suite from project root
./run_tests.sh
```

## Test Configuration

### Backend Test Configuration
- Tests use in-memory SQLite databases for isolation
- Mock external services (OpenAI, Ollama) for reliable testing
- Temporary files and directories are cleaned up after tests

### Frontend Test Configuration
- Uses Jest and React Testing Library
- Components are tested in isolation with mocked dependencies
- Snapshot testing for UI regression detection

### E2E Test Configuration
- Placeholder structure for future Playwright/Cypress implementation
- Tests would run against full application stack
- Includes accessibility and performance testing scenarios

## Adding New Tests

### Backend Tests
1. Create test file in appropriate category (`unit/` or `integration/`)
2. Add necessary imports with proper path resolution
3. Use fixtures from `fixtures/` directory for consistent test data
4. Follow existing patterns for database setup and teardown

### Frontend Tests
1. Create test file in appropriate directory under `frontend/`
2. Import components with full relative paths
3. Use shared test helpers from `shared/test_helpers.js`
4. Follow React Testing Library best practices

### E2E Tests
1. Add test scenarios to existing e2e files
2. Follow placeholder structure for future implementation
3. Include both happy path and error scenarios

## Test Data and Fixtures

### Mock Data
- Consistent sample questions across all tests
- Standardized configuration objects
- Predictable API responses for testing

### Test Helpers
- Database setup and teardown utilities
- API mocking and response creation
- Configuration file management
- Assertion helpers for common patterns

## Best Practices

1. **Test Isolation**: Each test should be independent and not rely on other tests
2. **Clear Naming**: Test names should clearly describe what is being tested
3. **Arrange-Act-Assert**: Structure tests with clear setup, execution, and verification
4. **Mock External Dependencies**: Use mocks for external services and APIs
5. **Test Edge Cases**: Include tests for error conditions and boundary values
6. **Keep Tests Simple**: Focus on single responsibilities per test
7. **Use Fixtures**: Leverage shared test data and utilities
8. **Clean Up**: Ensure tests clean up temporary resources

## Continuous Integration

Tests are run automatically via GitHub Actions:
- Unit tests run on every push and pull request
- Integration tests run after unit tests pass
- E2E tests run on release branches
- Coverage reports are generated and tracked

## Migration Notes

This centralized structure was created by moving tests from:
- `backend/test_*.py` → `tests/backend/unit/` and `tests/backend/integration/`
- `frontend/src/components/__tests__/` → `tests/frontend/unit/components/`
- Root level test files → `tests/backend/integration/`

All file moves were done with `git mv` to preserve history.