"""
LLM Provider factory and utility functions.
This file is responsible for creating instances of LLM providers
and providing utility functions related to providers.
Individual provider implementations are in the `backend.llm` package.
"""

import os
import logging
from typing import List, Any

# Import from the llm_providers package directory
from llm_providers import LLMProvider, OllamaProvider, OpenAIProvider
from config_manager import config_manager

# Configure logging
# logging.basicConfig(level=logging.INFO) # Removed: Handled in main.py
logger = logging.getLogger("llm_providers") # Use component-specific logger


# Provider Factory
def create_llm_provider(provider_type: str = None, **kwargs) -> LLMProvider:
    """
    Factory function to create LLM provider instances.
    
    Args:
        provider_type: Type of provider ("ollama" or "openai")
        **kwargs: Additional configuration for the provider
        
    Returns:
        LLMProvider instance
    """
    if provider_type is None:
        # Get provider from config manager first, then environment
        provider_type = config_manager.get_config()["llm_provider"]
    
    logger.info(f"Creating LLM provider: {provider_type}")
    
    if provider_type == "ollama":
        # Use config manager values if no kwargs provided
        config = config_manager.get_config()
        model = kwargs.get("model", config["ollama_model"])
        host = kwargs.get("host", config["ollama_host"])
        return OllamaProvider(model=model, host=host)
    
    elif provider_type == "openai":
        # Use config manager values if no kwargs provided
        config = config_manager.get_config()
        api_key = kwargs.get("api_key", config["openai_api_key"])
        model = kwargs.get("model", config["openai_model"])
        return OpenAIProvider(api_key=api_key, model=model)
    
    else:
        raise ValueError(f"Unknown provider type: {provider_type}. Supported types: 'ollama', 'openai'")


def get_available_providers() -> List[str]:
    """Get list of available providers based on configuration."""
    providers = []
    
    # Check Ollama
    try:
        config = config_manager.get_config()
        provider = create_llm_provider("ollama")
        if provider.health_check():
            providers.append("ollama")
    except Exception:
        pass
    
    # Check OpenAI
    try:
        config = config_manager.get_config()
        if config["openai_api_key"]:
            provider = create_llm_provider("openai")
            if provider.health_check():
                providers.append("openai")
    except Exception:
        pass
    
    return providers

def get_available_models(provider_type: str = None) -> List[str]:
    """Get list of available models for a provider."""
    if provider_type is None:
        provider_type = config_manager.get_config()["llm_provider"]
    
    # Import here to avoid circular imports
    from llm_providers import get_available_models as get_models
    return get_models(provider_type)