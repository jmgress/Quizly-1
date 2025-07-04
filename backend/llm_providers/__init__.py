"""LLM provider package with factory utilities."""

from typing import List
import logging
import os

from .base import LLMProvider
from .ollama_provider import OllamaProvider
from .openai_provider import OpenAIProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_llm_provider(provider_type: str = None, **kwargs) -> LLMProvider:
    """Factory function to create LLM provider instances."""
    if provider_type is None:
        provider_type = os.getenv("LLM_PROVIDER", "ollama").lower()

    logger.info(f"Creating LLM provider: {provider_type}")

    if provider_type == "ollama":
        model = kwargs.get("model", os.getenv("OLLAMA_MODEL", "llama3.2"))
        host = kwargs.get("host", os.getenv("OLLAMA_HOST", "http://localhost:11434"))
        return OllamaProvider(model=model, host=host)
    elif provider_type == "openai":
        api_key = kwargs.get("api_key", os.getenv("OPENAI_API_KEY"))
        model = kwargs.get("model", os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
        return OpenAIProvider(api_key=api_key, model=model)
    else:
        raise ValueError(
            f"Unknown provider type: {provider_type}. Supported types: 'ollama', 'openai'"
        )


def get_available_providers() -> List[str]:
    """Get list of available providers based on configuration."""
    providers: List[str] = []

    try:
        provider = create_llm_provider("ollama")
        if provider.health_check():
            providers.append("ollama")
    except Exception:
        pass

    try:
        if os.getenv("OPENAI_API_KEY"):
            provider = create_llm_provider("openai")
            if provider.health_check():
                providers.append("openai")
    except Exception:
        pass

    return providers
