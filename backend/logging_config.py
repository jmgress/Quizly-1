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
            "llm_prompt_logging": {
                "enabled": False,
                "level": "INFO",
                "log_file": "llm_prompts.log",
                "include_metadata": True,
                "include_timing": True,
                "include_full_response": False
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
            }
        }
    
    def _ensure_logs_directory(self):
        """Ensure logs directory structure exists."""
        try:
            # Create main logs directory
            os.makedirs(self.logs_dir, exist_ok=True)
            
            # Create subdirectories for frontend and backend
            os.makedirs(os.path.join(self.logs_dir, "frontend"), exist_ok=True)
            os.makedirs(os.path.join(self.logs_dir, "backend"), exist_ok=True)
            
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
    
    def _validate_safe_path(self, file_path: str) -> str:
        """Validate and sanitize file path to prevent directory traversal attacks.
        
        Args:
            file_path: The file path to validate
            
        Returns:
            str: Safe, absolute path within the logs directory
            
        Raises:
            ValueError: If the path is invalid or attempts directory traversal
        """
        import os.path

        # Remove any null bytes and strip whitespace
        file_path = file_path.replace('\0', '').strip()

        # Reject empty paths
        if not file_path:
            raise ValueError("File path cannot be empty")

        # Reject paths with dangerous sequences
        if '..' in file_path or file_path.startswith('/') or file_path.startswith('\\'):
            raise ValueError("Invalid file path: directory traversal not allowed")

        # Get absolute, real path of logs directory (handle symlinks)
        logs_abs_path = os.path.realpath(os.path.abspath(self.logs_dir))

        # Combine and resolve the path, following symlinks
        candidate_path = os.path.join(logs_abs_path, file_path)
        resolved_path = os.path.realpath(os.path.abspath(candidate_path))

        # Ensure the resolved path is within the logs directory
        if not resolved_path.startswith(logs_abs_path + os.sep) and resolved_path != logs_abs_path:
            raise ValueError("Invalid file path: access outside logs directory not allowed")

        return resolved_path
    
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
    
    def get_log_files(self) -> List[Dict[str, Any]]:
        """Get list of available log files with metadata."""
        log_files = []
        
        try:
            # Search for log files in the logs directory
            pattern = os.path.join(self.logs_dir, "**", "*.log")
            for file_path in glob.glob(pattern, recursive=True):
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
            # Validate path to prevent directory traversal
            full_path = self._validate_safe_path(file_path)
            if os.path.exists(full_path):
                with open(full_path, 'w') as f:
                    f.write("")
                logger.info(f"Cleared log file: {file_path}")
            else:
                raise FileNotFoundError(f"Log file not found: {file_path}")
        except ValueError as e:
            logger.error(f"Invalid file path {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error clearing log file {file_path}: {e}")
            raise
    
    def rotate_log_file(self, file_path: str):
        """Rotate a specific log file."""
        try:
            # Validate path to prevent directory traversal
            full_path = self._validate_safe_path(file_path)
            if os.path.exists(full_path):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"{full_path}.{timestamp}"
                os.rename(full_path, backup_path)
                logger.info(f"Rotated log file: {file_path} -> {backup_path}")
            else:
                raise FileNotFoundError(f"Log file not found: {file_path}")
        except ValueError as e:
            logger.error(f"Invalid file path {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error rotating log file {file_path}: {e}")
            raise
    
    def is_llm_prompt_logging_enabled(self) -> bool:
        """Check if LLM prompt logging is enabled."""
        return self._config.get("llm_prompt_logging", {}).get("enabled", False)
    
    def get_llm_prompt_logging_level(self) -> str:
        """Get LLM prompt logging level."""
        return self._config.get("llm_prompt_logging", {}).get("level", "INFO")
    
    def get_llm_prompt_log_file(self) -> str:
        """Get LLM prompt log file path."""
        return self._config.get("llm_prompt_logging", {}).get("log_file", "llm_prompts.log")
    
    def log_llm_prompt(self, provider: str, model: str, prompt: str, response: str = None, 
                      metadata: Dict[str, Any] = None, timing: Dict[str, Any] = None, 
                      error: str = None, level: str = "INFO"):
        """Log LLM prompt based on configuration."""
        if not self.is_llm_prompt_logging_enabled():
            return
        
        config_level = self.get_llm_prompt_logging_level()
        level_hierarchy = ["ERROR", "WARN", "INFO", "DEBUG", "TRACE"]
        
        # Check if we should log this level (lower index = higher priority)
        if level_hierarchy.index(level) > level_hierarchy.index(config_level):
            return
        
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "provider": provider,
                "model": model,
                "level": level,
                "status": "error" if error else "success"
            }
            
            # Add prompt based on level
            if config_level in ["DEBUG", "TRACE"]:
                log_entry["prompt"] = prompt[:500] + "..." if len(prompt) > 500 else prompt
            else:
                log_entry["prompt_preview"] = prompt[:100] + "..." if len(prompt) > 100 else prompt
            
            # Add response based on level
            if config_level == "TRACE" and response:
                log_entry["response"] = response[:500] + "..." if len(response) > 500 else response
            elif config_level == "DEBUG" and response:
                log_entry["response_preview"] = response[:100] + "..." if len(response) > 100 else response
            
            # Add metadata if configured
            if self._config.get("llm_prompt_logging", {}).get("include_metadata", True) and metadata:
                log_entry["metadata"] = metadata
            
            # Add timing if configured
            if self._config.get("llm_prompt_logging", {}).get("include_timing", True) and timing:
                log_entry["timing"] = timing
            
            # Add error if present
            if error:
                log_entry["error"] = error
            
            # Write to log file
            log_file_path = os.path.join(self.logs_dir, self.get_llm_prompt_log_file())
            log_dir = os.path.dirname(log_file_path)
            if log_dir:  # Only create directory if there's a subdirectory
                os.makedirs(log_dir, exist_ok=True)
            else:
                os.makedirs(self.logs_dir, exist_ok=True)
            
            with open(log_file_path, 'a') as f:
                f.write(f"{json.dumps(log_entry)}\n")
                
        except Exception as e:
            logger.error(f"Error logging LLM prompt: {e}")
    
    def get_llm_prompt_logs(self, max_entries: int = 100) -> List[Dict[str, Any]]:
        """Get recent LLM prompt logs."""
        log_entries = []
        
        try:
            log_file_path = os.path.join(self.logs_dir, self.get_llm_prompt_log_file())
            if os.path.exists(log_file_path):
                with open(log_file_path, 'r') as f:
                    lines = f.readlines()
                    
                for line in lines[-max_entries:]:
                    try:
                        entry = json.loads(line.strip())
                        log_entries.append(entry)
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            logger.error(f"Error reading LLM prompt logs: {e}")
        
        return sorted(log_entries, key=lambda x: x.get("timestamp", ""), reverse=True)


# Global instance
logging_config_manager = LoggingConfigManager()