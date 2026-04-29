# Quizly AI Coding Agent Instructions

## Project Architecture

- **Monorepo Structure:**
  - `backend/`: FastAPI app, SQLite DB, modular config/logging/LLM provider system
  - `frontend/`: React app, communicates via REST API
  - `tests/`: Organized by backend, frontend, integration, e2e, shared helpers
  - `logs/`: All logs, separated by backend/frontend

## Key Workflows

- **Start App:** `./start.sh` (runs backend and frontend)
- **Run All Tests:** `./run_tests.sh` (backend, frontend, security)
- **Backend Tests:** `cd backend && pip install -r requirements-dev.txt && pytest`
- **Frontend Tests:** `cd frontend && npm test -- --watchAll=false`
- **Security Scan:** `./scripts/test_gitleaks.sh` (custom rules, allowlist)
- **Coverage:** Backend: `pytest --cov` | Frontend: `npm test -- --coverage`

## Critical Patterns and Conventions

### Backend

- Use pytest for all tests — no top-level script code, real assertions only
- Use in-memory SQLite for unit tests; integration tests hit real implementations
- Mock external services (see `tests/shared/`)
- Logging via `logging_config.json` and `logging_config.py` (path traversal protection)
- LLM providers are pluggable (`backend/llm_providers/`), config via API/UI
- Use type hints on all function signatures; Pydantic models for validation
- Config via `config_manager.py` and environment variables — never hardcode values

### Frontend

- Components in `src/components/`, state via React Hooks (no class components)
- Jest and React Testing Library, snapshot tests, mock dependencies
- HTTP via Axios; use `API_BASE_URL` from env — never hardcode base URLs

### Testing

- Arrange-Act-Assert pattern, clear naming, isolation
- Fixtures and helpers in `tests/shared/`
- Frontend coverage target: 80% or higher

### Security

- Validate and sanitize all file paths (path traversal protection)
- Never log sensitive data (tokens, passwords, PII)
- GitLeaks integrated in CI with custom rules and allowlist for false positives

## Integration Points

- **API Endpoints:** Frontend calls backend REST endpoints for quiz, admin, logging, and LLM config
- **LLM Provider Switching:** Change provider via admin UI/API, no restart required
- **Config Management:** Centralized in `backend/config_manager.py`, exposed via API
- **Shared Test Utilities:** `tests/shared/` for Python/JS helpers and mock server

## Examples

- **Add LLM Provider:** Implement in `backend/llm_providers/`, update config, test with `test_ai_integration_simple.py`
- **Run Security Scan:** `./scripts/test_gitleaks.sh` or `./run_tests.sh`
- **View Logs:** Admin UI or `logs/` directory

## References

- `README.md` — project overview and setup
- `docs/TESTING_GUIDE.md` — test organization and running instructions
- `docs/GITHUB_ACTIONS_SETUP.md` — CI/CD setup
- `docs/GITLEAKS_INTEGRATION_SUMMARY.md` — secrets scanning
- `tests/README.md` — test structure
