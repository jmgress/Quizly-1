---
name: llm-provider-scaffold
description: 'Scaffold a new LLM provider for the Quizly backend. Use when: adding a new AI provider, integrating a new LLM API, creating a provider plugin, extending the LLM provider system, or adding Anthropic/Gemini/Mistral/Claude support.'
argument-hint: 'Provider name (e.g. anthropic, gemini, mistral)'
---

# LLM Provider Scaffold

Scaffold a complete, convention-matching LLM provider for the Quizly backend, including its module, registration, and tests.

## When to Use
- The user wants to add a new LLM provider (e.g. Anthropic, Gemini, Mistral).
- Integrating a third-party question-generation API into the pluggable provider system.

## Procedure

1. **Gather requirements**
   - Provider name (lowercase, no spaces) — e.g. `anthropic`.
   - API base URL and authentication method.
   - Required pip dependency and the API-key environment variable name (`<NAME>_API_KEY`).

2. **Create the provider module**
   - Copy [provider template](./assets/provider_template.py) to `backend/llm_providers/<name>_provider.py`.
   - Implement the `LLMProvider` interface — see [provider interface](./references/provider-interface.md).
   - Read the API key from the environment; raise `ValueError` if it is missing.

3. **Register the provider**
   - Import the new class in `backend/llm_providers/__init__.py`.
   - Add a branch to the `create_llm_provider` factory for the new `provider_type`.
   - Add the provider's models to the `AVAILABLE_MODELS` dict.

4. **Add tests**
   - Copy [test template](./assets/provider_test_template.py) to `tests/backend/unit/test_<name>_provider.py`.
   - **Mock the external API** — never make a real network call in tests.
   - Cover: initialization (with and without key), successful generation, and error handling.

5. **Wire configuration**
   - Ensure the provider is selectable via `config_manager` so it appears in the admin UI dropdown.

6. **Validate**
   - Run `cd backend && pytest ../tests/backend/unit/test_<name>_provider.py`.
   - Run `cd backend && pytest ../tests/backend/integration/test_ai_integration_simple.py`.
   - Confirm no secrets are logged and the key is only read from the environment.

## Security Notes
- Never hardcode API keys. Read them from `<NAME>_API_KEY` only.
- Never include the key in log output, error messages, or responses.
