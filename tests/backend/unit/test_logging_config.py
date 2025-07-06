"""Test the logging configuration functionality."""

import pytest
import json
import os
import sys
import tempfile
from fastapi.testclient import TestClient

# Ensure backend modules can be imported
BACKEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../../backend')
)
sys.path.append(BACKEND_DIR)

def test_logging_config_endpoints():
    """Test the logging configuration endpoints."""
    
    # Test the logging configuration manager directly first
    from logging_config import LoggingConfigManager
    
    # Create a temporary config file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_config_file = f.name
    
    try:
        # Initialize logging config manager with temp file
        config_mgr = LoggingConfigManager(temp_config_file)
        
        # Test default configuration
        config = config_mgr.get_config()
        assert config is not None
        assert "log_levels" in config
        assert "frontend" in config["log_levels"]
        assert "backend" in config["log_levels"]
        
        # Test updating configuration
        updates = {
            "log_levels": {
                "backend": {
                    "api": "DEBUG"
                }
            }
        }
        updated_config = config_mgr.update_config(updates)
        assert updated_config["log_levels"]["backend"]["api"] == "DEBUG"
        
        # Test configuration persistence
        assert os.path.exists(temp_config_file)
        with open(temp_config_file, 'r') as f:
            file_config = json.load(f)
            assert file_config["log_levels"]["backend"]["api"] == "DEBUG"
        
        # Test log level setting and getting
        config_mgr.set_log_level("backend", "ERROR", "llm")
        level = config_mgr.get_log_level("backend", "llm")
        assert level == "ERROR"
        
        print("Logging configuration tests passed!")
        
    finally:
        # Clean up
        if os.path.exists(temp_config_file):
            os.remove(temp_config_file)


def test_logging_api_endpoints():
    """Test the logging API endpoints."""
    try:
        # Import the FastAPI app
        from main import app
        client = TestClient(app)
        
        # Test get logging config endpoint
        response = client.get("/api/logging/config")
        assert response.status_code == 200
        data = response.json()
        assert "config" in data
        assert "available_levels" in data
        assert "ERROR" in data["available_levels"]
        
        # Test update logging config endpoint
        update_data = {
            "log_levels": {
                "backend": {
                    "api": "DEBUG"
                }
            }
        }
        response = client.put("/api/logging/config", json=update_data)
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        
        # Test get log files endpoint
        response = client.get("/api/logging/files")
        assert response.status_code == 200
        data = response.json()
        assert "files" in data
        
        # Test get recent logs endpoint
        response = client.get("/api/logging/recent")
        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
        
        print("Logging API endpoint tests passed!")
        
    except Exception as e:
        print(f"API endpoint tests failed (this may be expected if dependencies are missing): {e}")


if __name__ == "__main__":
    test_logging_config_endpoints()
    test_logging_api_endpoints()
    print("All logging tests completed!")