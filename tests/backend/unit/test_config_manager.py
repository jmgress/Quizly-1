"""Test the configuration manager functionality."""

import pytest
import json
import os
import sys
import tempfile

# Add the backend directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

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

def test_config_validation():
    """Test configuration validation."""
    from config_manager import ConfigManager
    
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_file:
        temp_config_file = temp_file.name
    
    try:
        config_mgr = ConfigManager(temp_config_file)
        
        # Test invalid provider
        with pytest.raises(ValueError):
            config_mgr.update_config({"llm_provider": "invalid_provider"})
        
        # Test missing required fields for OpenAI
        config_mgr.update_config({"llm_provider": "openai", "openai_api_key": ""})
        provider_config = config_mgr.get_provider_config()
        # Should handle missing API key gracefully
        assert provider_config["provider"] == "openai"
        
    finally:
        if os.path.exists(temp_config_file):
            os.remove(temp_config_file)

if __name__ == "__main__":
    test_config_manager()
    test_config_validation()
    print("All configuration manager tests passed!")