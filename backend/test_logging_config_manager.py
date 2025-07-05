import unittest
import os
import json
from backend.logging_config_manager import LoggingConfigManager

# Ensure tests run from the project root or adjust path accordingly
CONFIG_FILE_PATH = "test_logging_config.json"
DEFAULT_LOG_DIR = "logs_test" # Use a separate test log directory

class TestLoggingConfigManager(unittest.TestCase):

    def setUp(self):
        # Create a dummy config file for testing
        self.test_config_path = CONFIG_FILE_PATH
        self.default_config = {
            "global_level": "INFO",
            "frontend_level": "INFO",
            "backend_levels": {
                "api_server": "INFO",
                "llm_providers": "INFO",
                "database": "WARNING"
            },
            "log_files": {
                "frontend_app": f"{DEFAULT_LOG_DIR}/frontend/app.log",
                "backend_api": f"{DEFAULT_LOG_DIR}/backend/api.log",
                "combined": f"{DEFAULT_LOG_DIR}/combined.log"
            },
            "log_rotation_max_bytes": 10000,
            "log_rotation_backup_count": 3,
            "enable_file_logging": True
        }
        with open(self.test_config_path, 'w') as f:
            json.dump(self.default_config, f, indent=2)

        # Instantiate the manager with the test config file
        # Adjust path if tests are run from backend directory
        if os.path.basename(os.getcwd()) == 'backend':
            self.manager = LoggingConfigManager(config_file=f"../{self.test_config_path}")
        else:
            self.manager = LoggingConfigManager(config_file=self.test_config_path)


    def tearDown(self):
        # Clean up the dummy config file
        if os.path.exists(self.test_config_path):
            os.remove(self.test_config_path)
        # Clean up dummy log directory if created by other tests
        # For now, this test suite only focuses on config manager, not log file creation

    def test_load_config(self):
        config = self.manager.get_config()
        self.assertIsNotNone(config)
        self.assertEqual(config["global_level"], "INFO")
        self.assertEqual(config["log_rotation_max_bytes"], 10000)
        self.assertTrue(config["enable_file_logging"])
        self.assertIn("backend_api", config["log_files"])

    def test_update_config(self):
        updates = {
            "global_level": "DEBUG",
            "log_rotation_max_bytes": 20000,
            "backend_levels": {
                "api_server": "DEBUG"
            }
        }
        self.manager.update_config(updates)
        updated_config = self.manager.get_config()

        self.assertEqual(updated_config["global_level"], "DEBUG")
        self.assertEqual(updated_config["log_rotation_max_bytes"], 20000)
        self.assertEqual(updated_config["backend_levels"]["api_server"], "DEBUG")
        # Ensure other backend levels are not wiped out if not in partial update
        self.assertEqual(updated_config["backend_levels"]["llm_providers"], "INFO")

    def test_update_nested_config(self):
        updates = {
            "backend_levels": {
                "database": "ERROR"
            }
        }
        self.manager.update_config(updates)
        updated_config = self.manager.get_config()
        self.assertEqual(updated_config["backend_levels"]["database"], "ERROR")
        self.assertEqual(updated_config["backend_levels"]["api_server"], "INFO") # Should remain unchanged

    def test_save_config(self):
        updates = {"global_level": "WARNING"}
        self.manager.update_config(updates) # This calls save_config()

        # Create a new manager instance to force re-load from file
        if os.path.basename(os.getcwd()) == 'backend':
            new_manager = LoggingConfigManager(config_file=f"../{self.test_config_path}")
        else:
            new_manager = LoggingConfigManager(config_file=self.test_config_path)

        reloaded_config = new_manager.get_config()
        self.assertEqual(reloaded_config["global_level"], "WARNING")

    def test_get_default_config_if_file_missing(self):
        if os.path.exists(self.test_config_path):
            os.remove(self.test_config_path)

        # Instantiate manager - it should create a default config file
        if os.path.basename(os.getcwd()) == 'backend':
            temp_manager = LoggingConfigManager(config_file=f"../{self.test_config_path}")
        else:
            temp_manager = LoggingConfigManager(config_file=self.test_config_path)

        config = temp_manager.get_config()
        self.assertIsNotNone(config)
        # Check a few default values from _get_default_config in LoggingConfigManager
        self.assertEqual(config["global_level"], "INFO")
        self.assertEqual(config["log_rotation_max_bytes"], 10485760) # Default from class
        self.assertTrue(os.path.exists(self.test_config_path)) # Check if file was created

if __name__ == '__main__':
    unittest.main()
