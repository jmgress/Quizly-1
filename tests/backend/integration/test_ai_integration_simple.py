"""Simple AI integration tests that do not make actual external API calls."""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))


def test_ai_providers_import():
    """Test that AI provider helpers can be imported."""
    from llm_providers import get_available_providers, get_available_models

    providers = get_available_providers()
    assert isinstance(providers, list)


def test_configuration_loading():
    """Test that the configuration manager loads a config with the expected keys."""
    from config_manager import config_manager

    config = config_manager.get_config()

    assert config is not None
    assert "llm_provider" in config


def test_fastapi_import():
    """Test that the FastAPI application can be imported."""
    from main import app

    assert app is not None


def test_environment_variables():
    """Test that environment variables can be set and retrieved."""
    original = os.environ.get("TEST_VAR")
    try:
        os.environ["TEST_VAR"] = "test_value"
        assert os.getenv("TEST_VAR") == "test_value"
    finally:
        if original is None:
            os.environ.pop("TEST_VAR", None)
        else:
            os.environ["TEST_VAR"] = original
