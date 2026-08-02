---
mode: agent
description: 'Refactor the selected code to use a chosen design pattern without changing behavior.'
---

# Refactor to Design Pattern

Refactor the selected code to use the **${input:PATTERN:Strategy|Factory|Observer|Singleton|Decorator}** design pattern.

## Rules
- **Preserve behavior exactly.** The refactor must not change any observable output or side effect.
- Keep the public interface stable so existing callers and tests continue to pass.
- Add a single short inline comment where the pattern's intent is not obvious from the code.
- Match the existing style of the file (Python for backend, JS/React for frontend).
- After refactoring, list which existing tests cover this code and note any gaps that need a new test.

## Notes
- The Quizly LLM system already uses a **Factory** (`create_llm_provider` in `backend/llm_providers/__init__.py`) and a **Strategy**-style base (`LLMProvider` in `backend/llm_providers/base.py`). Align with those conventions where relevant.
