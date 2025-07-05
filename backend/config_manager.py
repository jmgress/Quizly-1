"""Configuration manager for LLM provider settings."""

import json
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger("api_server.config") # Use a more specific logger name

CONFIG_FILE = "llm_config.json"

class ConfigManager:
    """Manages LLM provider configuration with file persistence."""
    
    def __init__(self, config_file: str = CONFIG_FILE):
        self.config_file = config_file
        self._config = None
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file, fallback to environment variables."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self._config = json.load(f)
                logger.info(f"Loaded configuration from {self.config_file}")
            else:
                self._config = self._get_default_config()
                logger.info("Using default configuration from environment variables")
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration from environment variables."""
        return {
            "llm_provider": os.getenv("LLM_PROVIDER", "ollama").lower(),
            "ollama_model": os.getenv("OLLAMA_MODEL", "llama3.2"),
            "ollama_host": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
            "openai_model": os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
        }
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            raise
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self._config.copy()
    
    def update_config(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update configuration with new values."""
        for key, value in updates.items():
            if key in self._config:
                self._config[key] = value
            else:
                logger.warning(f"Unknown config key: {key}")
        
        self.save_config()
        return self._config.copy()
    
    def get_provider_config(self) -> Dict[str, Any]:
        """Get provider-specific configuration."""
        provider = self._config["llm_provider"]
        
        if provider == "ollama":
            return {
                "provider": "ollama",
                "model": self._config["ollama_model"],
                "host": self._config["ollama_host"]
            }
        elif provider == "openai":
            return {
                "provider": "openai",
                "model": self._config["openai_model"],
                "api_key": self._config["openai_api_key"]
            }
        else:
            raise ValueError(f"Unknown provider: {provider}")

# Global instance
config_manager = ConfigManager()