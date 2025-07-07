#!/usr/bin/env python3
"""Test script to verify LLM logging functionality."""

import sys
import os
sys.path.append('backend')

from backend.logging_config import logging_config_manager

def test_llm_logging():
    """Test LLM logging functionality."""
    print("Testing LLM logging configuration...")
    
    # Check configuration
    print(f"LLM Prompt Logging Enabled: {logging_config_manager.is_llm_prompt_logging_enabled()}")
    print(f"LLM Prompt Logging Level: {logging_config_manager.get_llm_prompt_logging_level()}")
    print(f"LLM Prompt Log File: {logging_config_manager.get_llm_prompt_log_file()}")
    
    # Test logging a prompt
    print("\nTesting prompt logging...")
    try:
        logging_config_manager.log_llm_prompt(
            provider="test",
            model="test-model",
            prompt="What is the capital of France?",
            response="The capital of France is Paris.",
            metadata={"test": True, "subject": "Geography"},
            timing={"duration_ms": 500},
            level="INFO"
        )
        print("✓ Prompt logged successfully")
    except Exception as e:
        print(f"✗ Error logging prompt: {e}")
    
    # Check if log file was created
    log_file_path = os.path.join(logging_config_manager.logs_dir, logging_config_manager.get_llm_prompt_log_file())
    print(f"\nChecking log file: {log_file_path}")
    
    if os.path.exists(log_file_path):
        print("✓ Log file exists")
        with open(log_file_path, 'r') as f:
            content = f.read()
            print(f"Log file content:\n{content}")
    else:
        print("✗ Log file does not exist")
        
    # List recent logs
    print("\nRecent log entries:")
    logs = logging_config_manager.get_llm_prompt_logs(5)
    for log in logs:
        print(f"  - {log}")

if __name__ == "__main__":
    test_llm_logging()
