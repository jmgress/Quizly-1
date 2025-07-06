"""Test configuration settings and helpers."""

import os
import tempfile
import json
from typing import Dict, Any

# Test database configuration
TEST_DB_CONFIG = {
    "database_url": ":memory:",  # Use in-memory SQLite for tests
    "echo": False  # Disable SQL logging during tests
}

# Test API configuration
TEST_API_CONFIG = {
    "host": "127.0.0.1",
    "port": 8000,
    "debug": True,
    "testing": True
}

# Test environment variables
TEST_ENV_VARS = {
    "TESTING": "true",
    "DATABASE_URL": "sqlite:///:memory:",
    "LOG_LEVEL": "WARNING",
    "OPENAI_API_KEY": "test-api-key",
    "LLM_PROVIDER": "openai",
    "OPENAI_MODEL": "gpt-3.5-turbo"
}

class TestConfig:
    """Configuration class for testing environments."""
    
    def __init__(self):
        self.temp_dir = None
        self.temp_files = []
        
    def create_temp_config_file(self, config_data: Dict[str, Any] = None) -> str:
        """Create a temporary configuration file for testing."""
        if config_data is None:
            config_data = {
                "llm_provider": "openai",
                "openai_model": "gpt-3.5-turbo",
                "openai_api_key": "test-key",
                "ollama_model": "llama3.2",
                "ollama_host": "http://localhost:11434"
            }
        
        temp_file = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.json', 
            delete=False
        )
        
        json.dump(config_data, temp_file, indent=2)
        temp_file.close()
        
        self.temp_files.append(temp_file.name)
        return temp_file.name
    
    def create_temp_directory(self) -> str:
        """Create a temporary directory for testing."""
        if self.temp_dir is None:
            self.temp_dir = tempfile.mkdtemp()
        return self.temp_dir
    
    def cleanup(self):
        """Clean up temporary files and directories."""
        import shutil
        
        # Remove temporary files
        for temp_file in self.temp_files:
            try:
                os.remove(temp_file)
            except FileNotFoundError:
                pass
        
        # Remove temporary directory
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        
        self.temp_files = []
        self.temp_dir = None

def set_test_environment():
    """Set up environment variables for testing."""
    for key, value in TEST_ENV_VARS.items():
        os.environ[key] = value

def clear_test_environment():
    """Clear test environment variables."""
    for key in TEST_ENV_VARS.keys():
        if key in os.environ:
            del os.environ[key]

def get_test_database_path() -> str:
    """Get path for test database."""
    return ":memory:"  # Use in-memory database for tests

def get_test_log_config() -> Dict[str, Any]:
    """Get logging configuration for tests."""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": "%(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "simple",
                "level": "WARNING"  # Reduce noise during tests
            }
        },
        "root": {
            "level": "WARNING",
            "handlers": ["console"]
        }
    }

# Test constants
TEST_CONSTANTS = {
    "MAX_QUESTIONS_PER_QUIZ": 10,
    "DEFAULT_QUIZ_TIMEOUT": 30,  # seconds
    "API_TIMEOUT": 5,  # seconds
    "MAX_RETRIES": 3,
    "SUPPORTED_CATEGORIES": ["geography", "math", "programming", "science", "technology", "history"],
    "SUPPORTED_LLM_PROVIDERS": ["openai", "ollama"],
    "DEFAULT_OPENAI_MODEL": "gpt-3.5-turbo",
    "DEFAULT_OLLAMA_MODEL": "llama3.2"
}