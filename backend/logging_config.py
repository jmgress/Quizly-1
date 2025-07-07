"""Configuration manager for logging settings."""

import json
import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import glob

logger = logging.getLogger(__name__)

LOGGING_CONFIG_FILE = "logging_config.json"
LOGS_DIR = "logs"

class LoggingConfigManager:
    """Manages logging configuration with file persistence."""
    
    def __init__(self, config_file: str = LOGGING_CONFIG_FILE):
        self.config_file = config_file
        self.logs_dir = LOGS_DIR
        self._config = None
        self._load_config()
        self._ensure_logs_directory()
    
    def _load_config(self):
        """Load logging configuration from file, fallback to defaults."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self._config = json.load(f)
                logger.info(f"Loaded logging configuration from {self.config_file}")
            else:
                self._config = self._get_default_config()
                logger.info("Using default logging configuration")
        except Exception as e:
            logger.error(f"Error loading logging config: {e}")
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default logging configuration."""
        return {
            "log_levels": {
                "frontend": {
                    "app": "INFO"
                },
                "backend": {
                    "api": "INFO",
                    "llm": "INFO",
                    "database": "INFO"
                }
            },
            "file_settings": {
                "enable_file_logging": True,
                "log_directory": self.logs_dir,
                "max_file_size_mb": 10,
                "max_backup_files": 5,
                "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "monitoring": {
                "enable_live_viewer": True,
                "max_recent_entries": 100,
                "auto_refresh_interval": 5000
            },
            "llm_prompt_logging": {
                "enabled": True,
                "level": "INFO"
            }
        }
    
    def _ensure_logs_directory(self):
        """Ensure logs directory structure exists."""
        try:
            # Create main logs directory
            os.makedirs(self.logs_dir, exist_ok=True)
            
            # Create subdirectories for frontend and backend
            os.makedirs(os.path.join(self.logs_dir, "frontend"), exist_ok=True)
            backend_logs_dir = os.path.join(self.logs_dir, "backend")
            os.makedirs(backend_logs_dir, exist_ok=True)

            # Ensure llm_prompts.log file exists
            llm_prompts_log_file = os.path.join(backend_logs_dir, "llm_prompts.log")
            if not os.path.exists(llm_prompts_log_file):
                with open(llm_prompts_log_file, 'w') as f:
                    f.write("") # Create an empty file
                logger.info(f"Created LLM prompts log file at {llm_prompts_log_file}")
            
            logger.info(f"Ensured logs directory structure at {self.logs_dir}")
        except Exception as e:
            logger.error(f"Error creating logs directory: {e}")
            raise
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
            logger.info(f"Logging configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving logging config: {e}")
            raise
    
    def get_config(self) -> Dict[str, Any]:
        """Get current logging configuration."""
        return self._config.copy()
    
    def update_config(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update logging configuration with new values."""
        try:
            # Deep merge the updates
            self._deep_merge(self._config, updates)
            self.save_config()
            return self._config.copy()
        except Exception as e:
            logger.error(f"Error updating logging config: {e}")
            raise
    
    def _deep_merge(self, target: Dict, source: Dict):
        """Deep merge two dictionaries."""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value
    
    def get_log_level(self, component: str, subcomponent: str = None) -> str:
        """Get log level for a specific component."""
        try:
            if subcomponent:
                return self._config["log_levels"][component][subcomponent]
            else:
                return self._config["log_levels"][component]
        except KeyError:
            return "INFO"  # Default fallback
    
    def set_log_level(self, component: str, level: str, subcomponent: str = None):
        """Set log level for a specific component."""
        try:
            if subcomponent:
                if component not in self._config["log_levels"]:
                    self._config["log_levels"][component] = {}
                self._config["log_levels"][component][subcomponent] = level
            else:
                self._config["log_levels"][component] = level
            self.save_config()
        except Exception as e:
            logger.error(f"Error setting log level: {e}")
            raise

    def get_llm_prompt_logging_config(self) -> Dict[str, Any]:
        """Get LLM prompt logging configuration."""
        return self._config.get("llm_prompt_logging", {"enabled": False, "level": "INFO"})

    def set_llm_prompt_logging_config(self, enabled: bool, level: str):
        """Set LLM prompt logging configuration."""
        try:
            if "llm_prompt_logging" not in self._config:
                self._config["llm_prompt_logging"] = {}
            self._config["llm_prompt_logging"]["enabled"] = enabled
            self._config["llm_prompt_logging"]["level"] = level
            # Also update the general log_levels for the llm_prompts logger
            if "backend" not in self._config["log_levels"]:
                self._config["log_levels"]["backend"] = {}
            self._config["log_levels"]["backend"]["llm_prompts"] = level
            self.save_config()
            logger.info(f"LLM prompt logging set to enabled: {enabled}, level: {level}")
        except Exception as e:
            logger.error(f"Error setting LLM prompt logging config: {e}")
            raise
    
    def get_log_files(self) -> List[Dict[str, Any]]:
        """Get list of available log files with metadata."""
        log_files = []
        
        try:
            # Search for log files in the logs directory, including subdirectories
            patterns = [
                os.path.join(self.logs_dir, "*.log"), # Logs in root of logs_dir
                os.path.join(self.logs_dir, "frontend", "*.log"),
                os.path.join(self.logs_dir, "backend", "*.log")
            ]

            processed_files = set()

            for pattern in patterns:
                for file_path in glob.glob(pattern):
                    if file_path in processed_files:
                        continue
                    processed_files.add(file_path)

                    try:
                        stat = os.stat(file_path)
                    rel_path = os.path.relpath(file_path, self.logs_dir)
                    
                    log_files.append({
                        "path": rel_path,
                        "full_path": file_path,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "component": self._get_component_from_path(rel_path)
                    })
                except Exception as e:
                    logger.warning(f"Error reading log file {file_path}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error listing log files: {e}")
        
        return sorted(log_files, key=lambda x: x["modified"], reverse=True)
    
    def _get_component_from_path(self, path: str) -> str:
        """Extract component name from log file path."""
        parts = path.split(os.sep)
        if len(parts) >= 2:
            return f"{parts[0]}/{parts[1].replace('.log', '')}"
        return path.replace('.log', '')
    
    def get_recent_logs(self, max_entries: int = None) -> List[Dict[str, Any]]:
        """Get recent log entries from all log files."""
        if max_entries is None:
            max_entries = self._config["monitoring"]["max_recent_entries"]
        
        all_entries = []
        
        try:
            for log_file in self.get_log_files():
                try:
                    with open(log_file["full_path"], 'r') as f:
                        lines = f.readlines()
                        # Get last few lines from each file
                        for line in lines[-20:]:  # Last 20 lines per file
                            if line.strip():
                                all_entries.append({
                                    "timestamp": datetime.now().isoformat(),
                                    "component": log_file["component"],
                                    "message": line.strip(),
                                    "level": self._extract_log_level(line)
                                })
                except Exception as e:
                    logger.warning(f"Error reading log file {log_file['full_path']}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error getting recent logs: {e}")
        
        # Sort by timestamp and limit results
        all_entries.sort(key=lambda x: x["timestamp"], reverse=True)
        return all_entries[:max_entries]
    
    def _extract_log_level(self, log_line: str) -> str:
        """Extract log level from a log line."""
        levels = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE"]
        for level in levels:
            if level in log_line:
                return level
        return "INFO"
    
    def clear_log_file(self, file_path: str):
        """Clear contents of a specific log file."""
        try:
            full_path = os.path.join(self.logs_dir, file_path)
            if os.path.exists(full_path):
                with open(full_path, 'w') as f:
                    f.write("")
                logger.info(f"Cleared log file: {file_path}")
            else:
                raise FileNotFoundError(f"Log file not found: {file_path}")
        except Exception as e:
            logger.error(f"Error clearing log file {file_path}: {e}")
            raise
    
    def rotate_log_file(self, file_path: str):
        """Rotate a specific log file."""
        try:
            full_path = os.path.join(self.logs_dir, file_path)
            if os.path.exists(full_path):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"{full_path}.{timestamp}"
                os.rename(full_path, backup_path)
                logger.info(f"Rotated log file: {file_path} -> {backup_path}")
            else:
                raise FileNotFoundError(f"Log file not found: {file_path}")
        except Exception as e:
            logger.error(f"Error rotating log file {file_path}: {e}")
            raise


# Global instance
logging_config_manager = LoggingConfigManager()