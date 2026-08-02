---
applyTo: 'backend/**/*.py'
description: 'Coding rules for the Quizly FastAPI backend.'
---

# FastAPI Backend Conventions

When writing or editing Python code in the backend:

- Define request and response bodies as **Pydantic models** — do not accept or return raw dicts for structured payloads.
- Return correct **HTTP status codes** and raise `HTTPException` for error responses; never return error strings with a 200.
- Use module-level loggers via `logging.getLogger(__name__)`. Do not use `print`.
- **Never log or return secrets** (API keys, tokens) or full stack traces in responses.
- All SQL must use **parameterized queries** (`?` placeholders). Never build SQL with f-strings, `%`, or `.format()`.
- Load configuration through `config_manager`; do not scatter `os.getenv` calls across endpoints.
- New LLM providers must implement the `LLMProvider` interface in `backend/llm_providers/base.py` and be registered in `create_llm_provider`.
- Keep endpoint handlers thin — push business logic into helper functions or modules.
