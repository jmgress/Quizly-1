---
mode: agent
description: 'Generate a pytest integration test for a Quizly FastAPI endpoint.'
---

# Generate API Integration Test

Generate a complete pytest integration test for the following backend endpoint.

## Inputs
- **Endpoint path**: ${input:ENDPOINT:e.g. /api/questions}
- **HTTP method**: ${input:HTTP_METHOD:GET|POST|PUT|DELETE}

## Requirements

Follow the Quizly test conventions found in `tests/backend/integration/test_api_endpoints.py`:

- Use FastAPI's `TestClient` against the app in `backend/main.py`.
- Use an **in-memory SQLite** database — never touch the real `quiz.db`.
- **Mock all external services** (LLM providers, network calls). Never make a real API call.
- Structure each test with **Arrange-Act-Assert** and a descriptive `test_<behavior>` name.
- Cover at minimum:
  1. **Happy path** — valid request returns the expected status code and response schema.
  2. **Validation failure** — invalid or missing input returns `422` / `400`.
  3. **Error handling** — downstream failure (e.g. provider error) returns the correct status code and a safe error message that leaks no secrets.
- Assert on both the HTTP status code and the JSON body shape.
- Place the test in the correct file under `tests/backend/integration/`.

Explain any fixtures you add and why they are needed.
