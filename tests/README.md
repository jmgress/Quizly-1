# Quizly Test Organization

This directory centralizes backend tests for the Quizly application. Frontend tests are located within the `frontend/src/tests` directory to align with Create React App conventions.

## Directory Structure

- **`tests/backend/`**: Contains all Python tests for the FastAPI backend.
    - **`tests/backend/unit/`**: Unit tests for individual backend modules, classes, and functions. These tests should be fast and isolated, often using mocks for external dependencies.
    - **`tests/backend/integration/`**: Integration tests that verify interactions between different backend components, such as API endpoints and database interactions, or interactions with external services (which might be mocked).
    - **`tests/backend/fixtures/`**: (Planned) Intended for shared test fixtures, mock data, or configuration files used by multiple backend tests.

- **`tests/frontend/`**: This directory was part of the initial plan for centralizing all tests. However, due to Create React App's conventions and build process, frontend tests have been located at `frontend/src/tests/`.
    - See `frontend/src/tests/README.md` (if created) or `frontend/package.json` for details on frontend test structure (`unit`, `integration`, etc.).

- **`tests/e2e/`**: (Planned) Intended for End-to-End tests that simulate full user workflows across the entire application (frontend and backend). Currently empty.

- **`tests/shared/`**: (Planned) Intended for shared helper functions, utilities, or mock servers that can be used by tests across different domains (backend, frontend, e2e). Currently empty.
    - Examples might include `test_helpers.py` or `test_helpers.js`.

## Running Tests

The primary way to run all tests is using the `run_tests.sh` script in the project root:
```bash
./run_tests.sh
```

This script can also run specific suites:
```bash
./run_tests.sh backend
./run_tests.sh backend unit
./run_tests.sh backend integration
./run_tests.sh frontend
```

For more details on running tests, specific commands, and debugging, please refer to the main `TESTING_GUIDE.md` in the project root.
