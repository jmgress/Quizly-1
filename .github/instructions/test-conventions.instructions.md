---
applyTo: 'tests/**'
description: 'Testing conventions for Quizly (backend pytest and frontend Jest).'
---

# Test Conventions

When writing or editing tests:

- Structure every test with **Arrange-Act-Assert**.
- Use descriptive names that state the behavior under test (e.g. `test_generate_questions_returns_five_items`).
- **Mock all external services** — LLM providers, HTTP calls, filesystem side effects. Tests must never hit the network or a real API.
- For backend database tests, use **in-memory SQLite**; never touch the real `quiz.db`.
- Reuse shared fixtures and helpers from `tests/shared/` instead of duplicating setup.
- Keep tests **isolated** — no shared mutable state or ordering dependencies between tests.
- Backend: pytest + fixtures. Frontend: Jest + React Testing Library with role/label-based queries.
- Assert on specific values and response shapes, not just that a call did not throw.
