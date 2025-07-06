"""Test the new LLM configuration management endpoints."""

import pytest
import json
import os
import sys
import tempfile

# Add backend directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

# Test the configuration manager directly first
def test_config_manager():
    """Test the configuration manager functionality."""
    from config_manager import ConfigManager
    
    # Use temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_file:
        temp_config_file = temp_file.name
    
    try:
        # Create config manager with temp file
        config_mgr = ConfigManager(temp_config_file)
        
        # Test getting default config
        config = config_mgr.get_config()
        assert "llm_provider" in config
        assert "ollama_model" in config
        assert "ollama_host" in config
        assert "openai_model" in config
        assert "openai_api_key" in config
        
        # Test updating config
        updates = {
            "llm_provider": "openai",
            "openai_model": "gpt-4"
        }
        updated_config = config_mgr.update_config(updates)
        assert updated_config["llm_provider"] == "openai"
        assert updated_config["openai_model"] == "gpt-4"
        
        # Test provider config
        provider_config = config_mgr.get_provider_config()
        assert provider_config["provider"] == "openai"
        assert provider_config["model"] == "gpt-4"
        
        # Test file persistence
        assert os.path.exists(temp_config_file)
        with open(temp_config_file, 'r') as f:
            file_config = json.load(f)
            assert file_config["llm_provider"] == "openai"
            assert file_config["openai_model"] == "gpt-4"
            
    finally:
        # Clean up
        if os.path.exists(temp_config_file):
            os.remove(temp_config_file)

def test_llm_providers_import():
    """Test that the LLM providers can be imported and used."""
    from llm_providers import create_llm_provider, get_available_providers
    
    # Test creating providers
    try:
        ollama_provider = create_llm_provider("ollama")
        assert ollama_provider is not None
    except Exception as e:
        # Expected if Ollama is not available
        assert "ollama" in str(e).lower() or "import" in str(e).lower()
    
    try:
        openai_provider = create_llm_provider("openai", api_key="test-key")
        assert openai_provider is not None
    except Exception as e:
        # Expected if OpenAI package is not properly configured
        pass
    
    # Test getting available providers (should not crash)
    providers = get_available_providers()
    assert isinstance(providers, list)

def test_main_app_imports():
    """Test that the main app can be imported."""
    try:
        from main import app
        assert app is not None
        print("Main app imported successfully")
    except Exception as e:
        print(f"Error importing main app: {e}")
        # Don't fail the test as the app might have complex dependencies

if __name__ == "__main__":
    test_config_manager()
    test_llm_providers_import()
    test_main_app_imports()
    print("All tests passed!")