import json
import os
import logging
from logging.handlers import RotatingFileHandler

DEFAULT_CONFIG = {
    "backend": {
        "level": "INFO",
        "max_bytes": 1048576,
        "backup_count": 3
    }
}

class LoggingConfigManager:
    def __init__(self, config_file: str = "logging_config.json"):
        self.config_file = config_file
        self.config = self._load_config()
        self._ensure_log_dirs()
        self._handler: RotatingFileHandler | None = None
        self.apply_config()

    def _load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return DEFAULT_CONFIG.copy()

    def _ensure_log_dirs(self):
        os.makedirs(os.path.join("logs", "backend"), exist_ok=True)

    def save_config(self):
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)

    def get_config(self):
        return self.config.copy()

    def apply_config(self):
        level_name = self.config.get("backend", {}).get("level", "INFO").upper()
        level = getattr(logging, level_name, logging.INFO)
        root_logger = logging.getLogger()
        root_logger.setLevel(level)

        log_path = os.path.join("logs", "backend", "api.log")
        if not self._handler:
            self._handler = RotatingFileHandler(
                log_path,
                maxBytes=self.config["backend"].get("max_bytes", 1048576),
                backupCount=self.config["backend"].get("backup_count", 3),
            )
            formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            )
            self._handler.setFormatter(formatter)
            root_logger.addHandler(self._handler)
        else:
            self._handler.maxBytes = self.config["backend"].get("max_bytes", 1048576)
            self._handler.backupCount = self.config["backend"].get("backup_count", 3)

    def update_config(self, updates: dict):
        if "backend" in updates:
            self.config["backend"].update(updates["backend"])
        self.save_config()
        self.apply_config()
        return self.get_config()

    def get_recent_logs(self, lines: int = 100):
        log_path = os.path.join("logs", "backend", "api.log")
        if not os.path.exists(log_path):
            return []
        with open(log_path, "r") as f:
            return f.readlines()[-lines:]

    def clear_logs(self):
        log_path = os.path.join("logs", "backend", "api.log")
        open(log_path, "w").close()

logging_config_manager = LoggingConfigManager()
