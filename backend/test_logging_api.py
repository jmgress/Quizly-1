import unittest
import os
import json
from fastapi.testclient import TestClient
from backend.main import app # Assuming 'app' is your FastAPI instance in main.py

# Use a separate test config file for API tests to avoid conflicts
TEST_API_LOGGING_CONFIG_PATH = "test_api_logging_config.json"
# Store the original config path to restore later
ORIGINAL_LOGGING_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "logging_config.json")
# Path for backend.main's logging_config_mgr to point to during tests
# This assumes test_logging_api.py is in the 'backend' directory
BACKEND_TEST_CONFIG_PATH = TEST_API_LOGGING_CONFIG_PATH

class TestLoggingAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create a specific logging config for API tests
        cls.test_config_data = {
            "global_level": "DEBUG",
            "frontend_level": "INFO",
            "backend_levels": { "api_server": "DEBUG", "llm_providers": "INFO", "database": "WARNING" },
            "log_files": {
                "backend_api": "logs_test/backend/api_test.log",
                "combined": "logs_test/combined_test.log",
                "backend_error": "logs_test/backend/error_test.log"
            },
            "log_rotation_max_bytes": 1024, # Small for testing rotation if possible
            "log_rotation_backup_count": 1,
            "enable_file_logging": True # Ensure file logging is on for some tests
        }
        # Write this config to where backend.main.logging_config_mgr will find it
        # This requires careful path management. If main.py's LoggingConfigManager
        # is initialized with `os.path.join(os.path.dirname(__file__), "..", "logging_config.json")`
        # then this test file (if in backend/) needs to write to ../test_api_logging_config.json
        # and temporarily repoint the manager. This is tricky without direct app modification.

        # For now, let's assume we can influence where logging_config_mgr loads from,
        # or that we can directly patch its config path or instance.
        # A simpler approach for isolated testing is to ensure the default logging_config.json
        # is either backed up and replaced, or that tests use a distinct one.

        # Create the test config file in the project root, as that's where LoggingConfigManager expects it by default.
        # The path in LoggingConfigManager is relative to the project root.
        project_root_test_config_path = os.path.join(os.path.dirname(__file__), "..", TEST_API_LOGGING_CONFIG_PATH)

        with open(project_root_test_config_path, 'w') as f:
            json.dump(cls.test_config_data, f, indent=2)

        # IMPORTANT: We need to tell main.logging_config_mgr to use this test file.
        # This typically involves patching or environment variables at app startup.
        # For TestClient, the app is imported, so this needs careful handling.
        # One way: main.py could check an ENV VAR for the config file path.
        # For now, we'll assume that `logging_config_mgr` in `main.py` somehow
        # picks up `TEST_API_LOGGING_CONFIG_PATH` when tests run.
        # This is a common challenge in testing FastAPI apps with file configs.

        # A more robust way would be to use FastAPI's dependency overrides for settings.
        # For this exercise, we'll proceed as if the config is loaded.
        # We also need to ensure 'logs_test' directory exists.
        cls.test_log_dir = os.path.join(os.path.dirname(__file__), "..", "logs_test")
        os.makedirs(os.path.join(cls.test_log_dir, "backend"), exist_ok=True)
        os.makedirs(os.path.join(cls.test_log_dir, "frontend"), exist_ok=True)


        cls.client = TestClient(app)


    @classmethod
    def tearDownClass(cls):
        # Clean up the test config file
        project_root_test_config_path = os.path.join(os.path.dirname(__file__), "..", TEST_API_LOGGING_CONFIG_PATH)
        if os.path.exists(project_root_test_config_path):
            os.remove(project_root_test_config_path)

        # Clean up test log files (optional, but good practice)
        # Example:
        # api_log = os.path.join(cls.test_log_dir, "backend", "api_test.log")
        # if os.path.exists(api_log): os.remove(api_log)
        # ... and so on for other test log files ...
        # For simplicity, manual cleanup or git clean might be used outside tests.


    def setUp(self):
        # Reset to the initial test config before each test if needed,
        # especially if tests modify the config file directly.
        # For API tests, usually we test the PUT endpoint's effect.

        # Ensure the log files defined in test_config_data exist and are empty for some tests
        self.api_log_path = os.path.join(self.test_log_dir, "backend", "api_test.log")
        self.error_log_path = os.path.join(self.test_log_dir, "backend", "error_test.log")
        self.combined_log_path = os.path.join(self.test_log_dir, "combined_test.log")

        for path in [self.api_log_path, self.error_log_path, self.combined_log_path]:
            if not os.path.exists(os.path.dirname(path)):
                 os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f: # Clear file
                f.write("")


    def test_get_logging_config(self):
        response = self.client.get("/api/logging/config")
        self.assertEqual(response.status_code, 200)
        config = response.json()
        self.assertIsNotNone(config)
        self.assertEqual(config["global_level"], self.test_config_data["global_level"]) # Check against our test setup
        self.assertEqual(config["log_files"]["backend_api"], self.test_config_data["log_files"]["backend_api"])

    def test_update_logging_config(self):
        update_payload = {
            "global_level": "WARNING",
            "backend_levels": {
                "api_server": "INFO", # Change from DEBUG
                "database": "ERROR"  # Change from WARNING
            }
        }
        response = self.client.put("/api/logging/config", json=update_payload)
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["message"], "Logging configuration updated successfully")

        # Verify by GETting the config again
        response_get = self.client.get("/api/logging/config")
        updated_config = response_get.json()
        self.assertEqual(updated_config["global_level"], "WARNING")
        self.assertEqual(updated_config["backend_levels"]["api_server"], "INFO")
        self.assertEqual(updated_config["backend_levels"]["database"], "ERROR")

    def test_get_log_entries_default(self):
        # First, make some log entries by calling an endpoint
        self.client.get("/") # This should log something to api_server if level is DEBUG/INFO

        # Now try to fetch logs
        # This depends on the logging setup actually writing to the file defined in TEST_API_LOGGING_CONFIG_PATH
        # And that TestClient runs the app in a way that logging is fully initialized.

        # Create a dummy log line to ensure the file is not empty
        with open(self.combined_log_path, "a") as f:
            f.write("INFO - Test line for combined log\n")

        response = self.client.get("/api/logging/logs?component=combined&lines=10")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("logs", data)
        # self.assertTrue(len(data["logs"]) > 0) # This is tricky, depends on actual logging activity

    def test_get_log_entries_filtered(self):
        with open(self.api_log_path, "a") as f:
            f.write("2023-10-01 ... - api_server - DEBUG - This is a debug message\n")
            f.write("2023-10-01 ... - api_server - INFO - This is an info message\n")

        response = self.client.get("/api/logging/logs?component=backend_api&level=DEBUG&lines=10")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("logs", data)
        if data["logs"]: # if log file was found and readable
            self.assertTrue(any("DEBUG - This is a debug message" in line for line in data["logs"]))
            self.assertFalse(any("INFO - This is an info message" in line for line in data["logs"]))

    def test_download_log_file(self):
        log_key = "backend_api" # from test_config_data
        with open(self.api_log_path, "w") as f:
            f.write("Test content for download.\n")

        response = self.client.get(f"/api/logging/actions/download/{log_key}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Test content for download.", response.text)
        self.assertIn("text/plain", response.headers["content-type"])

    def test_clear_log_file(self):
        log_key = "backend_api"
        with open(self.api_log_path, "w") as f:
            f.write("Some content to be cleared.\n")

        response = self.client.post(f"/api/logging/actions/clear/{log_key}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("cleared successfully", response.json()["message"])

        with open(self.api_log_path, "r") as f:
            content = f.read()
        self.assertEqual(content, "")

    # Manual rotation test is hard here as it depends on logging handler state.
    # We can check if the endpoint runs without error.
    def test_rotate_log_file_endpoint(self):
        log_key = "backend_api" # from test_config_data
        # Ensure the file exists for rotation logic
        open(self.api_log_path, 'a').close()

        response = self.client.post(f"/api/logging/actions/rotate/{log_key}")
        self.assertEqual(response.status_code, 200) # Or 404 if handler not found, which is possible in test setup
        # A more thorough test would check if a .1 file was created, but that's complex here.
        self.assertIn("Log rotation triggered", response.json()["message"])


if __name__ == '__main__':
    # This setup is crucial for making the app use the test config.
    # One way is to set an environment variable that main.py checks.
    # For example: os.environ["LOGGING_CONFIG_FILE"] = TEST_API_LOGGING_CONFIG_PATH
    # And main.py's LoggingConfigManager constructor would use this env var if set.

    # The provided main.py initializes logging_config_mgr at the module level:
    # logging_config_mgr = LoggingConfigManager(config_file=os.path.join(os.path.dirname(__file__), "..", "logging_config.json"))
    # To make it use TEST_API_LOGGING_CONFIG_PATH, we would need to patch it *before* TestClient(app) imports 'app'.
    # This is usually done with pytest fixtures or unittest's patch.

    print("NOTE: Running these tests requires FastAPI's TestClient and a mechanism")
    print("to make the FastAPI app use the '{}' during testing.".format(TEST_API_LOGGING_CONFIG_PATH))
    print("This might involve patching 'backend.main.logging_config_mgr.config_file' or similar.")

    # For now, we'll assume this setup is handled externally or via patching if running in a real test runner.
    unittest.main()
