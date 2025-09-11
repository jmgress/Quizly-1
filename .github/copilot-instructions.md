# Quizly AI Coding Agent Instructions

## Project Overview
- **Quizly** is a full-stack knowledge testing app with a FastAPI backend (Python, SQLite) and a React frontend.
- Supports AI-powered question generation via multiple LLM providers (Ollama, OpenAI).
- Comprehensive logging, security scanning, and CI/CD workflows are integrated.

## Architecture & Data Flow
- **Frontend** (`frontend/`): React app communicates with backend via REST API.
- **Backend** (`backend/`): FastAPI server, SQLite DB, modular config/logging/LLM provider system.
- **LLM Providers** (`backend/llm_providers/`): Pluggable architecture for AI question generation.
- **Logging**: Configurable via `logging_config.json` and managed through API/admin UI.
- **Tests**: Organized in `tests/` (backend, frontend, integration, e2e, shared helpers).

## Key Workflows
- **Start Application**: `./start.sh` launches both backend and frontend servers.
- **Run All Tests**: `./run_tests.sh` executes backend, frontend, and security tests (GitLeaks).
- **Backend Tests**: `cd backend && pip install -r requirements-dev.txt && pytest`
- **Frontend Tests**: `cd frontend && npm test -- --watchAll=false`
- **Security Scan**: `./scripts/test_gitleaks.sh` or via CI pipeline.
- **Coverage Reports**: Backend (`pytest --cov`), Frontend (`npm test -- --coverage`).

## Conventions & Patterns
- **Backend**: Use in-memory SQLite for tests, mock external services, clean up temp files.
- **Frontend**: Jest/React Testing Library, snapshot tests, mock dependencies.
- **LLM Providers**: Add new providers in `backend/llm_providers/`, update config via API/UI.
- **Logging**: All logs stored in `logs/`, configurable levels, path traversal protection.
- **Security**: Custom GitLeaks rules, allowlist for false positives, integrated in CI.
- **Test Structure**: Arrange-Act-Assert, clear naming, isolation, use fixtures/helpers.

## Integration Points
- **API Endpoints**: Frontend calls backend REST endpoints for quiz, admin, logging, LLM config.
- **LLM Provider Switching**: Change provider via admin UI/API, no restart required.
- **Config Management**: Centralized in `backend/config_manager.py` and exposed via API.
- **Shared Test Utilities**: `tests/shared/` for Python/JS helpers and mock server.

## Examples
- **Add LLM Provider**: Implement in `backend/llm_providers/`, update config, test with `test_ai_integration_simple.py`.
- **Run Security Scan**: `./scripts/test_gitleaks.sh` or `./run_tests.sh` (includes security section).
- **View Logs**: Access via admin UI or directly in `logs/` directory.

## References
- See `README.md`, `docs/TESTING_GUIDE.md`, `docs/AI_TEST_FIX.md`, `docs/GITHUB_ACTIONS_SETUP.md`, `docs/GITLEAKS_INTEGRATION_SUMMARY.md` for details.
- Architecture diagram: `docs/README.md`
- Test organization: `tests/README.md`

---
_If any section is unclear or missing, please provide feedback for improvement._
