#!/usr/bin/env python3
"""Test script to verify LLM logging functionality."""

import sys
import os
import json
import unittest
from unittest.mock import patch, MagicMock

# Add project root to path and change working directory to project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.chdir(project_root)

from backend.logging_config import logging_config_manager


class TestLLMLogging(unittest.TestCase):
    """Test cases for LLM logging functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Ensure we're in the correct directory
        if not os.path.exists('logging_config.json'):
            os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Force reload of configuration to ensure we get the latest config
        logging_config_manager._load_config()
        
        # Override the configuration to ensure LLM logging is enabled for tests
        test_config = logging_config_manager.get_config()
        test_config['llm_prompt_logging'] = {
            'enabled': True,
            'level': 'DEBUG',
            'log_file': 'backend/llm_prompts.log',
            'include_metadata': True,
            'include_timing': True,
            'include_full_response': True
        }
        logging_config_manager._config = test_config
        
        self.test_log_file = os.path.join(
            logging_config_manager.logs_dir, 
            logging_config_manager.get_llm_prompt_log_file()
        )
        
        # Ensure test log file doesn't exist at start
        if os.path.exists(self.test_log_file):
            os.remove(self.test_log_file)

    def tearDown(self):
        """Clean up after tests."""
        # Remove test log file
        if os.path.exists(self.test_log_file):
            os.remove(self.test_log_file)

    def test_llm_logging_configuration(self):
        """Test that LLM logging is properly configured."""
        self.assertTrue(
            logging_config_manager.is_llm_prompt_logging_enabled(),
            "LLM prompt logging should be enabled"
        )
        
        level = logging_config_manager.get_llm_prompt_logging_level()
        self.assertIn(level, ["DEBUG", "INFO", "WARN", "ERROR", "TRACE"])
        
        log_file = logging_config_manager.get_llm_prompt_log_file()
        self.assertTrue(log_file.endswith('.log'))

    def test_log_llm_prompt_basic(self):
        """Test basic LLM prompt logging functionality."""
        # Log a test prompt
        logging_config_manager.log_llm_prompt(
            provider="test_provider",
            model="test_model",
            prompt="What is 2+2?",
            response="4",
            metadata={"test": True, "subject": "Math"},
            timing={"duration_ms": 100},
            level="INFO"
        )
        
        # Check if log file was created
        self.assertTrue(os.path.exists(self.test_log_file), "Log file should be created")
        
        # Read and verify log content
        with open(self.test_log_file, 'r') as f:
            content = f.read().strip()
            self.assertTrue(content, "Log file should not be empty")
            
            # Parse JSON log entry
            log_entry = json.loads(content)
            self.assertEqual(log_entry["provider"], "test_provider")
            self.assertEqual(log_entry["model"], "test_model")
            self.assertEqual(log_entry["prompt"], "What is 2+2?")
            self.assertEqual(log_entry["status"], "success")
            self.assertIn("timestamp", log_entry)
            self.assertIn("metadata", log_entry)
            self.assertIn("timing", log_entry)

    def test_log_llm_prompt_with_error(self):
        """Test LLM prompt logging with error."""
        logging_config_manager.log_llm_prompt(
            provider="test_provider",
            model="test_model",
            prompt="Invalid prompt",
            error="API Error: Invalid request",
            metadata={"test": True},
            timing={"duration_ms": 50},
            level="ERROR"
        )
        
        # Check log content
        with open(self.test_log_file, 'r') as f:
            log_entry = json.loads(f.read().strip())
            self.assertEqual(log_entry["status"], "error")
            self.assertEqual(log_entry["error"], "API Error: Invalid request")
            self.assertEqual(log_entry["level"], "ERROR")

    def test_log_llm_prompt_level_filtering(self):
        """Test that log level filtering works correctly."""
        # Set logging level to ERROR only
        original_config = logging_config_manager.get_config()
        logging_config_manager.update_config({
            "llm_prompt_logging": {
                "enabled": True,
                "level": "ERROR"
            }
        })
        
        try:
            # Try to log INFO level (should be filtered out)
            logging_config_manager.log_llm_prompt(
                provider="test",
                model="test",
                prompt="Info prompt",
                level="INFO"
            )
            
            # File should not be created or should be empty
            if os.path.exists(self.test_log_file):
                with open(self.test_log_file, 'r') as f:
                    content = f.read().strip()
                    self.assertEqual(content, "", "INFO level should be filtered out")
            
            # Log ERROR level (should be logged)
            logging_config_manager.log_llm_prompt(
                provider="test",
                model="test",
                prompt="Error prompt",
                error="Test error",
                level="ERROR"
            )
            
            # File should now contain the ERROR entry
            self.assertTrue(os.path.exists(self.test_log_file))
            with open(self.test_log_file, 'r') as f:
                content = f.read().strip()
                self.assertTrue(content, "ERROR level should be logged")
                log_entry = json.loads(content)
                self.assertEqual(log_entry["level"], "ERROR")
                
        finally:
            # Restore original config
            logging_config_manager._config = original_config
            logging_config_manager.save_config()

    def test_get_llm_prompt_logs(self):
        """Test retrieving LLM prompt logs."""
        # Log multiple entries
        test_entries = [
            {"provider": "test1", "model": "model1", "prompt": "prompt1"},
            {"provider": "test2", "model": "model2", "prompt": "prompt2"},
            {"provider": "test3", "model": "model3", "prompt": "prompt3"}
        ]
        
        for entry in test_entries:
            logging_config_manager.log_llm_prompt(
                provider=entry["provider"],
                model=entry["model"],
                prompt=entry["prompt"],
                level="INFO"
            )
        
        # Retrieve logs
        logs = logging_config_manager.get_llm_prompt_logs(max_entries=5)
        
        self.assertEqual(len(logs), 3, "Should retrieve 3 log entries")
        
        # Check that entries are in reverse chronological order
        for i, log in enumerate(logs):
            self.assertEqual(log["provider"], test_entries[-(i+1)]["provider"])

    def test_logging_when_disabled(self):
        """Test that nothing is logged when LLM logging is disabled."""
        # Disable logging
        original_config = logging_config_manager.get_config()
        logging_config_manager.update_config({
            "llm_prompt_logging": {
                "enabled": False
            }
        })
        
        try:
            # Try to log
            logging_config_manager.log_llm_prompt(
                provider="test",
                model="test",
                prompt="Should not be logged",
                level="INFO"
            )
            
            # File should not be created
            self.assertFalse(
                os.path.exists(self.test_log_file),
                "Log file should not be created when logging is disabled"
            )
            
        finally:
            # Restore original config
            logging_config_manager._config = original_config
            logging_config_manager.save_config()


def run_llm_logging_tests():
    """Run LLM logging tests and return results."""
    print("=" * 60)
    print("Running LLM Logging Tests")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLLMLogging)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\nTests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nLLM Logging Tests: {'PASSED' if success else 'FAILED'}")
    return success


if __name__ == "__main__":
    success = run_llm_logging_tests()
    sys.exit(0 if success else 1)
