# Provider Interface

All LLM providers inherit from the abstract base class `LLMProvider` in
`backend/llm_providers/base.py`.

## Required Methods

```python
class LLMProvider(ABC):
    @abstractmethod
    def generate_questions(self, subject: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Generate quiz questions for a given subject."""

    @abstractmethod
    def health_check(self) -> bool:
        """Check if the provider is available and working."""
```

## `generate_questions(subject, limit)`
- Returns a list of question dicts. Each question should contain the fields the
  frontend expects: `text`, `options`, and `correct_answer`.
- Raise `RuntimeError` on API failure with a message that does **not** leak the API key.

## `health_check()`
- Returns `True` if the provider is configured and reachable, `False` otherwise.
- Must not raise; swallow errors and return `False`.

## Registration (`backend/llm_providers/__init__.py`)
- Import the provider class.
- Add a branch to `create_llm_provider(provider_type, **kwargs)` for the new type.
- Add the provider's models to `AVAILABLE_MODELS`.

## Prompt Logging (optional but recommended)
Follow `openai_provider.py`: obtain `llm_prompt_logger` in `__init__` and call
`log_prompt(...)` on both success and failure, recording provider, model,
prompt, response/error, metadata, and timing.
