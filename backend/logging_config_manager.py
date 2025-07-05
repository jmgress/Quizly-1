"""Configuration manager for logging settings."""

import json
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

CONFIG_FILE = "logging_config.json" # Relative to project root

class LoggingConfigManager:
    """Manages logging configuration with file persistence."""

    def __init__(self, config_file: str = CONFIG_FILE):
        self.config_file = config_file
        self._config = None
        self._ensure_config_file_exists() # Ensure it's at project root
        self._load_config()

    def _ensure_config_file_exists(self):
        """Ensures the config file path is correct and accessible from backend directory."""
        # Adjust path to be relative to project root if called from backend/
        if not os.path.isabs(self.config_file) and os.path.basename(os.getcwd()) == 'backend':
            self.config_file = os.path.join("..", self.config_file)

        if not os.path.exists(self.config_file):
            logger.warning(f"Config file {self.config_file} not found. Creating with default values.")
            self._config = self._get_default_config()
            self.save_config() # Save the default config

    def _load_config(self):
        """Load configuration from file, fallback to defaults."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self._config = json.load(f)
                logger.info(f"Loaded logging configuration from {self.config_file}")
            else:
                # This case should ideally be handled by _ensure_config_file_exists
                # but as a fallback:
                logger.warning(f"Logging config file {self.config_file} not found during load. Using defaults.")
                self._config = self._get_default_config()
                self.save_config() # Attempt to save if it was missing
        except Exception as e:
            logger.error(f"Error loading logging config: {e}. Using default configuration.")
            self._config = self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default logging configuration."""
        return {
            "global_level": "INFO",
            "frontend_level": "INFO",
            "backend_levels": {
                "api_server": "INFO",
                "llm_providers": "INFO",
                "database": "WARNING"
            },
            "log_files": {
                "frontend_app": "logs/frontend/app.log", # Path relative to project root
                "backend_api": "logs/backend/api.log",
                "backend_llm": "logs/backend/llm.log",
                "backend_database": "logs/backend/database.log",
                "backend_error": "logs/backend/error.log",
                "combined": "logs/combined.log"
            },
            "log_rotation_max_bytes": 10485760,  # 10MB
            "log_rotation_backup_count": 5,
            "enable_file_logging": True
        }

    def save_config(self):
        """Save current configuration to file."""
        try:
            # Ensure path is correct if called from backend/
            config_file_path = self.config_file
            if not os.path.isabs(config_file_path) and os.path.basename(os.getcwd()) == 'backend':
                config_file_path = os.path.join("..", config_file_path)

            with open(config_file_path, 'w') as f:
                json.dump(self._config, f, indent=2)
            logger.info(f"Logging configuration saved to {config_file_path}")
        except Exception as e:
            logger.error(f"Error saving logging config: {e}")
            # Not raising here to avoid crashing the app if logging config save fails

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        if self._config is None: # Should not happen if constructor logic is correct
            self._load_config()
        return self._config.copy() # Return a copy to prevent external modification

    def update_config(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update configuration with new values and save."""
        if self._config is None:
            self._load_config()

        # Deep merge for nested dictionaries like backend_levels and log_files
        for key, value in updates.items():
            if isinstance(value, dict) and isinstance(self._config.get(key), dict):
                for sub_key, sub_value in value.items():
                    if sub_key in self._config[key]:
                        self._config[key][sub_key] = sub_value
                    else:
                        logger.warning(f"Unknown sub-key '{sub_key}' in '{key}' for logging config.")
            elif key in self._config:
                self._config[key] = value
            else:
                logger.warning(f"Unknown config key: {key} for logging config.")

        self.save_config()
        return self.get_config()

# Global instance (optional, depends on usage pattern)
# logging_config_manager = LoggingConfigManager()
# For now, let's instantiate it where needed to ensure correct pathing from main.py

# Example usage (for testing this file directly):
if __name__ == "__main__":
    # This assumes the script is run from the `backend` directory
    # Adjust path for logging_config.json accordingly if run from project root
    if os.path.basename(os.getcwd()) == 'backend':
        manager = LoggingConfigManager(config_file="../logging_config.json")
    else: # Assuming run from project root
        manager = LoggingConfigManager(config_file="logging_config.json")

    print("Initial config:", manager.get_config())

    # Test update
    manager.update_config({"global_level": "DEBUG", "backend_levels": {"api_server": "VERBOSE"}}) #VERBOSE is not standard, testing warning
    print("Updated config:", manager.get_config())

    # Test saving a new key (should warn and not add)
    manager.update_config({"new_unknown_key": "test_value"})
    print("Config after unknown key:", manager.get_config())

    # Restore
    manager.update_config({"global_level": "INFO", "backend_levels": {"api_server": "INFO"}})
    print("Restored config:", manager.get_config())
