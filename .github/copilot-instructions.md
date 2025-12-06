---
# Quizly AI Coding Agent Instructions

## Project Architecture
- **Monorepo Structure:**
	- `backend/`: FastAPI app, SQLite DB, modular config/logging/LLM provider system
	- `frontend/`: React app, communicates via REST API
	- `tests/`: Organized by backend, frontend, integration, e2e, shared helpers
	- `logs/`: All logs, separated by backend/frontend

## Key Workflows
- **Start App:** `./start.sh` (runs backend & frontend)
- **Run All Tests:** `./run_tests.sh` (backend, frontend, security)
- **Backend Tests:** `cd backend && pip install -r requirements-dev.txt && pytest`
- **Frontend Tests:** `cd frontend && npm test -- --watchAll=false`
- **Security Scan:** `./scripts/test_gitleaks.sh` (custom rules, allowlist)
- **Coverage:** Backend: `pytest --cov`, Frontend: `npm test -- --coverage`

## Critical Patterns & Conventions
- **Backend:**
	- Use in-memory SQLite for tests
	- Mock external services (see `tests/shared/`)
	- Logging via `logging_config.json` and `logging_config.py` (path traversal protection)
	- LLM providers are pluggable (`backend/llm_providers/`), config via API/UI
- **Frontend:**
	- Components in `src/components/`, state via hooks
	- Jest/React Testing Library, snapshot tests, mock dependencies
- **Testing:**
	- Arrange-Act-Assert, clear naming, isolation, fixtures/helpers in `tests/shared/`
- **Security:**
	- GitLeaks integrated in CI, custom rules, allowlist for false positives

## Integration Points
- **API Endpoints:** Frontend calls backend REST endpoints for quiz, admin, logging, LLM config
- **LLM Provider Switching:** Change provider via admin UI/API, no restart required
- **Config Management:** Centralized in `backend/config_manager.py`, exposed via API
- **Shared Test Utilities:** `tests/shared/` for Python/JS helpers and mock server

## Examples
- **Add LLM Provider:** Implement in `backend/llm_providers/`, update config, test with `test_ai_integration_simple.py`
- **Run Security Scan:** `./scripts/test_gitleaks.sh` or `./run_tests.sh`
- **View Logs:** Admin UI or `logs/` directory

## References
- See `README.md`, `docs/TESTING_GUIDE.md`, `docs/AI_TEST_FIX.md`, `docs/GITHUB_ACTIONS_SETUP.md`, `docs/GITLEAKS_INTEGRATION_SUMMARY.md`
- Architecture diagram: `docs/README.md`
- Test organization: `tests/README.md`

---
_If any section is unclear, outdated, or missing, please provide feedback for improvement._
